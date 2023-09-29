import re

from pydantic import BaseModel, EmailStr, validator
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app import _init_models  # noqa: F401
from app.models.users import User


class UserCreateSchema(BaseModel):
    is_owner: bool = False
    email: EmailStr
    phone: str
    full_name: str
    password: str
    organization_inn: str or None = None

    @validator("phone")
    def check_phone(cls, v):
        phone = re.compile(r"^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$")
        if not phone.match(v):
            raise ValueError("Invalid phone number")
        return v

    @validator("password")
    def check_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search("[a-zа-я]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search("[A-ZА-Я]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search("[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v

    @validator("organization_inn", always=True)
    def check_organization_inn(cls, v, values):
        if values.get("is_owner") and not v:
            raise ValueError("Organization INN is required for owners")
        if v and not v.isdigit():
            raise ValueError("Organization INN must contain only digits")
        if v and len(v) not in (10, 12):
            raise ValueError("Organization INN must contain 10 or 12 digits")
        return v


class UserUpdateSchema(UserCreateSchema):
    is_owner: bool or None = None
    email: EmailStr or None = None
    phone: str or None = None
    full_name: str or None = None
    password: str or None = None
    new_password: str or None = None

    @validator("password")
    def check_password(cls, v):
        return v

    @validator("new_password", always=True)
    def check_new_password(cls, v, values):
        if values.get("password") and not v:
            raise ValueError("New password is required")
        if v is None:
            return v
        return super().check_password(v)


# "name" argument is critical for correct work of pydantic_model_creator!
# See https://github.com/tortoise/tortoise-orm/issues/647
UserSchema = pydantic_model_creator(User, name="UserSchema")
UserListSchema = pydantic_queryset_creator(User, exclude=("requisites",))
