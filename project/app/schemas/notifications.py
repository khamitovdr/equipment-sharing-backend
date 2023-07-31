from tortoise.contrib.pydantic import pydantic_queryset_creator

from app.models.notifications import Notification
from app.schemas import _init_models

# class NotificationSchema(BaseModel):
#     id: int
#     status: NotificationStatus
#     created_at: datetime
#     delivered_at: datetime | None = None
#     read_at: datetime | None = None
#     type: NotificationType
#     content: dict


NotificationListSchema = pydantic_queryset_creator(Notification)
