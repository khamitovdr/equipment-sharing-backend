import os
import json
import logging

from dadata import DadataAsync
from fastapi import status, HTTPException

from app.schemas.organizations import DadataResponseSchema
from app.crud.organizations import create_activities, get_organization_by_inn, create_organization
from app.models.organizations import Organization


log = logging.getLogger("uvicorn")


DADATA_TOKEN = os.getenv("DADATA_TOKEN")


async def get_or_create_organization_by_inn(inn: str) -> Organization:
    """Returns organization from DB if exists, otherwise creates it."""
    log.info(f"Getting organization by inn {inn} from DB...")
    organization = await get_organization_by_inn(inn)
    if organization is None:
        log.info(f"Organization with inn {inn} not found in DB, creating it...")
        organization_data = await get_organization_data_by_code(inn)
        organization = await create_organization(organization_data)
    return organization


async def get_organization_data_by_code(query: str) -> DadataResponseSchema:
    """Returns organization data by code from DaData API."""
    log.info(f"Getting organization data by code {query} from DaData API...")
    async with DadataAsync(DADATA_TOKEN) as dadata:
        result = await dadata.find_by_id("party", query, status="ACTIVE", count=1)

    if not result:
        log.error(f"Organization not found by code {query}")
        organization_not_found_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
        raise organization_not_found_exception
    
    result = result[0]["data"]
    log.info(f"Organization data by code {query} from DaData API received successfully")
    response = DadataResponseSchema(
        short_name=result["name"]["short_with_opf"],
        full_name=result["name"]["full_with_opf"],
        ogrn=result["ogrn"],
        inn=result["inn"],
        kpp=result["kpp"],
        registration_date=result["state"]["registration_date"],
        # authorized_capital_k_rubles=result["capital"]["value"],
        legal_address=result["address"]["value"],
        manager_name=result["management"]["name"],
        # main_activity=okveds[result["okved"]],
        main_activity=result["okved"],
    )
    return response


async def init_activities_db_table():
    with open("app/data/fns/okveds.json", "r") as f:
        okveds = json.load(f)
        await create_activities(okveds)
