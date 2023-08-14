import pytest
from httpx import AsyncClient
from fastapi import status

from tests.conftest import TEST_USER_DATA, TEST_OWNER_DATA, TEST_RENTER_DATA


@pytest.mark.anyio
@pytest.mark.parametrize(
    "new_user_data, status_code",
    [
        (
            # Owner
            TEST_OWNER_DATA,
            status.HTTP_201_CREATED,
        ),
        (
            # Renter
            TEST_RENTER_DATA,
            status.HTTP_201_CREATED,
        ),
        (
            {   # Owner without inn
                **TEST_USER_DATA,
                "is_owner": True,
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        (
            {   # Invalid email
                **TEST_USER_DATA,
                "email": "user@test",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        (
            {   # Invalid phone
                **TEST_USER_DATA,
                "phone": "99999999999",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        (
            {   # Invalid password
                **TEST_USER_DATA,
                "password": "password",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
    ]
)
async def test_user_create(client: AsyncClient, new_user_data: dict, status_code: int):
    # Given

    # When
    response = await client.post("/users/", json=new_user_data)

    # Then
    assert response.status_code == status_code
    if status_code == status.HTTP_201_CREATED:
        assert response.json()["email"] == new_user_data["email"]


@pytest.mark.anyio
async def test_email_conflict(client: AsyncClient, user_in_db: dict):
    # Given
    new_user_data = TEST_USER_DATA

    # When
    response = await client.post("/users/", json=new_user_data)

    # Then
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.anyio
async def test_users_get(client: AsyncClient, user_in_db: dict):
    # Given

    # When
    response = await client.get("/users/")

    # # Then
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0] == user_in_db


@pytest.mark.anyio
async def test_user_get_by_id(client: AsyncClient, user_in_db: dict):
    # Given

    # When
    response = await client.get(f"/users/{user_in_db['id']}/")

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user_in_db
