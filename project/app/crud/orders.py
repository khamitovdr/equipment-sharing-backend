import logging
from datetime import date

from app.models.users import User
from app.models.organizations import Organization
from app.models.orders import Order, OrderStatus
from app.models.equipment import Equipment
from app.schemas.orders import OrderCreateSchema, OrderUpdateSchema


log = logging.getLogger("uvicorn")


async def create_order(equipment: Equipment, requester: User, order_schema: OrderCreateSchema) -> Order:
    if order_schema.start_date < date.today():
        raise ValueError("Start date is in the past")
    if order_schema.start_date > order_schema.end_date:
        raise ValueError("Start date is after end date")
    order = await Order.create(
        equipment=equipment,
        requester=requester,
        start_date=order_schema.start_date,
        end_date=order_schema.end_date,
    )
    log.info(f"Order created: {order.id}")
    await order.fetch_related('equipment__category', 'equipment__organization', 'requester')
    return order


async def get_order_by_id(order_id: int) -> Order:
    order = await Order.get_or_none(id=order_id)
    if order is None:
        return None
    await order.fetch_related('equipment__category', 'equipment__organization', 'requester')
    return order


async def get_user_orders(user: User) -> list[Order]:
    user_orders = await Order.filter(requester=user).prefetch_related('equipment__category', 'equipment__organization', 'requester').all()
    return user_orders


async def get_organization_orders(organization: Organization) -> list[Order]:
    organization_orders = await Order \
        .filter(equipment__organization=organization) \
        .exclude(status=OrderStatus.CANCELED) \
        .prefetch_related('equipment__category', 'equipment__organization', 'requester') \
        .all()
    return organization_orders


async def respond_to_order(order: Order, response: OrderStatus) -> Order:
    order.status = response
    await order.save()
    log.info(f"Response to order {order.id}: {response}")
    return order


async def update_order(order: Order, order_schema: OrderUpdateSchema) -> Order:
    if order.status not in (OrderStatus.CREATED, OrderStatus.ACCEPTED):
        raise ValueError("Order can't be updated")
    if order_schema.start_date and order_schema.start_date < date.today():
        raise ValueError("Start date is in the past")
    if (
        order_schema.start_date and order_schema.end_date and order_schema.start_date > order_schema.end_date or
        order_schema.start_date and order_schema.start_date > order.end_date or
        order_schema.end_date and order.start_date > order_schema.end_date
        ):
        raise ValueError("Start date is after end date")
    
    await order.update_from_dict(order_schema.dict(exclude_unset=True)).save()
    log.info(f"Order updated: {order.id}")
    return order


async def cancel_order(order: Order) -> Order:
    if order.status not in (OrderStatus.CREATED, OrderStatus.ACCEPTED, OrderStatus.REJECTED):
        raise ValueError(f"Order with status \"{order.status}\" can't be canceled")
    order.status = OrderStatus.CANCELED
    await order.save()
    log.info(f"Order canceled: {order.id}")
    return order
