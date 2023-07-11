from datetime import date, datetime

from pydantic import BaseModel

from app.models.orders import OrderStatus
from app.schemas.equipment import EquipmentListSchema


class OrderCreateSchema(BaseModel):
    equipment_id: int
    start_date: date
    end_date: date


class OrderRenterUpdateSchema(BaseModel):
    id: int
    status: OrderStatus = None
    start_date: date = None
    end_date: date = None


class OrderOwnerUpdateSchema(BaseModel):
    id: int
    status: OrderStatus


class OrderSchema(BaseModel):
    id: int
    equipment: EquipmentListSchema
    start_date: date
    end_date: date
    status: OrderStatus
    created_at: datetime

    class Config:
        orm_mode = True
