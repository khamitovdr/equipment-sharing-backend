from tortoise import fields, models


class Activity(models.Model):
    code = fields.CharField(max_length=10, pk=True)
    description = fields.CharField(max_length=500)

    class PydanticMeta:
        backward_relations = False


class Organization(models.Model):
    inn = fields.CharField(max_length=20, pk=True)
    short_name = fields.CharField(max_length=100, unique=True)
    full_name = fields.CharField(max_length=150, unique=True)
    ogrn = fields.CharField(max_length=20, unique=True)
    kpp = fields.CharField(max_length=20, unique=True)
    registration_date = fields.DateField()
    authorized_capital_k_rubles = fields.DecimalField(max_digits=12, decimal_places=2, null=True)
    legal_address = fields.CharField(max_length=150)
    manager_name = fields.CharField(max_length=150)
    main_activity = fields.ForeignKeyField("models.Activity", related_name="organizations")

    class PydanticMeta:
        backward_relations = False
