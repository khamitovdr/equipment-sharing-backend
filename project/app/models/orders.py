from enum import Enum
from functools import total_ordering, lru_cache

from tortoise import fields, models

from app.models.equipment import TimeInterval
from app.models.files import FileBaseModel, UploadedFileBaseModel
from app.models.payments import PaymentBaseModel


class OrderContractDraft(UploadedFileBaseModel):
    SAVE_PATH = "orders/documents/"

    host = fields.ForeignKeyField("models.Order", related_name="contract_drafts", on_delete=fields.CASCADE, null=True)
    accepted_by_renter = fields.BooleanField(default=False)
    accepted_by_owner = fields.BooleanField(default=False)

    class PydanticMeta:
        backward_relations = False
        exclude = ["created_at", "host", "host_id", "hash"]


class OrderContract(FileBaseModel):
    SAVE_PATH = "orders/documents/"

    host = fields.OneToOneField("models.Order", related_name="contract", on_delete=fields.CASCADE, null=True)


class OrderContractSignature(UploadedFileBaseModel):
    SAVE_PATH = "orders/documents/"

    verified = fields.BooleanField(default=False)

    class Meta:
        abstract = True


class OrderContractSignatureRenter(OrderContractSignature):
    host = fields.OneToOneField(
        "models.OrderContract", related_name="signature_renter", on_delete=fields.CASCADE, null=True
    )


class OrderContractSignatureOwner(OrderContractSignature):
    host = fields.OneToOneField(
        "models.OrderContract", related_name="signature_owner", on_delete=fields.CASCADE, null=True
    )


class OrderPayment(PaymentBaseModel):
    corresponding_order_id = fields.IntField()
    order = fields.OneToOneField("models.Order", related_name="payment", on_delete=fields.CASCADE, null=True)


@total_ordering
class OrderStatus(str, Enum):
    CREATED = "created"
    COST_NEGOTIATION = "cost_negotiation"
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

    REJECTED = "rejected"  # rejected by owner
    CANCELED = "canceled"  # canceled by renter

    @classmethod
    @property
    @lru_cache()
    def __order_dict(cls):
        return {val: key for key, val in enumerate(cls)}
    

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.__order_dict[self] > self.__order_dict[other]
        return NotImplemented
    

    def __add__(self, other):
        if isinstance(other, int):
            return tuple(self.__class__)[self.__order_dict[self] + other]
        return NotImplemented


class PaymentType(str, Enum):
    VIA_PLATFORM = "via-platform"
    BY_CASH = "by-cash"


class Order(models.Model):
    equipment = fields.ForeignKeyField("models.Equipment", related_name="orders")
    requester = fields.ForeignKeyField("models.User", related_name="orders")
    start_date = fields.DateField()
    end_date = fields.DateField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    status = fields.CharEnumField(OrderStatus, default=OrderStatus.CREATED)

    cost = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    cost_accepted_by_renter = fields.BooleanField(default=True)

    signed_offline_by_renter = fields.BooleanField(default=False)
    signed_offline_by_owner = fields.BooleanField(default=False)

    payment_type = fields.CharEnumField(PaymentType, null=True)
    is_paid = fields.BooleanField(default=False)

    equipment_accepted_by_renter = fields.BooleanField(default=False)
    equipment_accepted_by_owner = fields.BooleanField(default=False)

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
    
    def waiting_for_renter_action(self) -> bool:
        return NotImplemented
    
    def waiting_for_owner_action(self) -> bool:
        return NotImplemented
    class PydanticMeta:
        backward_relations = False
        # computed = ["waiting_for_renter_action", "waiting_for_owner_action"]
