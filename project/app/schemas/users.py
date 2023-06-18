from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models.users import User


# "name" argument is critical for correct work of pydantic_model_creator! See https://github.com/tortoise/tortoise-orm/issues/647 
UserAuthSchema: BaseModel = pydantic_model_creator(User, name="UserAuthSchema")
UserSchema: BaseModel = pydantic_model_creator(User, name="UserSchema", exclude=["hashed_password", "id"])
