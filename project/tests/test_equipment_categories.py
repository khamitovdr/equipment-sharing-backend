import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.equipment import EquipmentCategory


@pytest.mark.anyio
async def test_get_equipment_categories(client: AsyncClient, verified_equipment_categories_in_db: list[EquipmentCategory]):
    # Given

    # When
    response = await client.get("/equipment/categories/")

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(verified_equipment_categories_in_db)


@pytest.mark.anyio
async def test_get_equipment_categories_not_verified(client: AsyncClient, not_verified_equipment_categories_in_db: list[EquipmentCategory]):
    # Given

    # When
    response = await client.get("/equipment/categories/")

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


@pytest.mark.anyio
async def test_create_equipment_category_not_verified_organization(
    authorized_not_verified_owner_client: AsyncClient,
):
    # Given
    data = {"name": "Test Category"}

    # When
    response = await authorized_not_verified_owner_client.post(
        "/equipment/categories/", params=data
    )

    # Then
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_create_equipment_category(
    authorized_owner_client: AsyncClient,
):
    # Given
    data = {"name": "Test Category"}

    # When
    response = await authorized_owner_client.post(
        "/equipment/categories/", params=data
    )

    # Then
    print(response.json())
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == data["name"]


@pytest.mark.anyio
@pytest.mark.skip(reason="Works only if there are equipment in this category")
async def test_get_own_organization_equipment_category(
    authorized_owner_client: AsyncClient,
    organizations_equipment_category_in_db: EquipmentCategory,
):
    # Given
    query = {
        "organization_inn": organizations_equipment_category_in_db.added_by.organization.inn
    }
    print(query)

    # When
    response = await authorized_owner_client.get(
        "/equipment/categories/",
        params=query,
    )
    print(response.url)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == organizations_equipment_category_in_db.name
