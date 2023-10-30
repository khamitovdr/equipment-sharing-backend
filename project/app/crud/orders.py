import logging
from datetime import date
from typing import Any

from fastapi import HTTPException, status

from app.models.equipment import Equipment
from app.models.orders import Order, OrderStatus
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.orders import OrderCreateSchema, OrderUpdateSchema

log = logging.getLogger("uvicorn")


async def create_order(equipment: Equipment, requester: User, order_schema: OrderCreateSchema) -> Order:
    if order_schema.start_date < date.today():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Start date is in the past")
    if order_schema.start_date > order_schema.end_date:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Start date is after end date")
    order = await Order.create(
        equipment=equipment,
        requester=requester,
        start_date=order_schema.start_date,
        end_date=order_schema.end_date,
    )
    order.cost = order.estimated_cost()
    await order.save(update_fields=["cost"])
    log.info(f"Order created: {order.id}")
    await order.fetch_related(
        "equipment__category",
        "equipment__photo_and_video",
        "requester",
    )
    return order


async def get_order_by_id(order_id: int) -> Order:
    order = await Order.get_or_none(id=order_id)
    if order is None:
        return None
    await order.fetch_related(
        "equipment__category",
        "equipment__photo_and_video",
        "requester",
    )
    return order


async def get_user_orders(user: User, offset: int = 0, limit: int = 40) -> list[Order]:
    user_orders = (
        await Order.filter(requester=user)
        .order_by("-created_at")
        .offset(offset)
        .limit(limit)
        .all()
        .prefetch_related(
            "equipment__category",
            "equipment__photo_and_video",
            "requester",
        )
    )
    return user_orders


async def get_organization_orders(organization: Organization, offset: int = 0, limit: int = 40) -> list[Order]:
    organization_orders = (
        await Order.filter(equipment__organization=organization)
        .exclude(status=OrderStatus.CANCELED)
        .order_by("-created_at")
        .offset(offset)
        .limit(limit)
        .all()
        .prefetch_related(
            "equipment__category",
            "equipment__photo_and_video",
            "requester",
        )
    )
    return organization_orders


async def update_order_details(order: Order, order_schema: OrderUpdateSchema) -> Order:
    if order.status != OrderStatus.CREATED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Order can't be updated")
    if order_schema.start_date and order_schema.start_date < date.today():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Start date is in the past")
    if (
        order_schema.start_date
        and order_schema.end_date
        and order_schema.start_date > order_schema.end_date
        or order_schema.start_date
        and order_schema.start_date > order.end_date
        or order_schema.end_date
        and order.start_date > order_schema.end_date
    ):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Start date is after end date")

    update_dict = order_schema.dict(exclude_unset=True)
    await order.update_from_dict(update_dict).save(update_fields=update_dict.keys())
    await order.fetch_related("equipment__category", "equipment__photo_and_video", "requester")
    return order


async def update_order_status(order: Order, new_status: OrderStatus) -> Order:
    order.status = new_status
    await order.save(update_fields=["status"])
    await order.fetch_related("equipment__category", "equipment__photo_and_video", "requester")
    log.info(f"Order status updated: {order.id}")
    return order


async def update_order(order: Order, update: (str, Any) = (None, None), new_status: OrderStatus = None) -> Order:
    updated_fields = []
    if new_status is not None:
        order.status = new_status
        updated_fields.append("status")
    
    order_field, field_value = update
    if order_field is not None:
        setattr(order, order_field, field_value)
        updated_fields.append(order_field)

    await order.save(update_fields=updated_fields)
    await order.fetch_related("equipment__category", "equipment__photo_and_video", "requester")
    log.info(f"Order updated: {order.id}")
    return order
