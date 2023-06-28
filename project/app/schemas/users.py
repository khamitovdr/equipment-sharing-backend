from pydantic import BaseModel, EmailStr
# from pydantic_extra_types.phone_numbers import PhoneNumber # NotImplemented
from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

from app.db import MODELS
from app.models.users import User


class UserCreateSchema(BaseModel):
    email: EmailStr
    phone: str # PhoneNumber
    password: str
    full_name: str
    organization_inn: str or None = None


Tortoise.init_models(MODELS, "models")

# "name" argument is critical for correct work of pydantic_model_creator! See https://github.com/tortoise/tortoise-orm/issues/647 
UserAuthSchema: BaseModel = pydantic_model_creator(User, name="UserAuthSchema")
UserSchema: BaseModel = pydantic_model_creator(User, name="UserSchema", exclude=["hashed_password", "id"])
