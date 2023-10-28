import hashlib
import io
import logging
import os
from typing import Type

from fastapi import UploadFile, HTTPException, status
from PIL import Image

from app.config import get_settings
from app.models.files import FileBaseModel, UploadedFileBaseModel, UploadedMediaBaseModel

UPLOAD_DIR = get_settings().static_dir

log = logging.getLogger("uvicorn")


async def create_uploaded_file(
        file: UploadFile,
        cls: Type[UploadedFileBaseModel],
        allowed_types: list[str] = None,
        allowed_formats: list[str] = None,
    ) -> UploadedFileBaseModel:
    data = await file.read()

    media_type, media_format = file.content_type.split("/")
    if allowed_types and media_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported media type: {media_type}! Allowed types: {allowed_types}",
        )
    
    if allowed_formats and media_format not in allowed_formats:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported media format: {media_format}! Allowed formats: {allowed_formats}",
        )
    
    hash = hashlib.sha1(data).hexdigest()
    ext = os.path.splitext(file.filename)[-1].strip(".")

    def get_save_path(suffix: str = "", ext: str = ext) -> str:
        return os.path.join(UPLOAD_DIR, cls.SAVE_PATH, f"{hash}{'_' if suffix else ''}{suffix}.{ext}")

    path = {
        "original": get_save_path("original"),
    }

    file_record = await cls(
            name=file.filename,
            media_type=media_type,
            media_format=media_format,
            hash=hash,
            path=get_save_path(),
        )

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

            file_record.derived_path = {
                "webp": get_save_path(ext="webp"),
                "large": get_save_path("large", ext="webp"),
                "medium": get_save_path("medium", ext="webp"),
                "small": get_save_path("small", ext="webp"),
            }

            image.save(file_record.path, quality=100)
            image.save(file_record.derived_path["webp"], quality=100)
            image_large.save(file_record.derived_path["large"], quality=100)
            image_medium.save(file_record.derived_path["medium"], quality=100)
            image_small.save(file_record.derived_path["small"], quality=100)

        elif media_type in ["video", "application", "text"]:
            with open(file_record.path, "wb") as f:
                f.write(data)

        else:
            raise TypeError(f"Unsupported media type: {media_type}")

        await file_record.save()
        return file_record

    except Exception as e:
        log.error(f"Error while creating file {file.filename}: {e}")
        if os.path.exists(file_record.path): os.remove(file_record.path)

        if cls == UploadedMediaBaseModel and file_record.derived_path:
            for path in file_record.derived_path.values():
                if os.path.exists(path): os.remove(path)
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
