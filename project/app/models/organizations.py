from tortoise import fields, models


class Organization(models.Model):
    inn = fields.CharField(max_length=63, pk=True)
    short_name = fields.CharField(max_length=255, unique=True)
    full_name = fields.CharField(max_length=255, unique=True)
    ogrn = fields.CharField(max_length=63, unique=True)
    kpp = fields.CharField(max_length=63, unique=True)
    registration_date = fields.DateField()
    authorized_capital_k_rubles = fields.DecimalField(max_digits=24, decimal_places=2, null=True)
    legal_address = fields.CharField(max_length=255)
    manager_name = fields.CharField(max_length=255)
    main_activity = fields.CharField(max_length=15)

    class PydanticMeta:
        exclude = ("users", "equipment", "notifications")
