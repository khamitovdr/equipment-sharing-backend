import logging
from functools import lru_cache

from pydantic import AnyUrl, BaseSettings


log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = 0
    database_url: AnyUrl = None
    dadata_token: str = "9e00342e6a7c5bdc1192203f0efd5fa1fb130e67"    # !!!!


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
