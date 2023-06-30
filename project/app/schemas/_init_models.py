from tortoise import Tortoise

from app.db import MODELS


Tortoise.init_models(MODELS, "models")
