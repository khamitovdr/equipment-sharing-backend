import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.orders import get_order_by_id
from app.crud.reviews import (
    compute_csi,
    compute_nps,
    create_nps_csi_feedback,
    create_or_update_review,
)
from app.models.users import User
from app.schemas.reviews import FeedbackCreateSchema, ReviewCreateSchema, ReviewSchema
from app.services.auth import get_current_active_user

log = logging.getLogger("uvicorn")


router = APIRouter()


@router.post("/{order_id}/", status_code=status.HTTP_201_CREATED, response_model=ReviewSchema)
async def create_owner_review(
    order_id: int, review: ReviewCreateSchema, user: User = Depends(get_current_active_user)
):
    order = await get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if user == order.requester:
        review = await create_or_update_review(order, user, review, "renter")
    elif await user.organization == await order.equipment.organization:
        review = await create_or_update_review(order, user, review, "owner")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to create review")

    return review


# TODO: "feedback" instead of "renter"
@router.post("/renter/{order_id}/", status_code=status.HTTP_201_CREATED)
async def create_renter_review(
    order_id: int, feedback: FeedbackCreateSchema, user: User = Depends(get_current_active_user)
):
    """Create renter review."""
    if not feedback.form_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Form data is required")
    order = await get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    await create_nps_csi_feedback(order, user, feedback.form_data)
    log.info(f"Create renter feedback for order {order_id}")
    return {"detail": "Feedback created"}


@router.get("/nps/", status_code=status.HTTP_200_OK)
async def get_nps():
    """Get NPS score."""
    return {"nps": await compute_nps()}


@router.get("/csi/", status_code=status.HTTP_200_OK)
async def get_csi():
    """Get CSI score."""
    return {"csi": str(await compute_csi())}
