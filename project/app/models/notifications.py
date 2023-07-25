from enum import Enum

from tortoise import fields, models


class NotificationStatus(Enum):
    CREATED = "created"
    DELIVERED = "delivered"
    READ = "read"


class BaseNotification(models.Model):
    status = fields.CharEnumField(NotificationStatus, default=NotificationStatus.CREATED)
    created_at = fields.DatetimeField(auto_now_add=True)
    delivered_at = fields.DatetimeField(null=True)
    read_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True


class UserBaseNotification(BaseNotification):
    recipient = fields.ForeignKeyField("models.User")

    class Meta:
        abstract = True


class UserOrganizationNotificationType(Enum):
    ORGANIZATION_VERIFIED = "organization_verified"
    ORGANIZATION_REJECTED = "organization_rejected"


class UserOrganizationNotification(UserBaseNotification):
    type = fields.CharEnumField(UserOrganizationNotificationType)


class UserOrderNotificationType(Enum):
    ORDER_ACCEPTED = "order_accepted"
    ORDER_REJECTED = "order_rejected"
    RENT_STARTED = "rent_started"
    RENT_FINISHED = "rent_finished"


class UserOrderNotification(UserBaseNotification):
    order = fields.ForeignKeyField("models.Order")
    type = fields.CharEnumField(UserOrderNotificationType)


# class UserRatingNotification(UserBaseNotification):
#     order = fields.ForeignKeyField("models.Order", related_name="notifications")
#     rating = fields.ForeignKeyField


class OrganizationBaseNotification(BaseNotification):
    organization = fields.ForeignKeyField("models.Organization")

    class Meta:
        abstract = True


class OrganizationNotificationType(Enum):
    ORDER_CREATED = "order_created"
    ORDER_CANCELED = "order_canceled"
    ORDER_UPDATED = "order_updated"
    RENT_STARTED = "rent_started"
    RENT_FINISHED = "rent_finished"


class OrganizationOrderNotification(OrganizationBaseNotification):
    order = fields.ForeignKeyField("models.Order")
    type = fields.CharEnumField(OrganizationNotificationType)


# class OrganizationRatingNotification(OrganizationBaseNotification):
#     order = fields.ForeignKeyField("models.Order", related_name="notifications")
    # rating = fields.ForeignKeyField(
