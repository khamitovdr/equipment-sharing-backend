import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.organizations import get_organization_by_inn, update_organization_requisites
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.organizations import OrganizationSchema
from app.schemas.requisites import RequisitesUpdateSchema, RequisitesSchema
from app.services.auth import get_current_active_user
from app.services.organizations import get_current_verified_organization

log = logging.getLogger("uvicorn")

router = APIRouter()


@router.get("/my-organization/", response_model=OrganizationSchema)
async def read_organization_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Get current user organization"""
    await current_user.fetch_related("organization__requisites")
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


@router.put("/requisites/", status_code=status.HTTP_202_ACCEPTED, response_model=RequisitesSchema)
async def update_organization_requisites_(
    requisites_schema: RequisitesUpdateSchema,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Update organization requisites"""
    requisites = await update_organization_requisites(organization, requisites_schema)
    return requisites
