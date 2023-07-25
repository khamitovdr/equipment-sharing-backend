import logging
from typing import Type
from datetime import datetime

from app.models.users import User
from app.models.organizations import Organization
from app.models.orders import Order, OrderStatus
from app.models.notifications import BaseNotification, UserBaseNotification, OrganizationBaseNotification, UserOrganizationNotification, UserOrderNotification, OrganizationOrderNotification, UserOrganizationNotificationType, UserOrderNotificationType, NotificationStatus, OrganizationNotificationType


log = logging.getLogger("uvicorn")


async def create_organization_verified_notification(user: User) -> UserOrganizationNotification:
    notification = await UserOrganizationNotification.create(
        recipient=user,
        type=UserOrganizationNotificationType.ORGANIZATION_VERIFIED,
    )
    log.info(f"Notification created: {notification.id}")
    return notification


async def create_requester_order_notification(order: Order, type: UserOrderNotificationType) -> UserOrderNotification:
    notification = await UserOrderNotification.create(
        recipient=order.requester,
        order=order,
        type=type,
    )
    log.info(f"Notification created: {notification.id}")
    return notification


async def create_organization_order_notification(order: Order, type: OrganizationNotificationType) -> OrganizationOrderNotification:
    await order.fetch_related('equipment__organization')
    notification = await OrganizationOrderNotification.create(
        organization=order.equipment.organization,
        order=order,
        type=type,
    )
    log.info(f"Notification created: {notification.id}")
    return notification


async def update_notifications_status(model: Type[BaseNotification], notification_id_list: list[int], new_status: NotificationStatus) -> list[BaseNotification]:
    update_fields = {
        'status': new_status,
    }
    match new_status:
        case NotificationStatus.DELIVERED: # Not used while there is no notification system
            # update_fields['delivered_at'] = datetime.now()
            pass
        case NotificationStatus.READ:
            update_fields['read_at'] = datetime.now()

    await model.filter(id__in=notification_id_list).update(**update_fields)
    log.info(f"Notifications updated to {new_status}: {notification_id_list}")


async def get_user_notifications(user: User, model: Type[UserBaseNotification]) -> list[UserBaseNotification]:
    notifications = await model.filter(recipient=user, status=NotificationStatus.CREATED).all()
    return notifications


async def get_organization_notifications(organization: Organization, model: Type[OrganizationBaseNotification]) -> list[OrganizationBaseNotification]:
    notifications = await model.filter(organization=organization, status=NotificationStatus.CREATED).all()
    return notifications


async def read_notifications(model: Type[BaseNotification], notification_id_list: list[int]):
    await update_notifications_status(model, notification_id_list, NotificationStatus.READ)
