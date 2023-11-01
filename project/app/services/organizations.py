import logging

from app.schemas.organizations import OrganizationCreateSchema

log = logging.getLogger("uvicorn")


def extract_organization_data_from_dadata_response(dadata_response: dict) -> OrganizationCreateSchema:
    result = dadata_response["data"]
    response = OrganizationCreateSchema(
        short_name=result["name"]["short_with_opf"],
        full_name=result["name"]["full_with_opf"],
        ogrn=result["ogrn"],
        inn=result["inn"],
        kpp=result.get("kpp"),
        registration_date=result["state"]["registration_date"],
        # authorized_capital_k_rubles=result["capital"]["value"],
        legal_address=result["address"]["value"],
        manager_name=result.get("management", {}).get("name"),
        main_activity=result["okved"],
    )
    return response
