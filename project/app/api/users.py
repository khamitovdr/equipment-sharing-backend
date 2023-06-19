import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.services.auth import get_current_active_user, create_new_user
from app.schemas.users import UserSchema, UserCreateSchema


log = logging.getLogger("uvicorn")

router = APIRouter()


@router.get("/me/", response_model=UserSchema)
async def read_users_me(current_user: Annotated[UserSchema, Depends(get_current_active_user)]):
    return current_user


@router.post("/create/", response_model=int)
async def create_user(user: UserCreateSchema):
    user_id = await create_new_user(user)
    return user_id


# @router.get("/mock/")
# async def mock_users():
    

#     fake_users_db = {
#         "johndoe": {
#             "full_name": "John Doe",
#             "email": "johndoe@example.com",
#             "phone": "+79999999999",
#             "hashed_password": get_password_hash("secret"),
#             "disabled": False,
#         },
#         "alice": {
#             "full_name": "Alice Wonderson",
#             "email": "alice@example.com",
#             "phone": "+78888888888",
#             "hashed_password": get_password_hash("secret2"),
#             "disabled": True,
#         },
#     }

#     for user in fake_users_db.values():
#         log.info(user)
#         log.info(await create_user(user))
