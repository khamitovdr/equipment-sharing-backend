from tortoise import fields, models


class FileBaseModel(models.Model):
    SAVE_PATH = None

    name = fields.CharField(max_length=255, null=True)
    media_type = fields.CharField(max_length=255, null=True)
    path = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    host: fields.ForeignKeyRelation

    class Meta:
        abstract = True

    class PydanticMeta:
        backward_relations = False
        exclude = ["created_at"]
