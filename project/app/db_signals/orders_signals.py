import logging
from typing import Optional, Type

from tortoise import BaseDBAsyncClient
from tortoise.signals import post_save, pre_save

from app.crud.notifications import (
    create_organization_order_notification,
    create_requester_order_notification,
)
from app.models.notifications import IncomingOrderType, OutgoingOrderType
from app.models.orders import Order, OrderStatus

log = logging.getLogger("uvicorn")


@post_save(Order)
async def order_post_save(
    sender: Type[Order],
    order: Order,
    created: bool,
    using_db: Optional[BaseDBAsyncClient],
    update_fields: list[str],
) -> None:
    if created:
        await create_organization_order_notification(order, IncomingOrderType.ORDER_CREATED)


@pre_save(Order)
async def order_pre_save(
    sender: Type[Order],
    order: Order,
    using_db: Optional[BaseDBAsyncClient],
    update_fields: list[str],
) -> None:
    if update_fields and "status" in update_fields:
        match order.status:
            case OrderStatus.CONTRACT_FORMATION:
                await create_requester_order_notification(order, event=OutgoingOrderType.ORDER_ACCEPTED)
            case OrderStatus.REJECTED:
                await create_requester_order_notification(order, event=OutgoingOrderType.ORDER_REJECTED)
            case OrderStatus.CANCELED:
                await create_organization_order_notification(order, event=IncomingOrderType.ORDER_CANCELED)

    if update_fields and ("start_date" in update_fields or "end_date" in update_fields):
        await create_organization_order_notification(order, event=IncomingOrderType.ORDER_UPDATED)
        # change status to created
