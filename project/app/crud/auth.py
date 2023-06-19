import logging

from app.models.users import User
from app.schemas.users import UserAuthSchema, UserSchema, UserCreateSchema


log = logging.getLogger("uvicorn")


async def get_user_with_password_by_email(email: str) -> UserAuthSchema | None:
    user = await User.filter(email=email).first()
    if user:
        return await UserAuthSchema.from_tortoise_orm(user)
    return None


async def get_user_by_email(email: str) -> UserSchema | None:
    user = await User.filter(email=email).first()
    if user:
        return await UserSchema.from_tortoise_orm(user)
    return None


async def create_user(user_schema: UserCreateSchema) -> int:
    new_user = User(
        email=user_schema.email,
        phone=user_schema.phone,
        hashed_password=user_schema.password,
        full_name=user_schema.full_name,
    )
    await new_user.save()
    return new_user.id
