import logging

from app.models.organizations import Organization
from app.models.users import User
from app.models.requisites import Requisites
from app.schemas.users import UserCreateSchema, UserUpdateSchema
from app.schemas.requisites import RequisitesUpdateSchema
from app.crud.requisites import _update_requisites

log = logging.getLogger("uvicorn")


async def get_user_by_email(email: str) -> User | None:
    return await User.filter(email=email).first().prefetch_related("requisites")


async def get_user_by_id(user_id: int) -> User | None:
    return await User.get_or_none(id=user_id).prefetch_related("requisites")


async def create_user(
    user_schema: UserCreateSchema, organization: Organization = None
) -> User:  # Refactor! get_or_create organization inside!
    user_dict = user_schema.dict()
    user_dict["hashed_password"] = user_dict.pop("password")
    new_user = User(**user_dict)
    if organization:
        new_user.organization = organization
    await new_user.save()
    return new_user


async def update_user(
    user: User, user_schema: UserUpdateSchema, organization: Organization = None
) -> User:  # Refactor! get_or_create organization inside!
    user_dict = user_schema.dict(exclude_unset=True)
    if user_dict.get("password"):
        user_dict["hashed_password"] = user_dict.pop("password")
    await user.update_from_dict(user_dict)
    if organization:
        user.organization = organization
        user.is_verified_organization_member = False
    await user.save()
    return user


async def verify_user_organization(user: User) -> User:
    user.is_verified_organization_member = True
    await user.save()
    return user


async def get_users(offset: int = 0, limit: int = 40) -> list[User]:
    return await User.all().order_by("-created_at").offset(offset).limit(limit)  # .prefetch_related("organization")


async def update_user_requisites(user: User, requisites_schema: RequisitesUpdateSchema) -> Requisites:
    log.info(f"Adding requisites to user with email {user.email} in DB...")
    requisites = user.requisites
    if requisites is None:
        requisites = Requisites(user=user)

    return await _update_requisites(requisites, requisites_schema)
