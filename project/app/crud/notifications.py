import logging
from datetime import datetime

from tortoise.expressions import Q

from app.models.notifications import (
    IncomingOrderNotification,
    IncomingOrderType,
    Notification,
    NotificationStatus,
    NotificationType,
    OrganizationVerificationNotification,
    OrganizationVerificationType,
    OutgoingOrderNotification,
    OutgoingOrderType,
)
from app.models.orders import Order
from app.models.users import User

log = logging.getLogger("uvicorn")


async def create_organization_status_notification(user: User, event: OrganizationVerificationType) -> Notification:
    content = OrganizationVerificationNotification(event=event)
    notification = await Notification.create(
        recipient=user,
        type=NotificationType.ORGANIZATION_VERIFICATION,
        content=content.json(),
    )
    log.info(f"Notification created: {notification.id}")
    return notification


async def create_requester_order_notification(order: Order, event: OutgoingOrderType) -> Notification:
    content = OutgoingOrderNotification(event=event, order_id=order.id)
    notification = await Notification.create(
        recipient=await order.requester,
        type=NotificationType.OUTGOING_ORDER,
        content=content.json(),
    )
    log.info(f"Notification created: {notification.id}")
    return notification


async def create_organization_order_notification(order: Order, event: IncomingOrderType) -> Notification:
    await order.fetch_related("equipment__organization")
    content = IncomingOrderNotification(event=event, order_id=order.id)
    notification = await Notification.create(
        organization=order.equipment.organization,
        type=NotificationType.INCOMING_ORDER,
        content=content.json(),
    )
    log.info(f"Notification created: {notification.id}")
    return notification


async def update_notifications_status(notification_id_list: list[int], new_status: NotificationStatus) -> None:
    update_fields = {
        "status": new_status,
    }
    match new_status:
        case NotificationStatus.DELIVERED:  # Not used while there is no notification system
            # update_fields['delivered_at'] = datetime.now()
            pass
        case NotificationStatus.READ:
            update_fields["read_at"] = datetime.now()

    await Notification.filter(id__in=notification_id_list).update(**update_fields)
    log.info(f"Notifications updated to {new_status}: {notification_id_list}")


async def get_renter_notifications(
    user: User, unread: bool = False, offset: int = 0, limit: int = 40
) -> list[Notification]:
    if unread:
        notifications = Notification.filter(recipient=user, status=NotificationStatus.CREATED)
    else:
        notifications = Notification.filter(recipient=user)
    return (
        await notifications.order_by("-created_at")
        .offset(offset)
        .limit(limit)
        .all()
        .prefetch_related(
            "organization__main_activity",
            "recipient",
        )
    )


async def get_owner_notifications(
    user: User, unread: bool = False, offset: int = 0, limit: int = 40
) -> list[Notification]:
    await user.fetch_related("organization")
    if unread:
        notifications = Notification.filter(
            Q(recipient=user) | Q(organization=user.organization), status=NotificationStatus.CREATED
        )
    else:
        notifications = Notification.filter(Q(recipient=user) | Q(organization=user.organization))
    return (
        await notifications.order_by("-created_at")
        .offset(offset)
        .limit(limit)
        .all()
        .prefetch_related(
            "organization__main_activity",
            "recipient",
        )
    )


async def read_notifications(notification_id_list: list[int]) -> None:
    await update_notifications_status(notification_id_list, NotificationStatus.READ)
