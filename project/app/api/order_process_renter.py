import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.equipment import get_equipment_by_id
from app.crud.orders import (
    update_order_status,
    create_order,
    get_order_by_id,
    get_user_orders,
    update_order_details,
    update_order,
)
from app.models.equipment import EquipmentStatus
from app.models.orders import OrderStatus, Order
from app.models.users import User
from app.schemas.orders import (
    OrderCreateSchema,
    OrderListSchema,
    OrderSchema,
    OrderUpdateSchema,
)
from app.services.auth import get_current_active_user
from app.services.payments import create_payment_link

log = logging.getLogger("uvicorn")


async def get_own_order(order_id: int, current_user: User) -> Order:
    order = await get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.requester == current_user:
        return order
    
    user_organization = await current_user.organization
    requester_organization = await order.requester.organization
    if user_organization and requester_organization and current_user.is_verified_organization_member and user_organization == requester_organization:
        return order

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


router = APIRouter()


@router.get("/", response_model=OrderListSchema)
async def get_outgoing_orders_(
    current_user: User = Depends(get_current_active_user),
    offset: int = 0,
    limit: int = 40,
):
    """Get outgoing orders for current user"""
    return await get_user_orders(current_user, offset=offset, limit=limit)



@router.post("/", response_model=OrderSchema)
async def create_order_(create_schema: OrderCreateSchema, current_user: User = Depends(get_current_active_user)):
    """Create outgoing order for equipment"""
    equipment = await get_equipment_by_id(create_schema.equipment_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.status != EquipmentStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Equipment not published")

    order = await create_order(equipment, current_user, create_schema)
    return order


@router.put("/{order_id}/", response_model=OrderSchema)
async def update_order_(
    order_id: int, update_schema: OrderUpdateSchema, current_user: User = Depends(get_current_active_user)
):
    """Update outgoing order details (start_date and end_date for now)"""
    order = await get_own_order(order_id, current_user)
    if order.status > OrderStatus.CREATED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Order with status '{order.status}' can't be updated")
    order = await update_order_details(order, update_schema)
    return order


@router.delete("/{order_id}/cancel", response_model=OrderSchema)
async def cancel_order_(order_id: int, current_user: User = Depends(get_current_active_user)):
    """Cancel outgoing order"""
    order = await get_own_order(order_id, current_user)
    if order.status > OrderStatus.CONTRACT_SIGNING:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Order with status '{order.status}' can't be canceled")
    order = await update_order_status(order, OrderStatus.CANCELED)
    return order


@router.put("/{order_id}/accept-cost", response_model=OrderSchema)
async def accept_cost_(order_id: int, current_user: User = Depends(get_current_active_user)):
    """Accept cost of outgoing order"""
    order = await get_own_order(order_id, current_user)
    if order.status != OrderStatus.COST_NEGOTIATION:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not waiting for cost acceptance")
    order = await update_order(order, ("cost_accepted_by_renter", True), OrderStatus.CONTRACT_FORMATION)
    return order


@router.post("/{order_id}/repeat", response_model=OrderSchema)
async def repeat_order_(order_id: int, current_user: User = Depends(get_current_active_user)):
    """Repeat outgoing order"""
    order = await get_own_order(order_id, current_user)
    if order.status != OrderStatus.CANCELED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not canceled")
    order = await create_order_(
        OrderCreateSchema(equipment_id=order.equipment.id, start_date=order.start_date, end_date=order.end_date),
        current_user
    )
    return order


@router.get("/{order_id}/get-payment-link/")
async def get_payment_link_(order_id: int, return_url: str, current_user: User = Depends(get_current_active_user)):
    """Get payment link for order"""
    order = await get_own_order(order_id, current_user)
    if order.status != OrderStatus.WAITING_FOR_PAYMENT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not waiting for payment")

    link = create_payment_link(order.cost(), f"Оплата заказа №{order.id}", return_url)
    return {"paymentLink": link}
