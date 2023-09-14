from datetime import date
from typing import Any

from pydantic import BaseModel, Json
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app import _init_models  # noqa: F401
from app.models.organizations import Organization


class DadataResponseSchema(BaseModel):
    short_name: str
    full_name: str
    ogrn: str
    inn: str
    kpp: str
    registration_date: date
    # authorized_capital_k_rubles: int
    legal_address: str
    manager_name: str
    main_activity: str


class RequisitesUpdateSchema(BaseModel):
    dadata_response: Json[Any]


OrganizationSchema = pydantic_model_creator(Organization, name="OrganizationSchema")
OrganizationListSchema = pydantic_queryset_creator(
    Organization, exclude=("ogrn", "kpp", "authorized_capital_k_rubles")
)
