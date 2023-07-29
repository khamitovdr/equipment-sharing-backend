from datetime import datetime

from pydantic import BaseModel

from app.models.notifications import NotificationStatus, NotificationType


class NotificationSchema(BaseModel):
    id: int
    status: NotificationStatus
    created_at: datetime
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    type: NotificationType
    content: dict
