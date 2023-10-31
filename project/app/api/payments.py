from fastapi import APIRouter, status

from app.crud.orders import confirm_payment_by_id

router = APIRouter()


@router.post("/callback/", status_code=status.HTTP_202_ACCEPTED)
async def payment_callback_(payload: dict):
    """Payment callback"""
    if payload["event"] == "payment.succeeded":
        payment_id = payload["object"]["id"]
        await confirm_payment_by_id(payment_id, payload)
