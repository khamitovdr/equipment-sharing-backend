import logging
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile

from app.crud.orders import (
    update_order_status,
    get_order_by_id,
    get_organization_orders,
    update_order,
    get_contract_drafts,
    accept_last_contract_draft,
    confirm_contract_draft,
)
from app.crud.files import create_uploaded_file
from app.models.orders import OrderStatus, Order, OrderContractDraft, OrderContractSignatureOwner, PaymentType
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.orders import (
    OrderListSchema,
    OrderSchema,
    OrderContractDraftSchema,
)
from app.schemas.files import FileBaseSchema
from app.services.auth import get_current_active_user
from app.crud.organizations import get_current_verified_organization
from app.services.documents import get_contract_template
from app.services.orders import verify_e_signature

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


@router.get("/{order_id}/", response_model=OrderSchema)
async def get_request_(
    order_id: int,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Get incoming order by id"""
    order = await get_own_order(order_id, organization)
    return order


@router.delete("/{order_id}/reject/", response_model=OrderSchema, status_code=status.HTTP_202_ACCEPTED)
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


@router.put("/{order_id}/accept", response_model=OrderSchema, status_code=status.HTTP_202_ACCEPTED)
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


@router.put("/{order_id}/set-cost", response_model=OrderSchema, status_code=status.HTTP_202_ACCEPTED)
async def set_cost_(
    order_id: int,
    cost: float,
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


@router.post("/{order_id}/contract-drafts/", response_model=FileBaseSchema, status_code=status.HTTP_201_CREATED)
async def upload_contract_draft_(
    contract_draft: UploadFile,
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_verified_organization),
):
    """Upload contract draft"""
    order = await get_own_order(order_id, organization)
    if order.status not in (OrderStatus.CONTRACT_FORMATION, OrderStatus.CONTRACT_NEGOTIATION):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't upload contract draft for order with status '{order.status}'")
    
    file = await create_uploaded_file(
        contract_draft, OrderContractDraft, current_user,
        allowed_types=["application", "text"], host=order
    )
    return file


@router.put("/{order_id}/confirm-draft/", response_model=OrderSchema, status_code=status.HTTP_202_ACCEPTED)
async def confirm_contract_draft_(
    order_id: int,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Confirm contract draft for order"""
    order = await get_own_order(order_id, organization)
    if order.status != OrderStatus.CONTRACT_FORMATION:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't confirm contract draft for order with status '{order.status}'")
    order = await confirm_contract_draft(order)
    return order


@router.get("/{order_id}/contract-drafts/", response_model=list[OrderContractDraftSchema])
async def get_contract_drafts_(
    order_id: int,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Get contract drafts for order"""
    order = await get_own_order(order_id, organization)
    return await get_contract_drafts(order)


@router.get("/{order_id}/contract-drafts/last/", response_model=OrderContractDraftSchema)
async def get_last_contract_draft_(
    order_id: int,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Get last contract draft for order"""
    order = await get_own_order(order_id, organization)
    draft = await get_contract_drafts(order, only_last=True)
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract draft not found")
    return draft


@router.put("/{order_id}/accept-last-draft/", response_model=OrderSchema, status_code=status.HTTP_202_ACCEPTED)
async def accept_last_contract_draft_(
    order_id: int,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Accept last contract draft for order"""
    order = await get_own_order(order_id, organization)
    if order.status != OrderStatus.CONTRACT_NEGOTIATION:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't accept contract draft for order with status '{order.status}'")
    await accept_last_contract_draft(order, "owner")
    return order


@router.post("/{order_id}/e-sign/", response_model=FileBaseSchema, status_code=status.HTTP_202_ACCEPTED)
async def upload_e_sign_(
    e_sign_data: UploadFile,
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_verified_organization),
):
    """Upload contract draft"""
    order = await get_own_order(order_id, organization)
    contract = await order.contract
    if order.status != OrderStatus.CONTRACT_SIGNING:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't upload e-sign for order with status '{order.status}'")
    
    if not await verify_e_signature(e_sign_data, order, "owner"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-sign is not valid")
    
    e_sign = await create_uploaded_file(
        e_sign_data, OrderContractSignatureOwner, current_user,
        allowed_types=["application", "text"], host=contract
    )
    e_sign.verified = True
    await e_sign.save()

    if await contract.signature_renter:
        await update_order_status(order, OrderStatus.CHOOSING_PAYMENT_METHOD)

    return e_sign


@router.put("/{order_id}/signed-offline/", response_model=OrderSchema, status_code=status.HTTP_202_ACCEPTED)
async def set_signed_offline_(
    order_id: int,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Sign contract offline"""
    order = await get_own_order(order_id, organization)
    if order.status != OrderStatus.CONTRACT_SIGNING:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't sign contract offline for order with status '{order.status}'")
    order = await update_order(order, ("signed_offline_by_owner", True))

    if order.signed_offline_by_renter:
        await update_order_status(order, OrderStatus.CHOOSING_PAYMENT_METHOD)

    return order


@router.put("/{order_id}/payment-type/", response_model=OrderSchema, status_code=status.HTTP_202_ACCEPTED)
async def set_payment_type_(
    order_id: int,
    payment_type: PaymentType,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Set payment type for order"""
    order = await get_own_order(order_id, organization)
    if order.status != OrderStatus.CHOOSING_PAYMENT_METHOD:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't set payment type for order with status '{order.status}'")
    order = await update_order(order, ("payment_type", payment_type), OrderStatus.WAITING_FOR_PAYMENT)
    return order
