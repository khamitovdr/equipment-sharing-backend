from tortoise.contrib.pydantic import pydantic_model_creator

from app.schemas import _init_models
from app.models.equipment import Equipment


EquipmentCreateSchema = pydantic_model_creator(Equipment, name="EquipmentCreate", exclude_readonly=True)
# EquipmentSchema = pydantic_model_creator(Equipment, name="Equipment", exclude=["id", "organization"])
