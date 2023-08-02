from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app import _init_models  # noqa: F401
from app.models.equipment import (
    Equipment,
    EquipmentCategory,
    EquipmentCategoryWithEquipmentCount,
    TimeInterval,
)


class EquipmentCreateSchema(BaseModel):
    name: str
    description: str = None
    description_of_configuration: str = None
    with_operator: bool = False
    price: float
    time_interval: TimeInterval = TimeInterval.DAY
    category_id: int
    year_of_release: int = 1900

    documents_ids: list[int] = []
    photo_and_video_ids: list[int] = []


class EquipmentUpdateSchema(EquipmentCreateSchema):
    name: str = None
    price: float = None
    time_interval: TimeInterval = None
    category_id: int = None
    year_of_release: int = None


EquipmentCategorySchema = pydantic_model_creator(EquipmentCategory, name="EquipmentCategorySchema")
EquipmentCategoryListSchema = pydantic_queryset_creator(EquipmentCategoryWithEquipmentCount)


class EquipmentPydanticMeta:
    exclude = [
        "orders",
        "notifications",
    ]


EquipmentSchema = pydantic_model_creator(Equipment, name="EquipmentSchema", meta_override=EquipmentPydanticMeta)
EquipmentListSchema = pydantic_queryset_creator(Equipment)
