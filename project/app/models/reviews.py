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


class NPS_CSI_Review(models.Model):
    order = fields.ForeignKeyField("models.Order", related_name="nps_csi_reviews")
    user = fields.ForeignKeyField("models.User", related_name="nps_csi_reviews")
    created_at = fields.DatetimeField(auto_now_add=True)

    # NPS
    nps = fields.IntField(null=True, min_value=1, max_value=10)

    # CSI
    location_availability_importance = fields.IntField(null=True, min_value=1, max_value=5)
    technical_condition_importance = fields.IntField(null=True, min_value=1, max_value=5)
    rental_price_importance = fields.IntField(null=True, min_value=1, max_value=5)
    registration_speed_importance = fields.IntField(null=True, min_value=1, max_value=5)
    interface_simplicity_importance = fields.IntField(null=True, min_value=1, max_value=5)
    equipment_variety_importance = fields.IntField(null=True, min_value=1, max_value=5)
    platform_commission_importance = fields.IntField(null=True, min_value=1, max_value=5)
    equipment_maintenance_importance = fields.IntField(null=True, min_value=1, max_value=5)
    technical_support_importance = fields.IntField(null=True, min_value=1, max_value=5)
    equipment_card_creation_importance = fields.IntField(null=True, min_value=1, max_value=5)
    applications_and_rent_equipment_management_importance = fields.IntField(null=True, min_value=1, max_value=5)

    location_availability_satisfaction = fields.IntField(null=True, min_value=1, max_value=5)
    technical_condition_satisfaction = fields.IntField(null=True, min_value=1, max_value=5)
    rental_price_satisfaction = fields.IntField(null=True, min_value=1, max_value=5)
    registration_speed_satisfaction = fields.IntField(null=True, min_value=1, max_value=5)
    interface_simplicity_satisfaction = fields.IntField(null=True, min_value=1, max_value=5)
    equipment_variety_satisfaction = fields.IntField(null=True, min_value=1, max_value=5)
    platform_commission_satisfaction = fields.IntField(null=True, min_value=1, max_value=5)
    equipment_maintenance_satisfaction = fields.IntField(null=True, min_value=1, max_value=5)
    technical_support_satisfaction = fields.IntField(null=True, min_value=1, max_value=5)
    equipment_card_creation_satisfaction = fields.IntField(null=True, min_value=1, max_value=5)
    applications_and_rent_equipment_management_satisfaction = fields.IntField(null=True, min_value=1, max_value=5)
