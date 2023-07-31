from datetime import date

from pydantic import BaseModel

from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app.schemas import _init_models
from app.models.orders import Order


class OrderBaseSchema(BaseModel):
    start_date: date
    end_date: date


class OrderCreateSchema(OrderBaseSchema):
    equipment_id: int


class OrderUpdateSchema(BaseModel):
    start_date: date = None
    end_date: date = None


# class OrderSchema(OrderBaseSchema):
#     id: int
#     equipment: EquipmentListSchema
#     requester: UserSchema
#     status: OrderStatus
#     created_at: datetime

#     class Config:
#         orm_mode = True

OrderSchema = pydantic_model_creator(Order, name="OrderSchema")
OrderListSchema = pydantic_queryset_creator(Order)
