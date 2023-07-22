import logging

from fastapi import APIRouter, Depends, HTTPException

from app.models.equipment import EquipmentStatus
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.equipment import EquipmentCreateForm, EquipmentSchema, EquipmentListSchema, EquipmentCategoryListSchema, EquipmentCategorySchema
from app.crud.equipment import create_equipment, get_equipment_by_id, get_equipment_categories, get_equipment_list, get_equipment_list, create_equipment_category
from app.services.auth import get_current_active_user
from app.services.organizations import get_current_verified_organization


log = logging.getLogger("uvicorn")


router = APIRouter()


@router.post("/", response_model=EquipmentSchema)
async def create_equipment_(
    payload: EquipmentCreateForm = Depends(),
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_verified_organization)
    ):
    equipment = await create_equipment(payload, current_user)
    await equipment.fetch_related("category", "documents", "photo_and_video")
    log.info(f"Equipment created fetch_related: {list(equipment.photo_and_video)}")
    return equipment


@router.get("/", response_model=list[EquipmentListSchema])
async def get_equipment_list_(category_id: int = None, organization_inn: str = None):
    equipment_list = await get_equipment_list(organization_inn, category_id)
    return equipment_list


@router.get("/categories/", response_model=list[EquipmentCategoryListSchema])
async def get_equipment_categories_(organization_inn: str = None):
    categories = await get_equipment_categories(organization_inn)
    return categories


@router.post("/categories/", response_model=EquipmentCategorySchema)
async def create_equipment_category_(
    name: str,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_verified_organization)
    ):
    category = await create_equipment_category(name, current_user)
    return category


@router.get("/{equipment_id}/", response_model=EquipmentSchema)
async def get_equipment(equipment_id: int):
    equipment = await get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.put("/{equipment_id}/status/")
async def change_equipment_status(
    equipment_id: int,
    status: EquipmentStatus,
    organization: Organization = Depends(get_current_verified_organization),
    ):
    equipment = await get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.added_by.organization.inn != organization.inn:
        raise HTTPException(status_code=403, detail="You don't have permission to change equipment status")
    
    log.info(f"Updating equipment status: {equipment} to {status.value}")
    equipment.status = status
    await equipment.save()
    return {"new_status": status.value}
