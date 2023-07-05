import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.services.auth import get_current_active_user
from app.services.organizations import get_organization_data_by_code
from app.models.users import User
from app.schemas.organizations import OrganizationSchema
from app.crud.organizations import create_organization, get_organization_by_inn


log = logging.getLogger("uvicorn")

router = APIRouter()


@router.get("/my-organization/", response_model=OrganizationSchema)
async def read_organization_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    await current_user.fetch_related("organization")
    if current_user.organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    organization = current_user.organization
    await organization.fetch_related("main_activity")
    return organization


@router.get("/{inn}/", response_model=OrganizationSchema)
async def read_organization(inn: str):
    organization = await get_organization_by_inn(inn)
    return organization


@router.post("/create/", response_model=OrganizationSchema)
async def create_organization_handler(inn: str):
    organization_data = await get_organization_data_by_code(inn)
    organization = await create_organization(organization_data)
    return organization
