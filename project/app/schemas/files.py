from tortoise.contrib.pydantic import pydantic_model_creator

from app import _init_models  # noqa: F401
from app.models.files import FileBaseModel, UploadedMediaBaseModel

FileBaseSchema = pydantic_model_creator(FileBaseModel, name="FileBaseSchema")
MediaBaseSchema = pydantic_model_creator(UploadedMediaBaseModel, name="MediaBaseSchema")
