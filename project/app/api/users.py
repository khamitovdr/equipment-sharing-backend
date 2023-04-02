import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.auth.auth import get_current_active_user
from app.models.tortoise import UserInDBSchema

log = logging.getLogger("uvicorn")

router = APIRouter()


@router.get("/me/", response_model=UserInDBSchema)
async def read_users_me(current_user: Annotated[UserInDBSchema, Depends(get_current_active_user)]):
    return current_user


@router.get("/me/items/")
async def read_own_items(current_user: Annotated[UserInDBSchema, Depends(get_current_active_user)]):
    return [{"item_id": "Foo", "owner": current_user.email}]


@router.get("/mock/")
async def mock_users():
    from app.auth.auth import get_password_hash
    from app.auth.crud import create_user

    fake_users_db = {
        "johndoe": {
            "full_name": "John Doe",
            "email": "johndoe@example.com",
            "hashed_password": get_password_hash("secret"),
            "disabled": False,
        },
        "alice": {
            "full_name": "Alice Wonderson",
            "email": "alice@example.com",
            "hashed_password": get_password_hash("secret2"),
            "disabled": True,
        },
    }

    for user in fake_users_db.values():
        log.info(user)
        log.info(await create_user(user))
