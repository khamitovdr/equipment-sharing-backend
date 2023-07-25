import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.equipment import EquipmentStatus, EquipmentStatusUpdate
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.equipment import EquipmentCreateForm, EquipmentSchema, EquipmentListSchema, EquipmentCategoryListSchema, EquipmentCategorySchema
from app.crud.equipment import create_equipment, get_equipment_by_id, get_equipment_categories, get_equipment_list, get_equipment_list, create_equipment_category, update_equipment_status
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
    '''Create new equipment item for current organization'''
    try:
        equipment = await create_equipment(payload, current_user)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    
    await equipment.fetch_related("category", "documents", "photo_and_video")
    return equipment


@router.get("/", response_model=list[EquipmentListSchema])
async def get_equipment_list_(category_id: int = None, organization_inn: str = None):
    '''Get list of equipment to rent (all, by category or from particular organization)'''
    equipment_list = await get_equipment_list(organization_inn, category_id, EquipmentStatus.PUBLISHED)
    return equipment_list


@router.get("/my-organization/", response_model=list[EquipmentListSchema])
async def get_organization_equipment_list_(organization: Organization = Depends(get_current_verified_organization)):
    '''Get list of equipment of current organization'''
    equipment_list = await get_equipment_list(organization.inn)
    return equipment_list


@router.get("/categories/", response_model=list[EquipmentCategoryListSchema])
async def get_equipment_categories_(organization_inn: str = None):
    '''Get list of equipment categories (all or from particular organization)'''
    categories = await get_equipment_categories(organization_inn)
    return categories


@router.post("/categories/", response_model=EquipmentCategorySchema)
async def create_equipment_category_(
    name: str,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_verified_organization)
    ):
    '''Create new equipment category for current organization'''
    category = await create_equipment_category(name, current_user)
    return category


@router.get("/{equipment_id}/", response_model=EquipmentSchema)
async def get_equipment(equipment_id: int):
    '''Get equipment item by id'''
    equipment = await get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.put("/{equipment_id}/status/", response_model=EquipmentSchema)
async def change_equipment_status(
    equipment_id: int,
    status: EquipmentStatusUpdate,
    organization: Organization = Depends(get_current_verified_organization),
    ):
    '''Change equipment availability status'''
    equipment = await get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.added_by.organization.inn != organization.inn:
        raise HTTPException(status_code=403, detail="You don't have permission to change equipment status")
    
    log.info(f"Updating equipment status: {equipment} to {status.value}")

    status = EquipmentStatus(status.value)
    equipment = await update_equipment_status(equipment, status)
    return equipment
