import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.orders import (
    update_order_status,
    get_order_by_id,
    get_organization_orders,
    update_order,
)
from app.models.orders import OrderStatus, Order
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.orders import (
    OrderListSchema,
    OrderSchema,
)
from app.services.auth import get_current_active_user
from app.services.organizations import get_current_verified_organization
from app.services.documents import get_contract_template

log = logging.getLogger("uvicorn")


async def get_own_order(order_id: int, organization: Organization) -> Order:
    order = await get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if await order.equipment.organization != organization:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return order


router = APIRouter()


@router.get("/", response_model=OrderListSchema)
async def get_requests_(
    organization: Organization = Depends(get_current_verified_organization),
    offset: int = 0,
    limit: int = 40,
):
    """Get incoming orders for current organization"""
    return await get_organization_orders(organization, offset=offset, limit=limit)


@router.delete("/{order_id}/reject/", response_model=OrderSchema)
async def reject_order_(
    order_id: int,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Reject incoming order"""
    order = await get_own_order(order_id, organization)
    if order.status > OrderStatus.CONTRACT_SIGNING:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Order with status '{order.status}' can't be canceled")
    order = await update_order_status(order, OrderStatus.REJECTED)
    return order


@router.put("/{order_id}/accept", response_model=OrderSchema)
async def accept_order_(
    order_id: int,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Accept incoming order"""
    order = await get_own_order(order_id, organization)
    if order.status != OrderStatus.CREATED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Order with status '{order.status}' can't be accepted")
    order = await update_order_status(order, OrderStatus.CONTRACT_FORMATION)
    return order


@router.put("/{order_id}/set-cost", response_model=OrderSchema)
async def set_cost_(
    order_id: int,
    cost: int,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Set cost for order"""
    order = await get_own_order(order_id, organization)
    if order.status not in (OrderStatus.CREATED, OrderStatus.REJECTED, OrderStatus.COST_NEGOTIATION):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't set cost for order with status '{order.status}'")
    order = await update_order(order, ("cost", cost), OrderStatus.COST_NEGOTIATION)
    return order


@router.get("/{order_id}/contract-template/")
async def get_contract_template_(order_id: int, organization: Organization = Depends(get_current_verified_organization)):
    order = await get_own_order(order_id, organization)
    download_link = await get_contract_template("Москва", order)
    return {"downloadLink": download_link}
