from datetime import date

from pydantic import BaseModel


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


class OrganizationActivitySchema(BaseModel):
    code: str
    description: str

    class Config:
        orm_mode = True


class OrganizationListSchema(BaseModel):
    inn: str
    short_name: str
    full_name: str
    registration_date: date
    legal_address: str
    manager_name: str

    class Config:
        orm_mode = True


class OrganizationSchema(OrganizationListSchema):
    ogrn: str
    kpp: str
    authorized_capital_k_rubles: float | None = None
    main_activity: OrganizationActivitySchema

    class Config:
        orm_mode = True
