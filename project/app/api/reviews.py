import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.users import User
from app.services.auth import get_current_active_user
from app.schemas.reviews import ReviewCreateSchema
from app.crud.reviews import compute_nps, compute_csi, create_nps_csi_review
from app.crud.orders import get_order_by_id


log = logging.getLogger("uvicorn")


router = APIRouter()


@router.post("/renter/{order_id}/", status_code=status.HTTP_201_CREATED)
async def create_renter_review(order_id: int, review: ReviewCreateSchema, user: User = Depends(get_current_active_user)):
    """Create renter review."""
    if not review.form_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Form data is required")
    order = await get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    await create_nps_csi_review(order, user, review.form_data)
    log.info(f"Create renter review for order {order_id}")
    return {"detail": "Review created"}


@router.get("/nps/", status_code=status.HTTP_200_OK)
async def get_nps():
    """Get NPS score."""
    return {"nps": await compute_nps()}


@router.get("/csi/", status_code=status.HTTP_200_OK)
async def get_csi():
    """Get CSI score."""
    return {"csi": str(await compute_csi())}
