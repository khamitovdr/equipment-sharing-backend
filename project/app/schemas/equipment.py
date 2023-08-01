from dataclasses import dataclass
from typing import Optional

from fastapi import UploadFile
from fastapi.params import File, Form
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app import _init_models  # noqa: F401
from app.models.equipment import (
    Equipment,
    EquipmentCategory,
    EquipmentCategoryWithEquipmentCount,
    TimeInterval,
)


@dataclass
class EquipmentCreateForm:
    name: str = Form(...)
    description: Optional[str] = Form(None)
    description_of_configuration: Optional[str] = Form(None)
    with_operator: bool = Form(False)
    price: float = Form(...)
    time_interval: TimeInterval = Form(TimeInterval.DAY)
    category_id: int = Form(...)
    year_of_release: int = Form(1900)

    documents: Optional[list[UploadFile]] = File([])
    photo_and_video: Optional[list[UploadFile]] = File([])


EquipmentCategorySchema = pydantic_model_creator(EquipmentCategory, name="EquipmentCategorySchema")
EquipmentCategoryListSchema = pydantic_queryset_creator(EquipmentCategoryWithEquipmentCount)


class EquipmentPydanticMeta:
    exclude = [
        "orders",
        "notifications",
    ]


EquipmentSchema = pydantic_model_creator(Equipment, name="EquipmentSchema", meta_override=EquipmentPydanticMeta)
EquipmentListSchema = pydantic_queryset_creator(Equipment)
