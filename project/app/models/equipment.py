from enum import Enum

from tortoise import fields, models


class EquipmentStatus(Enum):
    PUBLISHED = "published"
    IN_RENT = "in_rent"
    HIDDEN = "hidden"
    ARCHIVED = "archived"


class TimeInterval(Enum):
    DAY = "дни"
    WEEK = "недели"
    MONTH = "месяцы"
    YEAR = "годы"


class EquipmentCategory(models.Model):
    # code = fields.CharField(max_length=3)
    name = fields.CharField(max_length=255)
    creator = fields.ForeignKeyField("models.User", related_name="equipment_categories", null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    verified = fields.BooleanField(default=False)


class EquipmentMedia(models.Model):
    equipment = fields.ForeignKeyField("models.Equipment", related_name="photo_and_video")
    media_type = fields.CharField(max_length=255, null=True)
    path = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)


class EquipmentDocument(models.Model): # pdf
    equipment = fields.ForeignKeyField("models.Equipment", related_name="documents")
    path = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)


class Equipment(models.Model):
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    description_of_configuration = fields.TextField(null=True)
    with_operator = fields.BooleanField(default=False)
    price = fields.FloatField()
    time_interval = fields.CharEnumField(TimeInterval, default=TimeInterval.DAY)
    # quantity = fields.IntField(default=1)
    # avatar = fields.ForeignKeyField(
    #     "models.EquipmentMedia", 
    #     null=True
    # ) # tortoise.exceptions.ConfigurationError: Can't create schema due to cyclic fk references
    organization = fields.ForeignKeyField("models.Organization", related_name="equipment")
    added_by = fields.ForeignKeyField("models.User", related_name="equipment")
    category = fields.ForeignKeyField("models.EquipmentCategory", related_name="equipment")
    status = fields.CharEnumField(EquipmentStatus, default=EquipmentStatus.HIDDEN)
    year_of_release = fields.IntField(default=1900)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
