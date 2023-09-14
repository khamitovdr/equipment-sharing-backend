import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.reviews import ReviewCreateSchema


log = logging.getLogger("uvicorn")


router = APIRouter()


@router.post("/renter/{order_id}/", status_code=status.HTTP_201_CREATED)
async def create_renter_review(order_id: int, review: ReviewCreateSchema):
    """Create renter review."""
    if not review.form_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Form data is required")
    log.info(f"Create renter review for order {order_id}")
    return {"detail": "Review created"}
