import hashlib
import logging
import os
from typing import Type

from fastapi import UploadFile

from app.models.files import FileBaseModel

UPLOAD_DIR = "static/"

log = logging.getLogger("uvicorn")


async def create_file(file: UploadFile, cls: Type[FileBaseModel]) -> int:
    data = await file.read()

    hash = hashlib.sha1(data).hexdigest()
    ext = os.path.splitext(file.filename)[-1]
    save_path = os.path.join(UPLOAD_DIR, cls.SAVE_PATH, hash + ext)

    try:
        with open(save_path, "wb") as f:
            f.write(data)

        file_record = await cls.create(name=file.filename, path=save_path, media_type=file.content_type)
        return file_record.id

    except Exception as e:
        log.error(f"Error while creating file {file.filename}: {e}")
        os.remove(save_path)
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
