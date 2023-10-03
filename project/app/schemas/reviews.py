from pydantic import BaseModel, validator
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models.reviews import OwnerReview


class ReviewCreateSchema(BaseModel):
    rating: int
    comment: str

    @validator("rating")
    def rating_must_be_in_range(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Rating must be in range [1, 5]")
        return v


class FeedbackCreateSchema(BaseModel):
    form_data: list[dict]


ReviewSchema = pydantic_model_creator(OwnerReview, name="ReviewSchema")
