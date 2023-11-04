import logging
from datetime import date
from typing import Any

from fastapi import HTTPException, status

from app.models.equipment import Equipment
from app.models.orders import (
    Order,
    OrderContractDraft,
    OrderPayment,
    OrderStatus,
    PaymentType,
    OrderContract,
    OrderContractSignature,
    OrderContractSignatureRenter,
    OrderContractSignatureOwner,
)
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.orders import OrderCreateSchema, OrderUpdateSchema
from app.services.orders import create_chatengine_users
from app.services.payments import check_payment_succeed

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
    await create_chatengine_users(order)
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


async def get_contract_drafts(order: Order, only_last: bool = False) -> list[OrderContractDraft]:
    query = order.contract_drafts.order_by("-created_at").prefetch_related("added_by")
    if only_last:
        return await query.first()
    return await query.all()


async def confirm_contract_draft(order: Order) -> Order:
    # all contract drafts except last one are deleted
    contract_drafts = await get_contract_drafts(order)
    if not contract_drafts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract draft not found")
    for contract_draft in contract_drafts[1:]:
        await contract_draft.delete()
    return await update_order_status(order, OrderStatus.CONTRACT_NEGOTIATION)


async def create_contract(order: Order, contract_draft: OrderContractDraft) -> OrderContract:
    contract = await OrderContract.create(
        host=order,
        name=contract_draft.name,
        media_type=contract_draft.media_type,
        media_format=contract_draft.media_format,
        hash=contract_draft.hash,
        path=contract_draft.path,
        added_by=contract_draft.added_by,
    )
    return contract


async def accept_last_contract_draft(order: Order, role: str) -> OrderContractDraft:
    contract_draft = await get_contract_drafts(order, only_last=True)
    if contract_draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract draft not found")
    if role == "owner":
        contract_draft.accepted_by_owner = True
        update_fields = ["accepted_by_owner"]
    elif role == "renter":
        contract_draft.accepted_by_renter = True
        update_fields = ["accepted_by_renter"]
    else:
        raise ValueError("Role must be 'owner' or 'renter'")
    await contract_draft.save(update_fields=update_fields)

    if contract_draft.accepted_by_owner and contract_draft.accepted_by_renter:
        await create_contract(order, contract_draft)
        await update_order_status(order, OrderStatus.CONTRACT_SIGNING)

    return contract_draft


async def create_payment(order: Order, payment_id: str, payment_status: str) -> OrderPayment:
    payment = await OrderPayment.create(
        id=payment_id,
        corresponding_order_id=order.id,
        amount=order.cost,
        status=payment_status,
    )
    return payment


async def confirm_payment_by_id(payment_id: int, payment_details: dict) -> Order:
    if not check_payment_succeed(payment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment not succeed")

    payment = await OrderPayment.get_or_none(id=payment_id)
    if payment is None:
        raise ValueError(f"Payment with id={payment_id} not found")

    order = await Order.get_or_none(id=payment.corresponding_order_id)
    if order is None:
        raise ValueError(f"Order with id={payment.corresponding_order_id} not found")

    assert order.status == OrderStatus.WAITING_FOR_PAYMENT
    assert order.payment_type == PaymentType.VIA_PLATFORM
    assert order.cost == float(payment_details["object"]["amount"]["value"])

    payment.order = order
    payment.events.append(payment_details)
    payment.status = payment_details["object"]["status"]
    await payment.save(update_fields=["order_id", "events", "status"])

    await OrderPayment.filter(corresponding_order_id=order.id, order_id__isnull=True).delete()

    order.is_paid = True
    order.status = OrderStatus.ACCEPTANCE_BY_RENTER
    await order.save(update_fields=["is_paid", "status"])

    return order
