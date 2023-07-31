from tortoise import fields, models


class Review(models.Model):
    rating = fields.IntField()
    comment = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        abstract = True

    class PydanticMeta:
        backward_relations = False


class OwnerReview(Review):
    order = fields.OneToOneField("models.Order", related_name="owner_review")


class RenterReview(Review):
    order = fields.OneToOneField("models.Order", related_name="renter_review")
