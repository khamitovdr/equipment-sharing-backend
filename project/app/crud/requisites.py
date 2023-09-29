import logging

from app.models.requisites import Requisites
from app.schemas.requisites import RequisitesUpdateSchema

log = logging.getLogger("uvicorn")


async def _update_requisites(requisites: Requisites, requisites_schema: RequisitesUpdateSchema) -> Requisites:
    log.info(f"Updating requisites with id {requisites.id} in DB...")
    bank_data = requisites_schema.dadata_response["data"]
    requisites.payment_account = requisites_schema.payment_account
    requisites.bank_bic = bank_data["bic"]
    requisites.bank_inn = bank_data["inn"]
    requisites.bank_name = bank_data["name"]["payment"]

    await requisites.save()
    return requisites
