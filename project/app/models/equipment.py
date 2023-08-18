from enum import Enum

from tortoise import fields, models

from app.models.files import FileBaseModel


class EquipmentStatus(str, Enum):
    IN_RENT = "in_rent"

    # Owner statuses
    PUBLISHED = "published"
    HIDDEN = "hidden"
    ARCHIVED = "archived"


class EquipmentStatusUpdate(str, Enum):
    PUBLISHED = "published"
    HIDDEN = "hidden"
    ARCHIVED = "archived"


class TimeInterval(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class EquipmentCategory(models.Model):
    # code = fields.CharField(max_length=3)
    name = fields.CharField(max_length=255)
    added_by = fields.ForeignKeyField(
        "models.User", related_name="equipment_categories", on_delete=fields.SET_NULL, null=True
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    verified = fields.BooleanField(default=False)

    class PydanticMeta:
        backward_relations = False
        exclude = ["added_by", "added_by_id", "created_at", "verified"]


# For pydantic schema generation
class EquipmentCategoryWithEquipmentCount(EquipmentCategory):
    equipment_count = fields.IntField()

    class Meta:
        abstract = True


class EquipmentMedia(FileBaseModel):
    SAVE_PATH = "equipment/media/"

    host = fields.ForeignKeyField(
        "models.Equipment", related_name="photo_and_video", on_delete=fields.CASCADE, null=True
    )


class EquipmentDocument(FileBaseModel):
    SAVE_PATH = "equipment/documents/"

    host = fields.ForeignKeyField("models.Equipment", related_name="documents", on_delete=fields.CASCADE, null=True)


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
    organization = fields.ForeignKeyField("models.Organization", related_name="equipment", on_delete=fields.CASCADE)
    added_by = fields.ForeignKeyField("models.User", related_name="equipment", on_delete=fields.SET_NULL, null=True)
    category = fields.ForeignKeyField("models.EquipmentCategory", related_name="equipment", on_delete=fields.CASCADE)
    status = fields.CharEnumField(EquipmentStatus, default=EquipmentStatus.HIDDEN)
    year_of_release = fields.IntField(default=1900)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    documents: fields.ReverseRelation["EquipmentDocument"]
    photo_and_video: fields.ReverseRelation["EquipmentMedia"]

    class Meta:
        ordering = ["-updated_at"]

    class PydanticMeta:
        # https://github.com/tortoise/tortoise-orm/issues/1444
        # backward_relations = False # for some reason excludes annotated relations!
        exclude = [
            "orders",
            "notifications",
            "created_at",
            "updated_at",
            "organization",
            "added_by",
            "description_of_configuration",
            "year_of_release",
            "documents",
        ]
