import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.crud.organizations import get_organization_by_inn
from app.models.users import User
from app.schemas.organizations import OrganizationSchema
from app.services.auth import get_current_active_user

log = logging.getLogger("uvicorn")

router = APIRouter()


@router.get("/my-organization/", response_model=OrganizationSchema)
async def read_organization_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Get current user organization"""
    await current_user.fetch_related("organization")
    if current_user.organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return current_user.organization


@router.get("/{inn}/", response_model=OrganizationSchema)
async def read_organization(inn: str):
    """Get organization by INN"""
    organization = await get_organization_by_inn(inn)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization
