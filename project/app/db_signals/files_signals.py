import logging
import os
from asyncio import sleep
from typing import Optional, Type

from tortoise import BaseDBAsyncClient
from tortoise.signals import post_save, pre_delete

from app.models.files import FileBaseModel
from app.scheduler import app as scheduler

log = logging.getLogger("uvicorn")

session = scheduler.session

UPLOADED_MEDIA_WAITING_TIME_MINUTES = 20


@scheduler.task()
async def delete_file_if_unused(file: FileBaseModel, waiting_time_seconds: int) -> None:
    """Delete file if it is not used in any equipment"""
    await sleep(waiting_time_seconds)
    await file.refresh_from_db()
    if await file.host is None:
        log.info(f"Deleting unused file {file.name}")
        await file.delete()


@post_save(*FileBaseModel.__subclasses__())
async def file_post_save(
    sender: Type[FileBaseModel],
    file: FileBaseModel,
    created: bool,
    using_db: Optional[BaseDBAsyncClient],
    update_fields: list[str],
) -> None:
    """Delete file if it is not used in any equipment"""
    if created:
        log.info(f"Waiting for file {file.name} to be used in created equipment")
        task = session[delete_file_if_unused]
        task.run(file=file, waiting_time_seconds=UPLOADED_MEDIA_WAITING_TIME_MINUTES * 60)


# on_delete=CASCADE doesn't fire pre_delete and post_delete signals
# https://github.com/tortoise/tortoise-orm/issues/1447
@pre_delete(*FileBaseModel.__subclasses__())
async def file_pre_delete(
    sender: Type[FileBaseModel],
    file: FileBaseModel,
    using_db: Optional[BaseDBAsyncClient],
) -> None:
    try:
        if await sender.filter(path=file.path).count() == 1:
            log.info(f"Deleting file {file.path}")
            os.remove(file.path)
    except Exception as e:
        log.error(f"Error while deleting file {file.path}: {e}")
        raise e
