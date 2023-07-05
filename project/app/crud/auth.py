import logging

from app.models.users import User
from app.models.organizations import Organization
from app.schemas.users import UserAuthSchema, UserCreateSchema


log = logging.getLogger("uvicorn")


async def get_user_with_password_by_email(email: str) -> UserAuthSchema | None:
    user = await User.filter(email=email).first()
    if user:
        return await UserAuthSchema.from_tortoise_orm(user)
    return None


async def get_user_by_email(email: str) -> User | None:
    user = await User.filter(email=email).first()
    if user:
        return user
    return None


async def create_user(user_schema: UserCreateSchema, organization: Organization = None) -> User:
    user_dict = user_schema.dict()
    user_dict["hashed_password"] = user_dict.pop("password")
    new_user = User(**user_dict)
    if organization:
        new_user.organization = organization
    await new_user.save()
    return new_user
