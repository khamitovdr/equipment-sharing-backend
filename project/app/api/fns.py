import json
import logging

from dadata import DadataAsync
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import Settings, get_settings
from app.schemas.fns import DadataResponseSchema


log = logging.getLogger("uvicorn")

router = APIRouter()


with open("app/data/fns/okveds.json", "r") as f: # needs refactoring
    okveds = json.load(f)


@router.post("/get-data-by-code/{query}/", response_model=DadataResponseSchema) # needs refactoring
async def get_data_by_code(query: str, settings: Settings = Depends(get_settings)):
    async with DadataAsync(settings.dadata_token) as dadata:
        result = await dadata.find_by_id("party", query, status="ACTIVE", count=1)
        
    if not result:
        organization_not_found_exception = HTTPException(
            status_code=status.HTTP_401_,
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
        # main_activity=result["okveds"][0]["name"],
        main_activity=okveds[result["okved"]],
    )
    return response
