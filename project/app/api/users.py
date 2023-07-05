import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.services.auth import get_current_active_user, create_new_user
from app.services.organizations import get_or_create_organization_by_inn
from app.schemas.users import UserSchema, UserCreateSchema
from app.models.users import User


log = logging.getLogger("uvicorn")

router = APIRouter()


@router.get("/me/", response_model=UserSchema)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    await current_user.fetch_related("organization")
    return current_user


@router.post("/create/", response_model=int)
async def create_user(user_schema: UserCreateSchema):
    if user_schema.organization_inn:
        organization = await get_or_create_organization_by_inn(user_schema.organization_inn)
        user = await create_new_user(user_schema, organization)
    else:
        user = await create_new_user(user_schema)
    return user.id
