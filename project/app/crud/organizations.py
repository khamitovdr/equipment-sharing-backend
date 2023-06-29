import logging

from app.models.organizations import Organization, Activity
from app.schemas.organizations import DadataResponseSchema, OrganizationSchema


log = logging.getLogger("uvicorn")


async def create_activities(okveds: dict):
    """Creates activities in DB."""
    activities = [Activity(code=code, description=description) for code, description in okveds.items()]
    await Activity.bulk_create(activities)


async def create_organization(organization_data: DadataResponseSchema) -> Organization:
    log.info(f"Creating organization with inn {organization_data.inn} in DB...")
    activity = await Activity.get_or_none(code=organization_data.main_activity)
    organization = Organization(
        inn=organization_data.inn,
        short_name=organization_data.short_name,
        full_name=organization_data.full_name,
        ogrn=organization_data.ogrn,
        kpp=organization_data.kpp,
        registration_date=organization_data.registration_date,
        legal_address=organization_data.legal_address,
        manager_name=organization_data.manager_name,
        main_activity=activity,
    )
    await organization.save()
    return organization


async def get_organization_by_inn(inn: str) -> Organization or None:
    organization = await Organization.get_or_none(inn=inn)
    if organization is not None:
        await organization.fetch_related('main_activity')
        return organization
