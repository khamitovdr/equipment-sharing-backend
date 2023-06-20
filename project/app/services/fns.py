import os
import json
import logging

from dadata import DadataAsync
from fastapi import status, HTTPException

from app.schemas.fns import DadataResponseSchema
from app.crud.organizations import create_activities


DADATA_TOKEN = os.getenv("DADATA_TOKEN")

async def get_organization_data_by_code(query: str) -> DadataResponseSchema:
    """Returns organization data by code from DaData API."""
    async with DadataAsync(DADATA_TOKEN) as dadata:
        result = await dadata.find_by_id("party", query, status="ACTIVE", count=1)
        
    if not result:
        organization_not_found_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
        raise organization_not_found_exception
    
    result = result[0]["data"]
    response = DadataResponseSchema(
        short_name=result["name"]["short_with_opf"],
        full_name=result["name"]["full_with_opf"],
        ogrn=result["ogrn"],
        inn=result["inn"],
        kpp=result["kpp"],
        registration_date=result["state"]["registration_date"],
        # capital=result["capital"]["value"],
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
