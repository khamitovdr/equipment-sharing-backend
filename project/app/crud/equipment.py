import os
import logging
import hashlib

from fastapi import UploadFile

from app.models.equipment import EquipmentCategory, EquipmentMedia, EquipmentDocument, Equipment
from app.models.users import User
from app.schemas.equipment import EquipmentCreateForm


UPLOAD_DIR = "static/equipment/"


log = logging.getLogger("uvicorn")


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
    equipment = Equipment(added_by=user, **{field: create_form.__getattribute__(field) for field in fields if field not in EXCLUDE_FIELDS})
    await equipment.save()

    media = [await create_equipment_media(equipment, media) for media in create_form.photo_and_video]
    documents = [await create_equipment_document(equipment, document) for document in create_form.documents]

    return equipment
