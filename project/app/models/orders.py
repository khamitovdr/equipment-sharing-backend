from enum import Enum

from tortoise import fields, models


class OrderStatus(Enum):
    # Renter statuses
    CANCELED = "canceled"

    # Owner statuses
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    
    # Common statuses
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

    # @classmethod
    # def owner_responses(self):
    #     return [
    #         self.ACCEPTED,
    #         self.REJECTED,
    #     ]
    
    # def is_owner_response(self):
    #     return self in self.owner_responses()


class OrderResponseStatus(Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Order(models.Model):
    equipment = fields.ForeignKeyField("models.Equipment", related_name="orders")
    requester = fields.ForeignKeyField("models.User", related_name="orders")
    start_date = fields.DateField()
    end_date = fields.DateField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    status = fields.CharEnumField(OrderStatus, default=OrderStatus.CREATED)
