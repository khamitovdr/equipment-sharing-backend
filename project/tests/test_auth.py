from asyncio import sleep

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.users import User
from tests.conftest import TEST_USER_DATA

LOGIN_DATA = {
    "username": TEST_USER_DATA["email"],
    "password": TEST_USER_DATA["password"],
}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "login_data, status_code",
    [
        (
            # Correct login
            LOGIN_DATA,
            status.HTTP_200_OK,
        ),
        (
            # Incorrect password
            {
                **LOGIN_DATA,
                "password": "wrong_password",
            },
            status.HTTP_401_UNAUTHORIZED,
        ),
        (
            # Incorrect email
            {
                **LOGIN_DATA,
                "username": "wrong_email@test.com",
            },
            status.HTTP_401_UNAUTHORIZED,
        ),
    ],
)
async def test_user_login(client: AsyncClient, user_in_db: User, login_data: dict, status_code: int):
    # Given

    # When
    response = await client.post("/login/", data=login_data)

    # Then
    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
    else:
        assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.anyio
async def test_auth_token_expired(client_instant_token_expired: AsyncClient, user_in_db: User):
    # Given
    login_response = await client_instant_token_expired.post("/login/", data=LOGIN_DATA)
    access_token = login_response.json()["access_token"]
    await sleep(1)

    # When
    response = await client_instant_token_expired.get(
        "/users/me/", headers={"Authorization": f"Bearer {access_token}"}
    )

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Could not validate credentials"
