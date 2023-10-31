from tortoise import fields, models


class PaymentBaseModel(models.Model):
    id = fields.CharField(max_length=255, pk=True)
    amount = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    currency = fields.CharField(max_length=3, default="RUB")
    status = fields.CharField(max_length=255, null=True)
    events = fields.JSONField(default=[])
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True
