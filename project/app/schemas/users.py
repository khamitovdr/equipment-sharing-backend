from pydantic import BaseModel, EmailStr
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app.schemas import _init_models
from app.models.users import User


class UserBaseSchema(BaseModel):
    email: EmailStr
    phone: str
    full_name: str
    is_owner: bool = False


class UserCreateSchema(UserBaseSchema):
    password: str
    organization_inn: str or None = None


class UserUpdateSchema(BaseModel):
    is_owner: bool or None = None
    phone: str or None = None
    full_name: str or None = None
    password: str or None = None
    new_password: str or None = None
    organization_inn: str or None = None


# class UserSchema(UserBaseSchema):
#     disabled: bool

#     class Config:
#         orm_mode = True


# class UserListSchema(UserSchema):
#     pass


# "name" argument is critical for correct work of pydantic_model_creator! See https://github.com/tortoise/tortoise-orm/issues/647 
UserSchema = pydantic_model_creator(User, name="UserSchema")
UserListSchema = pydantic_queryset_creator(User)
