from pydantic import BaseModel, EmailStr
# from pydantic_extra_types.phone_numbers import PhoneNumber # NotImplemented
from tortoise.contrib.pydantic import pydantic_model_creator

from app.schemas import _init_models
from app.models.users import User


class UserBaseSchema(BaseModel):
    email: EmailStr
    phone: str
    full_name: str


class UserCreateSchema(UserBaseSchema):
    password: str
    organization_inn: str or None = None


class UserSchema(UserBaseSchema):
    disabled: bool

    class Config:
        orm_mode = True


# "name" argument is critical for correct work of pydantic_model_creator! See https://github.com/tortoise/tortoise-orm/issues/647 
UserAuthSchema: BaseModel = pydantic_model_creator(User, name="UserAuthSchema")
# UserSchema: BaseModel = pydantic_model_creator(User, name="UserSchema", exclude=["hashed_password", "id"])
