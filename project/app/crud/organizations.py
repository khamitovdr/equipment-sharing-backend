import logging

from app.models.organizations import Organization
from app.models.requisites import Requisites
from app.schemas.organizations import DadataResponseSchema
from app.schemas.requisites import RequisitesUpdateSchema
from app.crud.requisites import _update_requisites

log = logging.getLogger("uvicorn")


async def create_organization(organization_data: DadataResponseSchema) -> Organization:
    log.info(f"Creating organization with inn {organization_data.inn} in DB...")
    organization = Organization(
        inn=organization_data.inn,
        short_name=organization_data.short_name,
        full_name=organization_data.full_name,
        ogrn=organization_data.ogrn,
        kpp=organization_data.kpp,
        registration_date=organization_data.registration_date,
        legal_address=organization_data.legal_address,
        manager_name=organization_data.manager_name,
        main_activity=organization_data.main_activity,
    )
    await organization.save()
    return organization


async def get_organization_by_inn(inn: str) -> Organization or None:
    return await Organization.get_or_none(inn=inn)


async def update_organization_requisites(organization: Organization, requisites_schema: RequisitesUpdateSchema) -> Requisites:
    log.info(f"Adding requisites to organization with inn {organization.inn} in DB...")
    requisites = await organization.requisites
    if requisites is None:
        requisites = Requisites(organization=organization)

    return await _update_requisites(requisites, requisites_schema)
