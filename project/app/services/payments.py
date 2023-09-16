import uuid

from yookassa import Configuration, Payment

from app.config import get_settings


Configuration.account_id = get_settings().yookassa_shop_id
Configuration.secret_key = get_settings().yookassa_secret_key


def create_payment_link(amount: float, description: str, return_url: str) -> str:
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url
        },
        "capture": True,
        "description": description
    }, uuid.uuid4())
    return payment.confirmation.confirmation_url
