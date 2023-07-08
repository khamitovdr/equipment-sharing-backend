import logging

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.equipment import EquipmentCreateForm, EquipmentSchema, EquipmentListSchema, EquipmentCategoryListSchema, EquipmentCategorySchema
from app.crud.equipment import create_equipment, get_equipment_by_id, get_equipment_categories, get_equipment_list, get_equipment_list, create_equipment_category


log = logging.getLogger("uvicorn")


router = APIRouter()


@router.post("/", response_model=EquipmentSchema)
async def create_equipment_(payload: EquipmentCreateForm = Depends()):

    from app.models.users import User
    user = await User.filter(email="johndoe@example.com").first()

    equipment = await create_equipment(payload, user)
    await equipment.fetch_related("category", "documents", "photo_and_video")
    log.info(f"Equipment created fetch_related: {list(equipment.photo_and_video)}")
    return equipment


@router.get("/{equipment_id}", response_model=EquipmentSchema)
async def get_equipment(equipment_id: int):
    equipment = await get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.get("/", response_model=list[EquipmentListSchema])
async def get_equipment_list_(category_id: int = None, organization_inn: str = None):
    equipment_list = await get_equipment_list(category_id, organization_inn)
    return equipment_list


@router.get("/categories/", response_model=list[EquipmentCategoryListSchema])
async def get_verified_equipment_categories_(organization_inn: str = None):
    categories = await get_equipment_categories(organization_inn)
    return categories


@router.post("/categories/", response_model=EquipmentCategorySchema)
async def create_equipment_category_(name: str):
    category = await create_equipment_category(name)
    return category
