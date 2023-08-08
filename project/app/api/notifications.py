import logging

from fastapi import APIRouter, Depends, status

from app.crud.notifications import (
    get_owner_notifications,
    get_renter_notifications,
    read_notifications,
)
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.notifications import NotificationListSchema
from app.services.auth import get_current_active_user
from app.services.organizations import get_current_verified_organization

log = logging.getLogger("uvicorn")


router = APIRouter()


@router.get("/renter/", response_model=NotificationListSchema)
async def get_notifications_renter(
    current_user: User = Depends(get_current_active_user),
    unread: bool = False,
    offset: int = 0,
    limit: int = 40,
):
    """Get notifications for current user"""
    notifications = await get_renter_notifications(current_user, unread, offset, limit)
    return notifications


@router.get("/owner/", response_model=NotificationListSchema)
async def get_notifications_owner(
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_verified_organization),
    unread: bool = False,
    offset: int = 0,
    limit: int = 40,
):
    """Get notifications for current user"""
    notifications = await get_owner_notifications(current_user, unread, offset, limit)
    return notifications


@router.put("/renter/read/", status_code=status.HTTP_202_ACCEPTED)
async def read_notifications_renter(
    current_user: User = Depends(get_current_active_user),
    notification_id_list: list[int] = [],
):
    """Read notifications for current user"""
    await read_notifications(notification_id_list)
    return


@router.put("/owner/read/", status_code=status.HTTP_202_ACCEPTED)
async def read_notifications_owner(
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_verified_organization),
    notification_id_list: list[int] = [],
):
    """Read notifications for current user"""
    await read_notifications(notification_id_list)
    return
