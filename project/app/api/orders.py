import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.users import User
from app.models.orders import OrderStatus
from app.models.equipment import EquipmentStatus
from app.models.organizations import Organization
from app.schemas.orders import OrderCreateSchema, OrderRenterUpdateSchema, OrderOwnerUpdateSchema, OrderSchema
from app.services.auth import get_current_active_user
from app.services.organizations import get_current_verified_organization
from app.crud.equipment import get_equipment_by_id
from app.crud.orders import create_order, update_order_renter, update_order_owner, get_order_by_id, get_organization_orders, get_user_orders


log = logging.getLogger("uvicorn")


router = APIRouter()


@router.get("/", response_model=list[OrderSchema])
async def get_orders_(current_user: User = Depends(get_current_active_user)):
    return await get_user_orders(current_user)


@router.get("/requests/", response_model=list[OrderSchema])
async def get_requests_(
    organization: Organization = Depends(get_current_verified_organization),
    ):
    return await get_organization_orders(organization)


@router.post("/", response_model=OrderSchema)
async def create_order_(create_schema: OrderCreateSchema, current_user: User = Depends(get_current_active_user)):
    equipment = await get_equipment_by_id(create_schema.equipment_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.status != EquipmentStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Equipment not published")
    
    order = await create_order(equipment, current_user, create_schema)
    log.info(f"Order created: {type(order)}")
    return order


# @router.get("/{order_id}/", response_model=OrderSchema)
# async def get_order(order_id: int, current_user: User = Depends(get_current_active_user)):
#     order = await get_order_by_id(order_id)
#     if order is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
#     if order.requester != current_user and order.equipment.owner != current_user:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
#     return order


@router.put("/renter/{order_id}/", response_model=OrderSchema)
async def update_order_renter_(update_schema: OrderRenterUpdateSchema, current_user: User = Depends(get_current_active_user)):
    order = await get_order_by_id(update_schema.id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.requester != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    order = await update_order_renter(order, update_schema)
    return order
