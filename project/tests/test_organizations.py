import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.organizations import Organization
from tests.conftest import TEST_OWNER_DATA


@pytest.mark.anyio
@pytest.mark.parametrize(
    "inn, status_code",
    [
        (  # Existing organization
            "0000000000",
            status.HTTP_200_OK,
        ),
        (  # Non-existing organization
            "0000000001",
            status.HTTP_404_NOT_FOUND,
        ),
    ],
)
async def test_get_organization_by_inn(
    client: AsyncClient, organization_in_db: Organization, inn: str, status_code: int
):
    # Given

    # When
    response = await client.get(f"/organizations/{inn}/")

    # Then
    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert response.json()["inn"] == inn


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user_client, status_code",
    [
        (
            pytest.lazy_fixture("client"),
            status.HTTP_401_UNAUTHORIZED,
        ),
        (
            pytest.lazy_fixture("authorized_user_client"),
            status.HTTP_404_NOT_FOUND,
        ),
        (pytest.lazy_fixture("authorized_owner_client"), status.HTTP_200_OK),
    ],
)
async def test_get_users_organization(user_client: AsyncClient, status_code: int):
    # Given

    # When
    response = await user_client.get("/organizations/my-organization/")

    # Then
    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert response.json()["inn"] == TEST_OWNER_DATA["organization_inn"]
