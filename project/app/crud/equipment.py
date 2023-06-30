import logging

from app.models.equipment import EquipmentCategory, Equipment
# from app.schemas.equipment import EquipmentCategorySchema, EquipmentSchema


log = logging.getLogger("uvicorn")


async def create_categories(categories_dict: dict, verified: bool = False):
    """Creates activities in DB."""
    categories = [EquipmentCategory(name=name, verified=verified) for _, name in categories_dict.items()]
    await EquipmentCategory.bulk_create(categories)
