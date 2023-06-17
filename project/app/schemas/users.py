from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models.users import User


# Порядок важен! Это супер странно! Если сперва вызвать строку UserSchema,
# то исключенные поля будут исключены и у UserInDBSchema...
UserInDBSchema: BaseModel = pydantic_model_creator(User)
# UserSchema = pydantic_model_creator(User, exclude=["hashed_password", "id"])    # temporary not in use
