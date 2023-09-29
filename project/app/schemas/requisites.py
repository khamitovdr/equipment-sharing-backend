from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from app import _init_models  # noqa: F401
from app.models.requisites import Requisites


class RequisitesUpdateSchema(BaseModel):
    payment_account: str
    dadata_response: dict


RequisitesSchema = pydantic_model_creator(Requisites, name="RequisitesSchema")
