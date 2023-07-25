import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.services.auth import get_current_active_user, get_password_hash
from app.services.organizations import get_or_create_organization_by_inn
from app.services.auth import authenticate_user, CREDENTIALS_EXCEPTION
from app.schemas.users import UserSchema, UserCreateSchema, UserUpdateSchema, UserListSchema
from app.models.users import User
from app.crud.users import get_user_by_id, create_user, update_user, get_users, get_user_by_email


log = logging.getLogger("uvicorn")

router = APIRouter()


@router.get("/me/", response_model=UserSchema)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''Get current user details'''
    await current_user.fetch_related("organization")
    return current_user


@router.get("/{user_id}/", response_model=UserSchema)
async def read_user(user_id: int):
    '''Get user details by id'''
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserSchema)
async def create_new_user(user_schema: UserCreateSchema):
    '''Create new user'''
    if await get_user_by_email(user_schema.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
    
    user_schema.password = get_password_hash(user_schema.password)
    if user_schema.organization_inn:
        organization = await get_or_create_organization_by_inn(user_schema.organization_inn)
    else:
        organization = None

    user = await create_user(user_schema, organization)
    return user


@router.put("/me/", response_model=UserSchema)
async def update_current_user(user_schema: UserUpdateSchema, current_user: Annotated[User, Depends(get_current_active_user)]):
    '''Update current user'''
    if user_schema.new_password:
        if not await authenticate_user(current_user.email, user_schema.password):
            raise CREDENTIALS_EXCEPTION
        user_schema.password = get_password_hash(user_schema.new_password)
        user_schema.new_password = None

    await current_user.fetch_related("organization")
    if user_schema.organization_inn and (current_user.organization is None or user_schema.organization_inn != current_user.organization.inn):
        organization = await get_or_create_organization_by_inn(user_schema.organization_inn)
    else:
        organization = None

    user = await update_user(current_user, user_schema, organization)
    return user


@router.get("/", response_model=list[UserListSchema])
async def read_users(skip: int = 0, limit: int = 100):
    '''Get list of all users'''
    users = await get_users(skip, limit)
    return users
