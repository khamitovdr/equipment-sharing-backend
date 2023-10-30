import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.crud.organizations import create_organization, get_organization_by_inn
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.organizations import DadataResponseSchema
from app.services.auth import get_current_active_user

log = logging.getLogger("uvicorn")


async def get_or_create_organization_by_inn(dadata_response: dict) -> Organization:
    """Returns organization from DB if exists, otherwise creates it."""
    organization_data = extract_organization_data_from_dadata_response(dadata_response)
    log.info(f"Getting organization by inn {organization_data.inn} from DB...")
    organization = await get_organization_by_inn(organization_data.inn)
    if organization is None:
        log.info(f"Organization with inn {organization_data.inn} not found in DB, creating it...")
        organization = await create_organization(organization_data)
    return organization


def extract_organization_data_from_dadata_response(dadata_response: dict) -> DadataResponseSchema:
    result = dadata_response["data"]
    response = DadataResponseSchema(
        short_name=result["name"]["short_with_opf"],
        full_name=result["name"]["full_with_opf"],
        ogrn=result["ogrn"],
        inn=result["inn"],
        kpp=result.get("kpp"),
        registration_date=result["state"]["registration_date"],
        # authorized_capital_k_rubles=result["capital"]["value"],
        legal_address=result["address"]["value"],
        manager_name=result.get("management", {}).get("name"),
        main_activity=result["okved"],
    )
    return response


async def get_organization_data_by_code(query: str) -> DadataResponseSchema:
    """Returns organization data by code from DaData API."""
    log.info(f"Getting organization data by code {query} from mock DaData API...")
    log.info(f"Organization data by code {query} from mock DaData API received successfully")
    return DadataResponseSchema(
        short_name=f"mock_short_name_{query}",
        full_name=f"mock_name_{query}",
        ogrn=f"mock_ogrn_{query}",
        inn=f"{query}",
        kpp=f"mock_kpp_{query}",
        registration_date="0000000000000",
        legal_address="mock_legal_address",
        manager_name="mock_manager_name",
        main_activity="01",
    )


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
