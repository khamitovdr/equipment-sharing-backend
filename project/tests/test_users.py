import pytest
from httpx import AsyncClient
from fastapi import status


TEST_USER_DATA = {
        "full_name": "Test User",
        "password": "test_password",
        "phone": "+79999999999",
    }


@pytest.mark.anyio
@pytest.mark.parametrize(
    "new_user_data, status_code",
    [
        (
            {   # Owner
                **TEST_USER_DATA,
                "email": "owner@test.com",
                "is_owner": True,
                "organization_inn": "1234567890",
            },
            status.HTTP_200_OK,
        ),
        (
            {   # Renter
                **TEST_USER_DATA,
                "email": "renter@test.com",
                "is_owner": False,
            },
            status.HTTP_200_OK,
        ),
        (
            {   # Owner without inn
                **TEST_USER_DATA,
                "email": "owner_no_inn@test.com",
                "is_owner": True,
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        (
            {   # Repeated email
                **TEST_USER_DATA,
                "email": "owner@test.com",
                "is_owner": True,
                "organization_inn": "1234567890",
            },
            status.HTTP_409_CONFLICT,
        ),
    ]
)
async def test_owner_registration_success(client: AsyncClient, new_user_data: dict, status_code: int):
    # Given
    new_user_data

    # When
    response = await client.post("/users/", json=new_user_data)

    # Then
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json()["email"] == new_user_data["email"]



@pytest.mark.anyio
async def test_users_get(client: AsyncClient):
    # Given

    # When
    response = await client.get("/users/")

    # # Then
    assert response.status_code == 200
    assert len(response.json()) == 2
