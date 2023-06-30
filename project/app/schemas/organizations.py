from datetime import date

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from app.schemas import _init_models
from app.models.organizations import Activity, Organization


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


# ActivitySchema = pydantic_model_creator(Activity, name="ActivitySchema")
OrganizationSchema = pydantic_model_creator(Organization, name="OrganizationSchema", exclude=["users"])
