from tortoise import fields, models
from tortoise.functions import functions

from app.models.equipment import EquipmentCategory


class Activity(models.Model):
    code = fields.CharField(max_length=10, pk=True)
    description = fields.CharField(max_length=500)


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
    main_activity = fields.ForeignKeyField('models.Activity', related_name='organizations')

    class PydanticMeta:
        exclude = ['users', 'equipment', 'notifications', 'main_activity']

    # users: fields.ReverseRelation['models.User']

    # def main_equipment_categories(self) -> list[dict]:
    #     equipment = self.users.equipment \
    #         .annotate(count=functions.Count('id')) \
    #         .group_by('category_id') \
    #         .order_by('-count') \
    #         .values('category__name', 'count')
        
    #     return equipment
