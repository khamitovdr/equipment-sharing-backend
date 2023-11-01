from datetime import date

from pydantic import BaseModel, EmailStr
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app import _init_models  # noqa: F401
from app.models.organizations import Organization


class OrganizationCreateSchema(BaseModel):
    short_name: str or None = None
    full_name: str or None = None
    ogrn: str or None = None
    inn: str
    kpp: str or None = None
    registration_date: date or None = None
    # authorized_capital_k_rubles: int or None = None
    legal_address: str or None = None
    manager_name: str or None = None
    main_activity: str or None = None


class OrganizationContactsUpdateSchema(BaseModel):
    contact_phone: str
    contact_email: EmailStr
    contact_employee_name: str
    contact_employee_middle_name: str or None = None
    contact_employee_surname: str or None = None


OrganizationSchema = pydantic_model_creator(Organization, name="OrganizationSchema")
OrganizationListSchema = pydantic_queryset_creator(
    Organization, exclude=("ogrn", "kpp", "authorized_capital_k_rubles", "requisites")
)
