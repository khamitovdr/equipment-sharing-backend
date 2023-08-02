import logging
import os
from asyncio import sleep
from typing import Optional, Type

from tortoise import BaseDBAsyncClient
from tortoise.signals import post_delete, post_save, pre_delete

from app.crud.files import delete_file
from app.models.files import FileBaseModel

log = logging.getLogger("uvicorn")


# async def delete_file_if_unused(file: FileBaseModel, waiting_time_seconds: int) -> None:
#     """Delete file if it is not used in any equipment"""
#     await sleep(waiting_time_seconds)
#     await file.refresh_from_db()
#     if await file.host is None:
#         log.info(f"Deleting unused file {file.name}")
#         await delete_file(file.id, type(file))


# @post_save(*FileBaseModel.__subclasses__())
# async def file_post_save(
#     sender: Type[FileBaseModel],
#     file: FileBaseModel,
#     created: bool,
#     using_db: Optional[BaseDBAsyncClient],
#     update_fields: list[str],
# ) -> None:
#     """Delete file if it is not used in any equipment"""
#     if created:
#         log.info(f"Waiting for file {file.name} to be used in created equipment")
#         await delete_file_if_unused(file, 10)


# on_delete=CASCADE doesn't fire pre_delete and post_delete signals
# https://github.com/tortoise/tortoise-orm/issues/1447
@pre_delete(*FileBaseModel.__subclasses__())
async def file_pre_delete(
    sender: Type[FileBaseModel],
    file: FileBaseModel,
    using_db: Optional[BaseDBAsyncClient],
) -> None:
    log.info(f"post_delete signal for file {file}")
    try:
        if await sender.filter(path=file.path).count() == 1:
            log.info(f"Deleting file {file.path}")
            os.remove(file.path)
    except Exception as e:
        log.error(f"Error while deleting file {file.path}: {e}")
        raise e
