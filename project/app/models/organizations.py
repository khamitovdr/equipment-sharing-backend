from tortoise import fields, models


class Organization(models.Model):
    inn = fields.CharField(max_length=63, pk=True)
    short_name = fields.CharField(max_length=255, unique=True, null=True)
    full_name = fields.CharField(max_length=255, unique=True, null=True)
    ogrn = fields.CharField(max_length=63, unique=True, null=True)
    kpp = fields.CharField(max_length=63, unique=True, null=True)
    registration_date = fields.DateField(null=True)
    authorized_capital_k_rubles = fields.DecimalField(max_digits=24, decimal_places=2, null=True)
    legal_address = fields.CharField(max_length=255, null=True)
    manager_name = fields.CharField(max_length=255, null=True)
    main_activity = fields.CharField(max_length=15, null=True)

    contact_phone = fields.CharField(max_length=255, null=True)
    contact_email = fields.CharField(max_length=255, null=True)
    contact_employee_name = fields.CharField(max_length=255, null=True)
    contact_employee_middle_name = fields.CharField(max_length=255, null=True)
    contact_employee_surname = fields.CharField(max_length=255, null=True)
    
    class PydanticMeta:
        exclude = ("users", "equipment", "notifications")
