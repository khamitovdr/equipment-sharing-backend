import os
import logging
import hashlib

from fastapi import UploadFile
from tortoise import functions

from app.models.equipment import EquipmentCategory, EquipmentMedia, EquipmentDocument, Equipment
from app.models.users import User
from app.schemas.equipment import EquipmentCreateForm, EquipmentStatus


UPLOAD_DIR = "static/equipment/"


log = logging.getLogger("uvicorn")


async def create_equipment_category(name: str, user: User, verified: bool = False) -> EquipmentCategory:
    category = EquipmentCategory(name=name, verified=verified, added_by=user)
    await category.save()
    return category


async def create_categories(categories_dict: dict, verified: bool = False):
    categories = [EquipmentCategory(name=name, verified=verified) for _, name in categories_dict.items()]
    await EquipmentCategory.bulk_create(categories)


async def create_equipment_media(equipment: Equipment, media: UploadFile) -> EquipmentMedia:
    data = await media.read()

    hash = hashlib.sha1(data).hexdigest()
    ext = os.path.splitext(media.filename)[-1]
    save_path = f"{UPLOAD_DIR}{hash}{ext}"

    with open(save_path, "wb") as f:
        f.write(data)

    equipment_media = EquipmentMedia(equipment=equipment, path=save_path, media_type=media.content_type)
    await equipment_media.save()
    return equipment_media


async def create_equipment_document(equipment: Equipment, document: UploadFile) -> EquipmentDocument:
    data = await document.read()
    assert document.content_type == "application/pdf"

    hash = hashlib.sha1(data).hexdigest()
    ext = os.path.splitext(document.filename)[-1]
    save_path = f"{UPLOAD_DIR}{hash}{ext}"

    with open(save_path, "wb") as f:
        f.write(data)

    equipment_document = EquipmentDocument(equipment=equipment, path=save_path)
    await equipment_document.save()
    return equipment_document


async def create_equipment(create_form: EquipmentCreateForm, user: User):

    EXCLUDE_FIELDS = ["photo_and_video", "documents"]

    fields = create_form.__dataclass_fields__.keys()

    await user.fetch_related("organization")
    equipment = Equipment(added_by=user, organization=user.organization, **{field: create_form.__getattribute__(field) for field in fields if field not in EXCLUDE_FIELDS})
    await equipment.save()

    media = [await create_equipment_media(equipment, media) for media in create_form.photo_and_video]
    documents = [await create_equipment_document(equipment, document) for document in create_form.documents]

    return equipment


async def get_equipment_by_id(equipment_id: int) -> Equipment | None:
    equipment = await Equipment.get_or_none(id=equipment_id).prefetch_related("organization", "category")
    return equipment


async def get_equipment_list(organization_inn: str = None, category_id: int = None, status: EquipmentStatus = None) -> list[Equipment]:
    filtering_params = {}
    if status:
        filtering_params["status"] = status
    if organization_inn:
        filtering_params["organization__inn"] = organization_inn
    if category_id:
        filtering_params["category_id"] = category_id
    return await Equipment.filter(**filtering_params).prefetch_related("category", "organization").all()


async def get_equipment_categories(organization_inn: str = None) -> list[EquipmentCategory]:
    filtering_params = {}
    if organization_inn:
        filtering_params["equipment__organization__inn"] = organization_inn
    else:
        filtering_params["verified"] = True

    return await EquipmentCategory.filter(**filtering_params) \
        .annotate(equipment_count=functions.Count('equipment')) \
        .order_by('-equipment_count') \
        .all()


async def get_organization_main_equipment_categories(organization_inn: str) -> list[EquipmentCategory]:
    categories = await EquipmentCategory \
        .filter(equipment__organization__inn=organization_inn) \
        .annotate(equipment_count=functions.Count('equipment')) \
        .order_by('-equipment_count') \
        .limit(3) \
        .all()
    
    return categories
