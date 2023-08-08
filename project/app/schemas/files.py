from tortoise.contrib.pydantic import pydantic_model_creator

from app import _init_models  # noqa: F401
from app.models.files import FileBaseModel


FileBaseSchema = pydantic_model_creator(FileBaseModel, name="FileBaseSchema")
