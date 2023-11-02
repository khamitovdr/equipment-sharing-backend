import hashlib
import re

import aiohttp
from fastapi import UploadFile

from app.config import get_settings
from app.models.orders import Order


def get_user_secret(order_id: int, role: str) -> str:
    assert role in ["owner", "renter"]
    return hashlib.sha1(f"{order_id}_{role}".encode("utf-8")).hexdigest()


def proscribe_role_and_chat_credentials(order: Order, role: str) -> Order:
    interlocutor_role = "owner" if role == "renter" else "renter"
    order.role_and_chat_credentials = {
        "role": role,
        "chat_credentials": {
            "username": f"order-{order.id}_{role}",
            "user_secret": get_user_secret(order.id, role),
            "interlocutor_username": f"order-{order.id}_{interlocutor_role}",
        },
    }
    return order


async def verify_e_signature(e_sign_data: UploadFile, order: Order, role: str) -> bool:
    assert role in ["owner", "renter"]

    e_sign_template = re.compile(r"-+BEGIN CMS-+.+-+END CMS-+", re.MULTILINE | re.DOTALL)
    e_sign_data_content = await e_sign_data.read()
    e_sign_data_content = e_sign_data_content.decode("utf-8")

    if not e_sign_template.match(e_sign_data_content):
        return False
    return True


async def create_chatengine_users(order: Order) -> None:
    renter = await order.requester
    organization = await order.equipment.organization

    chat_engine_url = "https://api.chatengine.io/users/"
    users_data = {
        "renter": {
            "username": f"order-{order.id}_renter",
            "secret": get_user_secret(order.id, "renter"),
            "email": renter.email,
            "first_name": renter.name,
            "last_name": renter.surname,
        },
        "owner": {
            "username": f"order-{order.id}_owner",
            "secret": get_user_secret(order.id, "owner"),
            "email": organization.contact_email,
            "first_name": organization.contact_employee_name
            if organization.contact_employee_name
            else "Представитель компании",
            "last_name": organization.contact_employee_surname,
        },
    }
    headers = {
        "PRIVATE-KEY": get_settings().chat_engine_secret_key,
    }

    async with aiohttp.ClientSession() as session:
        for user in users_data.values():
            async with session.post(chat_engine_url, json=user, headers=headers) as res:
                user = await res.json()
                print(user)
