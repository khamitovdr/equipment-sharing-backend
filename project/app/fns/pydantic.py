from datetime import date

from pydantic import BaseModel


class DadataResponseSchema(BaseModel):
    short_name: str
    full_name: str
    ogrn: str
    inn: str
    kpp: str
    registration_date: date
    # capital: int
    legal_address: str
    manager_name: str
    # main_activity: str