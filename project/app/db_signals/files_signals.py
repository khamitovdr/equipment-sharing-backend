import logging
import os
from asyncio import sleep
from typing import Optional, Type

from tortoise import BaseDBAsyncClient
from tortoise.signals import post_save, pre_delete

from app.models.files import UploadedFileBaseModel, UploadedMediaBaseModel
from app.scheduler import app as scheduler

log = logging.getLogger("uvicorn")

session = scheduler.session

UPLOADED_MEDIA_WAITING_TIME_MINUTES = 20


@scheduler.task()
async def delete_file_if_unused(file: UploadedFileBaseModel, waiting_time_seconds: int) -> None:
    """Delete file if it is not used in any equipment"""
    await sleep(waiting_time_seconds)
    await file.refresh_from_db()
    if await file.host is None:
        log.info(f"Deleting unused file {file.name}")
        await file.delete()


@post_save(*UploadedFileBaseModel.__subclasses__())
async def file_post_save(
    sender: Type[UploadedFileBaseModel],
    file: UploadedFileBaseModel,
    created: bool,
    using_db: Optional[BaseDBAsyncClient],
    update_fields: list[str],
) -> None:
    """Delete file if it is not used in any equipment"""
    if created:
        log.info(f"Waiting for file {file.name} to be used in created equipment")
        task = session[delete_file_if_unused]
        task.run(file=file, waiting_time_seconds=UPLOADED_MEDIA_WAITING_TIME_MINUTES * 60)


# TODO: Накинуть pre_delete на все модели, которые могут содержать ссылки на файлы
@pre_delete(*UploadedFileBaseModel.__subclasses__())
async def file_pre_delete(
    sender: Type[UploadedFileBaseModel],
    file: UploadedFileBaseModel,
    using_db: Optional[BaseDBAsyncClient],
) -> None:
    if await sender.filter(path=file.path).count() == 1:
        log.info(f"Deleting file {file.path}")
        if os.path.exists(file.path):
            os.remove(file.path)
        else:
            log.warning(f"File {file.path} doesn't exist")


@pre_delete(*UploadedMediaBaseModel.__subclasses__())
async def image_pre_delete(
    sender: Type[UploadedMediaBaseModel],
    file: UploadedMediaBaseModel,
    using_db: Optional[BaseDBAsyncClient],
) -> None:
    if file.media_type != "image":
        return await file_pre_delete(sender, file, using_db)

    if await sender.filter(path=file.path).count() == 1:
        log.info(f"Deleting photos derived from {file.path}")
        for path in (file.path, *file.derived_path.values()):
            if os.path.exists(path):
                os.remove(path)
            else:
                log.warning(f"File {path} doesn't exist")
