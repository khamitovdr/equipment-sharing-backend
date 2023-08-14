import hashlib
import io
import logging
import os
from typing import Type

from fastapi import UploadFile
from PIL import Image

from app.models.files import FileBaseModel

UPLOAD_DIR = "static/"

log = logging.getLogger("uvicorn")


async def create_file(file: UploadFile, cls: Type[FileBaseModel]) -> FileBaseModel:
    data = await file.read()

    media_type, media_format = file.content_type.split("/")
    hash = hashlib.sha1(data).hexdigest()
    ext = os.path.splitext(file.filename)[-1].strip(".")

    def get_save_path(suffix: str = "", ext: str = ext) -> str:
        return os.path.join(UPLOAD_DIR, cls.SAVE_PATH, f"{hash}{'_' if suffix else ''}{suffix}.{ext}")

    path = {
        "original": get_save_path("original"),
    }

    try:
        if media_type == "image":
            image = Image.open(io.BytesIO(data)).convert("RGB")

            image_large = image.copy()
            image_medium = image.copy()
            image_small = image.copy()
            image.thumbnail((1920, 1080))
            image_large.thumbnail((1024, 1024))
            image_medium.thumbnail((512, 512))
            image_small.thumbnail((128, 128))

            path.update(
                {
                    "webp": get_save_path("original", ext="webp"),
                    "large": get_save_path("large", ext="webp"),
                    "medium": get_save_path("medium", ext="webp"),
                    "small": get_save_path("small", ext="webp"),
                }
            )

            image.save(path["original"], quality=100)
            image.save(path["webp"], quality=100)
            image_large.save(path["large"], quality=100)
            image_medium.save(path["medium"], quality=100)
            image_small.save(path["small"], quality=100)

        elif media_type in ["video", "application"]:
            with open(path["original"], "wb") as f:
                f.write(data)

        else:
            raise TypeError(f"Unsupported media type: {media_type}")

        file_record = await cls.create(
            name=file.filename,
            media_type=media_type,
            media_format=media_format,
            hash=hash,
            original_path=path["original"],
            path=path,
        )
        return file_record

    except Exception as e:
        log.error(f"Error while creating file {file.filename}: {e}")
        for path_ in path.values():
            if os.path.exists(path_):
                os.remove(path_)
        raise e


async def delete_file(file_id: int, cls: Type[FileBaseModel]) -> int:
    file_record = await cls.get_or_none(id=file_id)
    if file_record is None:
        raise ValueError(f"File {file_id} not found")

    try:
        await file_record.delete()
        return file_id
    except Exception as e:
        log.error(f"Error while deleting file {file_id}: {e}")
        raise e
