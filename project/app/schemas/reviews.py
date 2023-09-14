import re
from typing import Any

from pydantic import BaseModel, Json


class ReviewCreateSchema(BaseModel):
    form_data: Json[Any]
