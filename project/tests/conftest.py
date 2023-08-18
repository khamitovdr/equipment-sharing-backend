import os
from datetime import date

import pytest
from httpx import AsyncClient
from tortoise import Tortoise

from app.api.users import create_new_user
from app.config import Settings, get_settings
from app.crud.organizations import create_organization
from app.crud.equipment import create_equipment_category
from app.db import MODELS
from app.main import create_application
from app.models.organizations import Organization
from app.models.users import User
from app.models.equipment import Equipment, EquipmentCategory
from app.schemas.organizations import DadataResponseSchema
from app.schemas.users import UserCreateSchema

#####################
#   General setup   #
#####################


DB_URL = os.environ.get("DATABASE_TEST_URL")


def get_settings_override() -> Settings:
    return Settings(
        environment="test",
        testing=True,
        secret_key="366b0d3d5451f8570e8bcd41b1747bdbcb12c8b1bd6ac909a9c04a1b437eb484",
        database_url=os.environ.get("DATABASE_TEST_URL"),
    )


async def init_db(db_url, create_db: bool = False, schemas: bool = False) -> None:
    """Initial database connection"""
    await Tortoise.init(db_url=db_url, modules={"models": MODELS}, _create_db=create_db)
    if create_db:
        print(f"Database created! {db_url = }")
    if schemas:
        await Tortoise.generate_schemas()
        print("Success to generate schemas")


async def init(db_url: str = DB_URL) -> None:
    await init_db(db_url, False, True)  # create_db=False, schemas=True


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    async with AsyncClient(app=app, base_url="http://test") as client:
        print("Client is ready")
        yield client


@pytest.fixture(autouse=True)
async def initialize_tests() -> None:
    await init()
    yield
    [await model.all().delete() for model in Tortoise.apps["models"].values()]


#####################
#   Auth fixtures   #
#####################


@pytest.fixture
async def client_instant_token_expired(monkeypatch) -> AsyncClient:
    monkeypatch.setattr("app.api.token.ACCESS_TOKEN_EXPIRE_DAYS", 0)
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    async with AsyncClient(app=app, base_url="http://test") as client:
        print("Client is ready")
        yield client


######################
#   Users fixtures   #
######################


TEST_USER_DATA = {
    "email": "user@test.com",
    "full_name": "Test User",
    "is_owner": False,
    "password": "SecretPassword123",
    "phone": "+79999999999",
}

TEST_OWNER_DATA = {
    **TEST_USER_DATA,
    "is_owner": True,
    "organization_inn": "1234567890",
}


@pytest.fixture
async def user_in_db() -> User:
    user_schema = UserCreateSchema(**TEST_USER_DATA)
    user = await create_new_user(user_schema)
    return user


# TODO: merge with user_in_db fixture (use parametrization)
@pytest.fixture
async def not_verified_owner_in_db() -> User:
    user_schema = UserCreateSchema(**TEST_OWNER_DATA)
    user_schema.email = "not_verified_owner@test.com"
    user = await create_new_user(user_schema)
    return user


# TODO: merge with user_in_db fixture (use parametrization)
@pytest.fixture
async def verified_owner_in_db() -> User:
    user_schema = UserCreateSchema(**TEST_OWNER_DATA)
    user_schema.email = "verified_owner@test.com"
    user = await create_new_user(user_schema)
    user.is_verified_organization_member = True
    await user.save()
    return user


@pytest.fixture
async def authorized_user_client(user_in_db: User) -> AsyncClient:
    login_data = {
        "username": user_in_db.email,
        "password": TEST_USER_DATA["password"],
    }
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/login/", data=login_data)
        access_token = login_response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {access_token}"
        print("Client is ready")
        yield client


# TODO: merge with authorized_user_client fixture (use parametrization)
@pytest.fixture
async def authorized_not_verified_owner_client(not_verified_owner_in_db: User) -> AsyncClient:
    login_data = {
        "username": not_verified_owner_in_db.email,
        "password": TEST_OWNER_DATA["password"],
    }
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/login/", data=login_data)
        access_token = login_response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {access_token}"
        print("Client is ready")
        yield client


# TODO: merge with authorized_user_client fixture (use parametrization)
@pytest.fixture
async def authorized_owner_client(verified_owner_in_db: User) -> AsyncClient:
    login_data = {
        "username": verified_owner_in_db.email,
        "password": TEST_OWNER_DATA["password"],
    }
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/login/", data=login_data)
        access_token = login_response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {access_token}"
        print("Client is ready")
        yield client


##############################
#   Organizations fixtures   #
##############################


TEST_ORGANIZATION = DadataResponseSchema(
    short_name="LLC Test Organization",
    full_name="Limited Liability Company Test Organization",
    ogrn="1234567890123",
    inn="0000000000",
    kpp="123456789",
    registration_date=date(2020, 1, 1),
    # authorized_capital_k_rubles=100,
    legal_address="Moscow, Test street, 1",
    manager_name="John Doe",
    main_activity="01.1",
)


@pytest.fixture
async def organization_in_db() -> Organization:
    organization = await create_organization(TEST_ORGANIZATION)
    return organization


#####################################
#   Equipment Categories fixtures   #
#####################################


@pytest.fixture
async def not_verified_equipment_categories_in_db() -> list[EquipmentCategory]:
    categories = [
        await create_equipment_category(name=name, verified=False, added_by=None)
        for name in ("Not verified Category 1", "Not verified Category 2")
    ]
    return categories


@pytest.fixture
async def verified_equipment_categories_in_db() -> list[EquipmentCategory]:
    categories = [
        await create_equipment_category(name=name, verified=True, added_by=None)
        for name in ("Test Category 1", "Test Category 2", "Test Category 3")
    ]
    return categories


@pytest.fixture
async def organizations_equipment_category_in_db(verified_owner_in_db: User) -> EquipmentCategory:
    category = await create_equipment_category(
        name="Organization's Category",
        added_by=verified_owner_in_db,
    )
    return category
