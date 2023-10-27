from datetime import date

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app import _init_models  # noqa: F401
from app.models.orders import Order


class OrderCreateSchema(BaseModel):
    equipment_id: int
    start_date: date
    end_date: date


class OrderUpdateSchema(BaseModel):
    start_date: date = None
    end_date: date = None


OrderSchema = pydantic_model_creator(Order, name="OrderSchema")
OrderListSchema = pydantic_queryset_creator(Order)


class ChatCredentialsSchema(BaseModel):
    username: str
    user_secret: str
    interlocutor_username: str
