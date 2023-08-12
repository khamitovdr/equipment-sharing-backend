import logging

from tortoise import functions
from tortoise.expressions import Q

from app.models.equipment import (
    Equipment,
    EquipmentCategory,
    EquipmentDocument,
    EquipmentMedia,
    EquipmentStatus,
)
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.equipment import EquipmentCreateSchema, EquipmentUpdateSchema

log = logging.getLogger("uvicorn")


async def create_equipment_category(name: str, user: User, verified: bool = False) -> EquipmentCategory:
    category = EquipmentCategory(name=name, verified=verified, added_by=user)
    await category.save()
    return category


async def create_categories(categories_dict: dict, verified: bool = False):
    categories = [EquipmentCategory(name=name, verified=verified) for _, name in categories_dict.items()]
    await EquipmentCategory.bulk_create(categories)


async def create_equipment(
    equipment_schema: EquipmentCreateSchema, user: User, organization: Organization
) -> Equipment:
    equipment_dict = equipment_schema.dict(exclude_unset=True)
    equipment_dict["added_by"] = user
    equipment_dict["organization"] = organization
    documents = equipment_dict.pop("documents_ids")
    photo_and_video = equipment_dict.pop("photo_and_video_ids")

    equipment = await Equipment.create(**equipment_dict)

    try:
        host_not_set = Q(host_id__isnull=True)
        await EquipmentDocument.filter(host_not_set, id__in=documents).update(host=equipment)
        await EquipmentMedia.filter(host_not_set, id__in=photo_and_video).update(host=equipment)
    except Exception as e:
        log.error(f"Error while updating equipment {equipment.id} with documents and media: {e}")
        await equipment.delete()
        raise e

    return equipment


async def update_equipment(equipment: Equipment, equipment_schema: EquipmentUpdateSchema) -> Equipment:
    equipment_dict = equipment_schema.dict(exclude_unset=True)
    documents = equipment_dict.pop("documents_ids")
    photo_and_video = equipment_dict.pop("photo_and_video_ids")

    await equipment.update_from_dict(equipment_dict)

    try:
        host_not_set = Q(host_id__isnull=True)
        host_is_equipment = Q(host=equipment)

        await EquipmentDocument.filter(host_not_set, id__in=documents).update(host=equipment)
        await EquipmentDocument.filter(host_is_equipment, id__not_in=documents).delete()

        await EquipmentMedia.filter(host_not_set, id__in=photo_and_video).update(host=equipment)
        await EquipmentMedia.filter(host_is_equipment, id__not_in=photo_and_video).delete()

    except Exception as e:
        log.error(f"Error while updating equipment {equipment.id} with documents and media: {e}")
        raise e

    await equipment.refresh_from_db()
    return equipment


async def delete_equipment(equipment: Equipment) -> int:
    equipment_id = equipment.id
    await equipment.delete()
    return equipment_id


async def get_equipment_by_id(equipment_id: int) -> Equipment | None:
    equipment = await Equipment.get_or_none(id=equipment_id).prefetch_related(
        "organization", "added_by", "category", "documents", "photo_and_video"
    )
    return equipment


async def get_equipment_list(
    organization_inn: str = None,
    category_id: int = None,
    status: EquipmentStatus = None,
    offset: int = 0,
    limit: int = 40,
) -> list[Equipment]:
    filtering_params = {}
    if status:
        filtering_params["status"] = status
    if organization_inn:
        filtering_params["organization__inn"] = organization_inn
    if category_id:
        filtering_params["category_id"] = category_id
    return (
        await Equipment.filter(**filtering_params)
        .prefetch_related(
            "organization",
            "category",
            "photo_and_video",
        )
        .order_by("-updated_at")
        .offset(offset)
        .limit(limit)
        .all()
    )


async def get_equipment_categories(organization_inn: str = None) -> list[EquipmentCategory]:
    filtering_params = {}
    if organization_inn:
        filtering_params["equipment__organization__inn"] = organization_inn
    else:
        filtering_params["verified"] = True

    return (
        await EquipmentCategory.filter(**filtering_params)
        .annotate(equipment_count=functions.Count("equipment"))
        .order_by("-equipment_count")
        .all()
    )


async def get_organization_main_equipment_categories(organization_inn: str) -> list[EquipmentCategory]:
    categories = (
        await EquipmentCategory.filter(equipment__organization__inn=organization_inn)
        .annotate(equipment_count=functions.Count("equipment"))
        .order_by("-equipment_count")
        .limit(3)
        .all()
    )

    return categories


async def update_equipment_status(equipment: Equipment, status: EquipmentStatus) -> Equipment:
    equipment.status = status
    await equipment.save()
    return equipment
