import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.orders import (
    get_order_by_id,
)
from app.models.users import User
from app.schemas.orders import ChatCredentialsSchema
from app.services.orders import get_user_secret
from app.services.auth import get_current_active_user

log = logging.getLogger("uvicorn")


router = APIRouter()


@router.get("/{order_id}/chat-credentials", response_model=ChatCredentialsSchema)
async def get_order_(order_id: int, current_user: User = Depends(get_current_active_user)):
    """Get order by id"""
    order = await get_order_by_id(order_id)
    user_organization = await current_user.organization
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")    

    if order.requester == current_user or await order.requester.organization == user_organization:
        return ChatCredentialsSchema(
            username=f"order-{order.id}_renter",
            user_secret=get_user_secret(order.id, "renter"),
            interlocutor_username=f"order-{order.id}_owner",
        )
    elif current_user.is_verified_organization_member and await order.equipment.organization == user_organization:
        return ChatCredentialsSchema(
            username=f"order-{order.id}_owner",
            user_secret=get_user_secret(order.id, "owner"),
            interlocutor_username=f"order-{order.id}_renter",
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
