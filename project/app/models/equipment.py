from enum import Enum

from tortoise import fields, models


class EquipmentStatus(Enum):
    PUBLISHED = "published"
    IN_RENT = "in_rent"
    HIDDEN = "hidden"
    ARCHIVED = "archived"


class EquipmentCategory(Enum):
    SPECIAL_EQUIPMENT = "Спецтехника"
    INDUSTRIAL_EQUIPMENT = "Промышленное оборудование"
    CONTRACT_MANUFACTURING = "Контрактное производство"
    EXHIBITION_EQUIPMENT = "Выставочное оборудование"
    OTHER = "Другое"


class TimeInterval(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class Equipment(models.Model):
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    description_of_configuration = fields.TextField(null=True)
    with_operator = fields.BooleanField(default=False)
    price = fields.FloatField()
    time_interval = fields.CharEnumField(TimeInterval, default=TimeInterval.DAY)
    # quantity = fields.IntField(default=1)
    avatar = fields.CharField(max_length=255)
    photo_and_video = fields.CharField(max_length=255)
    documents = fields.CharField(max_length=255) # one collective pdf file
    organization = fields.ForeignKeyField("models.Organization", related_name="equipment")
    category = fields.CharEnumField(EquipmentCategory, default=EquipmentCategory.OTHER)
    status = fields.CharEnumField(EquipmentStatus, default=EquipmentStatus.HIDDEN)
    year_of_release = fields.IntField(default=1900)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name
