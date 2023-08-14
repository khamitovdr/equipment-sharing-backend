from tortoise import fields, models


class FileBaseModel(models.Model):
    SAVE_PATH = None

    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=255)
    media_type = fields.CharField(max_length=255)
    media_format = fields.CharField(max_length=255)
    hash = fields.CharField(max_length=255)
    original_path = fields.CharField(max_length=255)
    path = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)
    host: fields.ForeignKeyRelation

    class Meta:
        abstract = True

    class PydanticMeta:
        backward_relations = False
        exclude = ["created_at", "host", "host_id", "hash"]
