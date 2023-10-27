from enum import Enum

from tortoise import fields, models

from app.models.equipment import TimeInterval


class OrderStatus(str, Enum):
    CREATED = "created"
    CANCELED = "canceled"  # canceled by renter
    REJECTED = "rejected"  # rejected by owner
    CONTRACT_FORMATION = "contract_formation"
    CONTRACT_NEGOTIATION = "contract_negotiation"
    CONTRACT_SIGNING = "contract_signing"
    CHOOSING_PAYMENT_METHOD = "choosing_payment_method"
    WAITING_FOR_PAYMENT = "waiting_for_payment"
    ACCEPTANCE_BY_RENTER = "acceptance_by_renter"
    WAITING_FOR_RENT = "waiting_for_rent"
    IN_RENT = "in_rent"
    ACCEPTANCE_BY_OWNER = "acceptance_by_owner"
    WAITING_FOR_REVIEW = "waiting_for_review"
    FINISHED = "finished"


class OrderResponseStatus(str, Enum):
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

    cost = fields.FloatField(null=True)
    payment_id = fields.CharField(max_length=255, null=True)

    def estimated_cost(self) -> float:
        price = self.equipment.price
        time_interval = self.equipment.time_interval
        n_days = (self.end_date - self.start_date).days + 1
        if time_interval == TimeInterval.DAY:
            cost = price * n_days
        elif time_interval == TimeInterval.WEEK:
            cost = price * n_days / 7
        elif time_interval == TimeInterval.MONTH:
            cost = price * n_days / 30
        elif time_interval == TimeInterval.YEAR:
            cost = price * n_days / 365

        return round(cost, 2)

    class PydanticMeta:
        backward_relations = False
