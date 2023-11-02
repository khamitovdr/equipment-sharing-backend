import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.crud.requisites import _update_requisites
from app.models.organizations import Organization
from app.models.requisites import Requisites
from app.models.users import User
from app.schemas.organizations import (
    OrganizationContactsUpdateSchema,
    OrganizationCreateSchema,
)
from app.schemas.requisites import RequisitesUpdateSchema
from app.services.auth import get_current_active_user
from app.services.organizations import extract_organization_data_from_dadata_response

log = logging.getLogger("uvicorn")


async def create_organization(organization_create_schema: OrganizationCreateSchema) -> Organization:
    log.info(f"Creating organization with inn {organization_create_schema.inn} in DB...")
    organization = Organization(**organization_create_schema.dict())
    await organization.save()
    return organization


async def get_organization_by_inn(inn: str) -> Organization or None:
    return await Organization.get_or_none(inn=inn)


async def get_or_create_organization(dadata_response: dict) -> Organization:
    """Returns organization from DB if exists, otherwise creates it."""
    organization_data = extract_organization_data_from_dadata_response(dadata_response)
    log.info(f"Getting organization by inn {organization_data.inn} from DB...")
    organization = await get_organization_by_inn(organization_data.inn)
    if organization is None:
        log.info(f"Organization with inn {organization_data.inn} not found in DB, creating it...")
        organization = await create_organization(organization_data)
    return organization


async def get_current_organization(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Organization:
    """Returns current user's organization"""
    log.info("Getting current user's organization...")
    organization = await current_user.organization
    if organization is None:
        log.error("Current user doesn't have an organization")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Current user doesn't have an organization",
        )
    log.info(f"Current user's organization {organization.inn} received successfully")
    return organization


async def get_current_verified_organization(
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
) -> Organization:
    """Returns current user's organization if it's verified"""
    if not current_user.is_verified_organization_member:
        log.error("Current user's organization is not verified")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Current user's organization is not verified",
        )
    return organization


async def update_organization_requisites(
    organization: Organization, requisites_schema: RequisitesUpdateSchema
) -> Requisites:
    log.info(f"Adding requisites to organization with inn {organization.inn} in DB...")
    requisites = await organization.requisites
    if requisites is None:
        requisites = Requisites(organization=organization)

    return await _update_requisites(requisites, requisites_schema)


async def update_organization_contacts(
    organization: Organization, contacts_schema: OrganizationContactsUpdateSchema
) -> Organization:
    log.info(f"Updating contacts of organization with inn {organization.inn} in DB...")
    if await organization.users.filter(is_verified_organization_member=True).count() > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization contacts can't be updated if there are verified members",
        )
    organization.update_from_dict(contacts_schema.dict())
    await organization.save()
    return organization


async def update_organization_contacts_by_member(
    organization: Organization,
    contacts_schema: OrganizationContactsUpdateSchema,
) -> Organization:
    log.info(f"Updating contacts of organization with inn {organization.inn} in DB...")
    organization.update_from_dict(contacts_schema.dict())
    await organization.save()
    return organization
