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
            "email": renter.email or "",
            "first_name": renter.name or "",
            "last_name": renter.surname or "",
        },
        "owner": {
            "username": f"order-{order.id}_owner",
            "secret": get_user_secret(order.id, "owner"),
            "email": organization.contact_email or "",
            "first_name": organization.contact_employee_name or "Представитель компании",
            "last_name": organization.contact_employee_surname or "",
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


async def get_or_create_chat(order: Order) -> str:
    url = "https://api.chatengine.io/chats/"
    
    headers = {
      'Project-ID': get_settings().chat_engine_project_id,
      'User-Name': f"order-{order.id}_owner",
      'User-Secret': get_user_secret(order.id, "owner"),
    }
    payload = {
        "usernames": [f"order-{order.id}_renter"],
        "title": f"Заказ №{order.id}",
        "is_direct_chat": True,
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.put(url, json=payload, headers=headers) as res:
            chat = await res.json()
            print(chat)

    return chat['id']


async def delete_all_chatengine_users():
    users_url = "https://api.chatengine.io/users/"

    headers = {
      'PRIVATE-KEY': get_settings().chat_engine_secret_key,
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(users_url, headers=headers) as res:
            users = await res.json()


        for user in users:
            user_url = f"https://api.chatengine.io/users/{user['id']}/"
            async with session.delete(user_url, headers=headers) as res:
                print(f"Deleting user {user['username']}:", res.status)
