import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.equipment import get_equipment_by_id
from app.crud.orders import (
    cancel_order,
    create_order,
    get_order_by_id,
    get_organization_orders,
    get_user_orders,
    respond_to_order,
    update_order,
)
from app.models.equipment import EquipmentStatus
from app.models.orders import OrderResponseStatus, OrderStatus
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.orders import (
    OrderCreateSchema,
    OrderListSchema,
    OrderSchema,
    OrderUpdateSchema,
)
from app.services.auth import get_current_active_user
from app.services.organizations import get_current_verified_organization
from app.services.payments import create_payment_link
from app.services.documents import get_contract_template

log = logging.getLogger("uvicorn")


router = APIRouter()


@router.get("/", response_model=OrderListSchema)
async def get_outgoing_orders_(
    current_user: User = Depends(get_current_active_user),
    offset: int = 0,
    limit: int = 40,
):
    """Get outgoing orders for current user"""
    return await get_user_orders(current_user, offset=offset, limit=limit)


@router.get("/requests/", response_model=OrderListSchema)
async def get_requests_(
    organization: Organization = Depends(get_current_verified_organization),
    offset: int = 0,
    limit: int = 40,
):
    """Get incoming orders for current organization"""
    return await get_organization_orders(organization, offset=offset, limit=limit)


@router.post("/", response_model=OrderSchema)
async def create_order_(create_schema: OrderCreateSchema, current_user: User = Depends(get_current_active_user)):
    """Create outgoing order for equipment"""
    equipment = await get_equipment_by_id(create_schema.equipment_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.status != EquipmentStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Equipment not published")

    try:
        order = await create_order(equipment, current_user, create_schema)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))

    return order


@router.put("/{order_id}/", response_model=OrderSchema)
async def update_order_(
    order_id: int, update_schema: OrderUpdateSchema, current_user: User = Depends(get_current_active_user)
):
    """Update outgoing order details (start_date and end_date for now)"""
    order = await get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.requester != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    try:
        order = await update_order(order, update_schema)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))

    return order


@router.put("/{order_id}/cancel", response_model=OrderSchema)
async def cancel_order_(order_id: int, current_user: User = Depends(get_current_active_user)):
    """Cancel outgoing order"""
    order = await get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.requester != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    try:
        order = await cancel_order(order)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))

    return order


@router.put("/{order_id}/reply/", response_model=OrderSchema)
async def respond_to_order_(
    order_id: int,
    response: OrderResponseStatus,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Respond to incoming order"""
    order = await get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if await order.equipment.organization != organization:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    response = OrderStatus(response.value)
    order = await respond_to_order(order, response)
    return order


@router.get("/{order_id}/contract-template/")
async def get_contract_template_(order_id: int, current_user: User = Depends(get_current_active_user)):
    order = await get_order_by_id(order_id)
    user_organization = await current_user.organization
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if not (
        (order.requester == current_user or await order.requester.organization == user_organization) or
        (current_user.is_verified_organization_member and await order.equipment.organization == user_organization)
        ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    download_link = await get_contract_template("Москва", order)
    return {"downloadLink": download_link}


@router.get("/get-payment-link/{order_id}/")
async def get_payment_link_(order_id: int, return_url: str, current_user: User = Depends(get_current_active_user)):
    """Get payment link for order"""
    order = await get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.requester != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if order.status != OrderStatus.WAITING_FOR_PAYMENT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not waiting for payment")

    link = create_payment_link(order.total_cost(), f"Оплата заказа №{order.id}", return_url)
    return {"paymentLink": link}


@router.patch("/{order_id}/set-waiting-for-payment/", response_model=OrderSchema)
async def set_waiting_payment(order_id: int):
    order = await get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order.status = OrderStatus.WAITING_FOR_PAYMENT
    await order.save()

    return order
