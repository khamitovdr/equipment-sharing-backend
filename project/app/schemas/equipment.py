from dataclasses import dataclass
from typing import Optional, Annotated

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from fastapi import UploadFile
from fastapi.params import File, Form


from app.schemas import _init_models
from app.models.equipment import TimeInterval
# from app.models.equipment import Equipment


class EquipmentCategorySchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class EquipmentMediaSchema(BaseModel):
    path: str
    media_type: str

    class Config:
        orm_mode = True


class EquipmentDocumentSchema(BaseModel):
    path: str

    class Config:
        orm_mode = True


class EquipmentSchema(BaseModel):
    name: str
    description: Optional[str]
    description_of_configuration: Optional[str]
    with_operator: bool
    price: float
    time_interval: TimeInterval
    year_of_release: int
    category: EquipmentCategorySchema
    # documents: list[EquipmentDocumentSchema]
    # photo_and_video: list[EquipmentMediaSchema]

    class Config:
        orm_mode = True
        

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
