import logging

from app.models.users import User
from app.models.organizations import Organization
from app.schemas.users import UserCreateSchema, UserUpdateSchema


log = logging.getLogger("uvicorn")


async def get_user_by_email(email: str) -> User | None:
    return await User.filter(email=email).first()


async def get_user_by_id(user_id: int) -> User | None:
    return await User.get_or_none(id=user_id)


async def create_user(user_schema: UserCreateSchema, organization: Organization = None) -> User:    # Refactor! get_or_create organization inside!
    user_dict = user_schema.dict()
    user_dict["hashed_password"] = user_dict.pop("password")
    new_user = User(**user_dict)
    if organization:
        new_user.organization = organization
    await new_user.save()
    return new_user


async def update_user(user: User, user_schema: UserUpdateSchema, organization: Organization = None) -> User:    # Refactor! get_or_create organization inside!
    user_dict = user_schema.dict(exclude_unset=True)
    if user_dict.get("password"):
        user_dict["hashed_password"] = user_dict.pop("password")
    await user.update_from_dict(user_dict)
    if organization:
        user.organization = organization
        user.is_verified_organization_member = False
    await user.save()
    return user
