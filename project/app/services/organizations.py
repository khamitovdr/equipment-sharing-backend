import logging
from typing import Annotated

# from dadata import DadataAsync
from fastapi import Depends, HTTPException, status

from app.config import get_settings
from app.crud.organizations import create_organization, get_organization_by_inn
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.organizations import DadataResponseSchema
from app.services.auth import get_current_active_user

log = logging.getLogger("uvicorn")


dadata_token = get_settings().dadata_token


async def get_or_create_organization_by_inn(inn: str) -> Organization:
    """Returns organization from DB if exists, otherwise creates it."""
    log.info(f"Getting organization by inn {inn} from DB...")
    organization = await get_organization_by_inn(inn)
    if organization is None:
        log.info(f"Organization with inn {inn} not found in DB, creating it...")
        organization_data = await get_organization_data_by_code(inn)
        organization = await create_organization(organization_data)
    return organization


# async def get_organization_data_by_code(query: str) -> DadataResponseSchema:
#     """Returns organization data by code from DaData API."""
#     log.info(f"Getting organization data by code {query} from DaData API...")
#     async with DadataAsync(dadata_token) as dadata:
#         result = await dadata.find_by_id("party", query, status="ACTIVE", count=1)

#     if not result:
#         log.error(f"Organization not found by code {query}")
#         organization_not_found_exception = HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Organization not found",
#         )
#         raise organization_not_found_exception

#     result = result[0]["data"]
#     log.info(f"Organization data by code {query} from DaData API received successfully")
#     response = DadataResponseSchema(
#         short_name=result["name"]["short_with_opf"],
#         full_name=result["name"]["full_with_opf"],
#         ogrn=result["ogrn"],
#         inn=result["inn"],
#         kpp=result["kpp"],
#         registration_date=result["state"]["registration_date"],
#         # authorized_capital_k_rubles=result["capital"]["value"],
#         legal_address=result["address"]["value"],
#         manager_name=result["management"]["name"],
#         # main_activity=okveds[result["okved"]],
#         main_activity=result["okved"],
#     )
#     return response


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
    if current_user.organization is None:
        log.error("Current user doesn't have an organization")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Current user doesn't have an organization",
        )
    organization = await current_user.organization
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
