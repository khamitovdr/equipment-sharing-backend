import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.organizations import get_organization_by_inn, update_organization_requisites, get_current_verified_organization, get_or_create_organization, update_organization_contacts, update_organization_contacts_by_member
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.organizations import OrganizationSchema, OrganizationContactsUpdateSchema
from app.schemas.requisites import RequisitesUpdateSchema, RequisitesSchema
from app.services.auth import get_current_active_user

log = logging.getLogger("uvicorn")

router = APIRouter()


@router.get("/my-organization/", response_model=OrganizationSchema)
async def read_organization_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Get current user organization"""
    await current_user.fetch_related("organization__requisites")
    if current_user.organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return current_user.organization


@router.post("/", response_model=OrganizationSchema)
async def get_or_create_organization_(dadata_response: dict):
    """Get or create organization by INN"""
    organization = await get_or_create_organization(dadata_response)
    return organization


@router.get("/{inn}/", response_model=OrganizationSchema)
async def read_organization(inn: str):
    """Get organization by INN"""
    organization = await get_organization_by_inn(inn)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return organization


@router.put("/requisites/", status_code=status.HTTP_202_ACCEPTED, response_model=RequisitesSchema)
async def update_organization_requisites_(
    requisites_schema: RequisitesUpdateSchema,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Update organization requisites"""
    requisites = await update_organization_requisites(organization, requisites_schema)
    return requisites


@router.put("/{inn}/contacts/", status_code=status.HTTP_202_ACCEPTED, response_model=OrganizationSchema)
async def update_organization_contacts_(
    inn: str,
    contacts_schema: OrganizationContactsUpdateSchema,
):
    """Update organization contacts"""
    organization = await get_organization_by_inn(inn)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    organization = await update_organization_contacts(organization, contacts_schema)
    return organization


# async def update_organization_contacts_by_member_
@router.put("/contacts/", status_code=status.HTTP_202_ACCEPTED, response_model=OrganizationSchema)
async def update_organization_contacts_by_member_(
    contacts_schema: OrganizationContactsUpdateSchema,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Update organization contacts by member"""
    organization = await update_organization_contacts_by_member(organization, contacts_schema)
    return organization
