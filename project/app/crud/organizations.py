import logging

from app.models.organizations import Organization
from app.schemas.organizations import DadataResponseSchema

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
