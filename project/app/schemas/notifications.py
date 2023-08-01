from tortoise.contrib.pydantic import pydantic_queryset_creator

from app import _init_models  # noqa: F401
from app.models.notifications import Notification

# class NotificationSchema(BaseModel):
#     id: int
#     status: NotificationStatus
#     created_at: datetime
#     delivered_at: datetime | None = None
#     read_at: datetime | None = None
#     type: NotificationType
#     content: dict


NotificationListSchema = pydantic_queryset_creator(Notification)
