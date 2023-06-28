import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.services.auth import get_current_active_user
from app.services.organizations import get_organization_data_by_code
from app.schemas.users import UserSchema
from app.schemas.organizations import OrganizationSchema
from app.crud.organizations import create_organization, get_organization_by_inn


log = logging.getLogger("uvicorn")

router = APIRouter()


# @router.get("/me/", response_model=OrganizationSchema)
# async def read_organization_me(current_user: Annotated[UserSchema, Depends(get_current_active_user)]):
#     if current_user.organization is None:
#         raise HTTPException(status_code=404, detail="Organization not found")
#     return current_user.organization


@router.get("/{inn}/", response_model=OrganizationSchema)
async def read_organization(inn: str):
    organization = await get_organization_by_inn(inn)
    return organization


@router.post("/create/", response_model=str)
async def create_organization_handler(inn: str):
    organization_data = await get_organization_data_by_code(inn)
    organization_inn = await create_organization(organization_data)
    return organization_inn
