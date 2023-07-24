from datetime import date, datetime

from pydantic import BaseModel

from app.models.orders import OrderStatus
from app.schemas.equipment import EquipmentListSchema
from app.schemas.users import UserSchema


class OrderBaseSchema(BaseModel):
    start_date: date
    end_date: date


class OrderCreateSchema(OrderBaseSchema):
    equipment_id: int


class OrderUpdateSchema(BaseModel):
    start_date: date = None
    end_date: date = None


class OrderSchema(OrderBaseSchema):
    id: int
    equipment: EquipmentListSchema
    requester: UserSchema
    status: OrderStatus
    created_at: datetime

    class Config:
        orm_mode = True
