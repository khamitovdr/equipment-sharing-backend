from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel
from fastapi import UploadFile
from fastapi.params import File, Form
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app.models.equipment import Equipment, EquipmentCategory, TimeInterval
from app.schemas import _init_models


EquipmentCategorySchema = pydantic_model_creator(EquipmentCategory, name="EquipmentCategorySchema")
# EquipmentCategoryListSchema = pydantic_queryset_creator(EquipmentCategory)

class EquipmentCategoryListSchema(BaseModel):
    id: int
    name: str
    verified: bool
    equipment_count: int

    class Config:
        orm_mode = True


EquipmentSchema = pydantic_model_creator(Equipment, name="EquipmentSchema")
EquipmentListSchema = pydantic_queryset_creator(Equipment, exclude=("added_by", "added_by_id", "documents", "description_of_configuration", "year_of_release"))


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
