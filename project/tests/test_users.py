import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.organizations import Organization
from app.models.users import User
from tests.conftest import TEST_OWNER_DATA, TEST_RENTER_DATA, TEST_USER_DATA


@pytest.mark.anyio
@pytest.mark.parametrize(
    "new_user_data, status_code, location, message",
    [
        (
            # Owner
            TEST_OWNER_DATA,
            status.HTTP_201_CREATED,
            None,
            None,
        ),
        (
            # Renter
            TEST_RENTER_DATA,
            status.HTTP_201_CREATED,
            None,
            None,
        ),
        (
            {  # Owner without inn
                **TEST_USER_DATA,
                "is_owner": True,
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "organization_inn",
            "Organization INN is required for owners",
        ),
        (
            {  # Invalid email
                **TEST_USER_DATA,
                "email": "user@test",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "email",
            "value is not a valid email address",
        ),
        (
            {  # Invalid phone
                **TEST_USER_DATA,
                "phone": "99999999999",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "phone",
            "Invalid phone number",
        ),
        (
            {  # Short password
                **TEST_USER_DATA,
                "password": "Secret1",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "password",
            "Password must be at least 8 characters long",
        ),
        (
            {  # Upper password
                **TEST_USER_DATA,
                "password": "SECRET_PASSWORD123",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "password",
            "Password must contain at least one lowercase letter",
        ),
        (
            {  # Lower password
                **TEST_USER_DATA,
                "password": "secret_password123",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "password",
            "Password must contain at least one uppercase letter",
        ),
        (
            {  # No digits password
                **TEST_USER_DATA,
                "password": "SecretPassword",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "password",
            "Password must contain at least one digit",
        ),
        (
            {  # Short inn
                **TEST_OWNER_DATA,
                "organization_inn": "123456789",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "organization_inn",
            "Organization INN must contain 10 or 12 digits",
        ),
        (
            {  # No digits inn
                **TEST_OWNER_DATA,
                "organization_inn": "A123456789",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "organization_inn",
            "Organization INN must contain only digits",
        ),
    ],
)
async def test_user_create(client: AsyncClient, new_user_data: dict, status_code: int, location: str, message: str):
    # Given

    # When
    response = await client.post("/users/", json=new_user_data)

    # Then
    assert response.status_code == status_code
    if status_code == status.HTTP_201_CREATED:
        assert response.json()["email"] == new_user_data["email"]
    elif status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        assert len(response.json()["detail"]) == 1
        detail = response.json()["detail"][0]
        assert detail["loc"][1] == location
        assert detail["msg"] == message


@pytest.mark.anyio
async def test_email_conflict(client: AsyncClient, user_in_db: User):
    # Given
    new_user_data = TEST_USER_DATA

    # When
    response = await client.post("/users/", json=new_user_data)

    # Then
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.anyio
async def test_users_get(client: AsyncClient, user_in_db: User):
    # Given

    # When
    response = await client.get("/users/")

    # # Then
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    for field, value in response.json()[0].items():
        assert getattr(user_in_db, field) == value


@pytest.mark.anyio
async def test_user_get_by_id(client: AsyncClient, user_in_db: User):
    # Given

    # When
    response = await client.get(f"/users/{user_in_db.id}/")

    # Then
    assert response.status_code == status.HTTP_200_OK
    for field, value in response.json().items():
        assert getattr(user_in_db, field) == value


@pytest.mark.anyio
async def test_user_get_by_id_not_found(client: AsyncClient):
    # Given

    # When
    response = await client.get("/users/1/")

    # Then
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
@pytest.mark.parametrize(
    "test_client, status_code",
    [
        (
            # Authorized
            pytest.lazy_fixture("authorized_user_client"),
            status.HTTP_200_OK,
        ),
        (
            # Unauthorized
            pytest.lazy_fixture("client"),
            status.HTTP_401_UNAUTHORIZED,
        ),
    ],
)
async def test_get_current_user(test_client: AsyncClient, status_code: int):
    # Given

    # When
    response = await test_client.get("/users/me/")

    # Then
    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert response.json()["email"] == TEST_USER_DATA["email"]


@pytest.mark.anyio
async def test_user_update_unauthorized(client: AsyncClient, user_in_db: User):
    # Given
    user_update_data = {"email": "user_new@test.com"}

    # When
    response = await client.put("/users/me/", json=user_update_data)

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# TODO: For errors add assert for response.json()["detail"]
@pytest.mark.anyio
@pytest.mark.parametrize(
    "user_update_data, status_code, updated_fields",
    [
        (
            {"email": "user_new@test.com"},  # Update email
            status.HTTP_202_ACCEPTED,
            [
                "email",
            ],
        ),
        (
            {  # Update multiple fields
                "email": "user_new@test.com",
                "full_name": "Test User Jr.",
                "phone": "+79888888888",
            },
            status.HTTP_202_ACCEPTED,
            ["email", "full_name", "phone"],
        ),
        (
            {  # Update password
                "password": TEST_USER_DATA["password"],
                "new_password": "NewSecretPassword321",
            },
            status.HTTP_202_ACCEPTED,
            None,
        ),
        (
            {  # Update password without new password
                "password": TEST_USER_DATA["password"],
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            None,
        ),
        (
            {  # Update password with wrong old password
                "password": "WrongPassword123",
                "new_password": "NewSecretPassword321",
            },
            status.HTTP_401_UNAUTHORIZED,
            None,
        ),
        (
            {  # Update password without old password
                "new_password": "NewSecretPassword321",
            },
            status.HTTP_401_UNAUTHORIZED,
            None,
        ),
    ],
)
async def test_user_update(
    authorized_user_client: AsyncClient,
    user_in_db: User,
    user_update_data: dict,
    status_code: int,
    updated_fields: list[str],
):
    # Given

    # When
    response = await authorized_user_client.put("/users/me/", json=user_update_data)

    # Then
    assert response.status_code == status_code
    if status_code == status.HTTP_202_ACCEPTED and updated_fields:
        for field in updated_fields:
            assert response.json()[field] == user_update_data[field]


# TODO: Update inn


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user_client, user_update_data, is_verified_organization_member",
    [
        (
            # Renter
            pytest.lazy_fixture("authorized_user_client"),
            {  # Add inn
                "organization_inn": "0987654321",
            },
            False,
        ),
        (
            # Owner with unverified organization
            pytest.lazy_fixture("authorized_not_verified_owner_client"),
            {  # Change inn
                "organization_inn": "0987654321",
            },
            False,
        ),
        (
            # Owner with verified organization
            pytest.lazy_fixture("authorized_owner_client"),
            {  # Change inn
                "organization_inn": "0987654321",
            },
            False,  # After change inn need to verify organization again
        ),
        (
            # Owner with verified organization
            pytest.lazy_fixture("authorized_owner_client"),
            {  # Same inn
                "organization_inn": TEST_OWNER_DATA["organization_inn"],
            },
            True,  # Nothing changed
        ),
    ],
)
async def test_user_update_inn(
    user_client: AsyncClient, user_update_data: dict, is_verified_organization_member: bool
):
    # Given
    print((await user_client.get("/users/me/")).json())

    # When
    response = await user_client.put("/users/me/", json=user_update_data)

    # Then
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["organization_id"] == user_update_data["organization_inn"]
    assert response.json()["is_verified_organization_member"] == is_verified_organization_member


@pytest.mark.anyio
async def test_user_update_inn_existing_organization(
    authorized_owner_client: AsyncClient, organization_in_db: Organization
):
    # Given
    user_update_data = {
        "organization_inn": organization_in_db.inn,
    }

    # When
    response = await authorized_owner_client.put("/users/me/", json=user_update_data)

    # Then
    assert response.status_code == status.HTTP_202_ACCEPTED
