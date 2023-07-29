from enum import Enum

from pydantic import BaseModel
from tortoise import fields, models


class NotificationStatus(Enum):
    CREATED = "created"
    DELIVERED = "delivered"
    READ = "read"


class NotificationType(Enum):
    INCOMING_ORDER = "incoming_order"
    OUTGOING_ORDER = "outgoing_order"
    ORGANIZATION_VERIFICATION = "organization_verification"
    RATING_FROM_RENTER = "rating_from_renter"
    RATING_FROM_OWNER = "rating_from_organization"


class Notification(models.Model):
    status = fields.CharEnumField(NotificationStatus, default=NotificationStatus.CREATED)
    created_at = fields.DatetimeField(auto_now_add=True)
    delivered_at = fields.DatetimeField(null=True)
    read_at = fields.DatetimeField(null=True)
    type = fields.CharEnumField(NotificationType)
    recipient = fields.ForeignKeyField("models.User", related_name="notifications", null=True)
    organization = fields.ForeignKeyField("models.Organization", related_name="notifications", null=True)
    content = fields.JSONField()


class IncomingOrderType(Enum):
    ORDER_CREATED = "order_created"
    ORDER_CANCELED = "order_canceled"
    ORDER_UPDATED = "order_updated"
    RENT_STARTED = "rent_started"
    RENT_FINISHED = "rent_finished"


class OutgoingOrderType(Enum):
    ORDER_ACCEPTED = "order_accepted"
    ORDER_REJECTED = "order_rejected"
    RENT_STARTED = "rent_started"
    RENT_FINISHED = "rent_finished"


class OrganizationVerificationType(Enum):
    ORGANIZATION_VERIFIED = "organization_verified"
    ORGANIZATION_REJECTED = "organization_rejected"


class BaseOrderNotification(BaseModel):
    order_id: int


class IncomingOrderNotification(BaseOrderNotification):
    event: IncomingOrderType


class OutgoingOrderNotification(BaseOrderNotification):
    event: OutgoingOrderType


class OrganizationVerificationNotification(BaseModel):
    event: OrganizationVerificationType


class BaseRatingNotification(BaseOrderNotification):
    rating: int


class RatingFromRenterNotification(BaseRatingNotification):
    pass


class RatingFromOwnerNotification(BaseRatingNotification):
    pass


notification_content_templates = {
    NotificationType.INCOMING_ORDER: IncomingOrderNotification,
    NotificationType.OUTGOING_ORDER: OutgoingOrderNotification,
    NotificationType.ORGANIZATION_VERIFICATION: OrganizationVerificationNotification,
    NotificationType.RATING_FROM_RENTER: RatingFromRenterNotification,
    NotificationType.RATING_FROM_OWNER: RatingFromOwnerNotification,
}
