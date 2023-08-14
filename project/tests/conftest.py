import os

import pytest
from httpx import AsyncClient
from tortoise import Tortoise

from app.config import Settings, get_settings
from app.db import MODELS
from app.main import create_application


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
    await Tortoise.init(
        db_url=db_url, modules={"models": MODELS}, _create_db=create_db
    )
    if create_db:
        print(f"Database created! {db_url = }")
    if schemas:
        await Tortoise.generate_schemas()
        print("Success to generate schemas")


async def init(db_url: str = DB_URL) -> None:
    await init_db(db_url, False, True) # create_db=False, schemas=True


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

TEST_RENTER_DATA = {
    **TEST_USER_DATA,
}

TEST_OWNER_DATA = {
    **TEST_USER_DATA,
    "is_owner": True,
    "organization_inn": "1234567890",
}


@pytest.fixture
async def user_in_db(client: AsyncClient) -> dict:
    response = await client.post("/users/", json=TEST_USER_DATA)
    return response.json()
