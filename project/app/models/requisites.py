from tortoise import fields, models


class Requisites(models.Model):
    user = fields.OneToOneField("models.User", related_name="requisites", on_delete=fields.CASCADE, null=True)
    organization = fields.OneToOneField(
        "models.Organization", related_name="requisites", on_delete=fields.CASCADE, null=True
    )

    payment_account = fields.CharField(max_length=63, null=True)
    bank_bic = fields.CharField(max_length=63, null=True)
    bank_inn = fields.CharField(max_length=63, null=True)
    bank_name = fields.CharField(max_length=255, null=True)
    bank_correspondent_account = fields.CharField(max_length=63, null=True)

    class PydanticMeta:
        exclude = ("id", "user", "user_id", "organization", "organization_id")
