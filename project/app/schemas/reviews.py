from pydantic import BaseModel


class ReviewCreateSchema(BaseModel):
    form_data: list[dict]
