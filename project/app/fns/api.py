import logging

from dadata import DadataAsync
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import Settings, get_settings
from app.fns.pydantic import DadataResponseSchema


log = logging.getLogger("uvicorn")

router = APIRouter()


@router.post("/get-data-by-code/{query}/", response_model=DadataResponseSchema)
async def get_data_by_code(query: str, settings: Settings = Depends(get_settings)):
    async with DadataAsync(settings.dadata_token) as dadata:
        result = await dadata.find_by_id("party", query, status="ACTIVE", count=1)
        
    print(result)
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
    )
    return response
