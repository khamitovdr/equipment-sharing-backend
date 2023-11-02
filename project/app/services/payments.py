import uuid

from yookassa import Configuration, Payment

from app.config import get_settings

Configuration.account_id = get_settings().yookassa_shop_id
Configuration.secret_key = get_settings().yookassa_secret_key


def create_payment_link(amount: float, description: str, return_url: str) -> (str, str):
    payment = Payment.create(
        {
            "amount": {"value": amount, "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": description,
        },
        uuid.uuid4(),
    )
    return payment.id, payment.status, payment.confirmation.confirmation_url


def check_payment_succeed(payment_id: str) -> bool:
    payment = Payment.find_one(payment_id)
    return payment.status == "succeeded"
