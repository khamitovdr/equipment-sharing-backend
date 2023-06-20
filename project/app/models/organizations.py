from tortoise import fields, models


class Activity(models.Model):
    code = fields.CharField(max_length=10, pk=True)
    description = fields.CharField(max_length=500)


class Organization(models.Model):
    short_name = fields.CharField(max_length=100, unique=True)
    full_name = fields.CharField(max_length=150, unique=True)
    ogrn = fields.CharField(max_length=20, unique=True)
    inn = fields.CharField(max_length=20, unique=True)
    kpp = fields.CharField(max_length=20, unique=True)
    registration_date = fields.DateField()
    authorized_capital_k_rubles = fields.DecimalField(max_digits=12, decimal_places=2)
    legal_address = fields.CharField(max_length=150)
    manager_name = fields.CharField(max_length=150)
    main_activity = fields.ForeignKeyField('models.Activity', related_name='organizations')