import os

import pytest
from httpx import AsyncClient
from tortoise import Tortoise

from app.config import Settings, get_settings
from app.db import MODELS
from app.main import create_application


DB_URL = os.environ.get("DATABASE_TEST_URL")


def get_settings_override():
    return Settings(
        environment="test",
        testing=True,
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


async def init(db_url: str = DB_URL):
    await init_db(db_url, False, True) # create_db=False, schemas=True


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    async with AsyncClient(app=app, base_url="http://test") as client:
        print("Client is ready")
        yield client


# @pytest.fixture(scope="function")  #, autouse=True)
# async def initialize_tests_function():
#     await init()
#     yield
#     [await model.all().delete() for model in Tortoise.apps["models"].values()]


@pytest.fixture(scope="module", autouse=True)
async def initialize_tests_session():
    await init()
    yield
    [await model.all().delete() for model in Tortoise.apps["models"].values()]
