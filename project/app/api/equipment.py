import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.crud.equipment import (
    create_equipment,
    create_equipment_category,
    delete_equipment,
    get_equipment_by_id,
    get_equipment_categories,
    get_equipment_list,
    get_equipment_list_added_by_user,
    update_equipment,
    update_equipment_status,
)
from app.crud.files import create_file, delete_file
from app.models.equipment import (
    EquipmentDocument,
    EquipmentMedia,
    EquipmentStatus,
    EquipmentStatusUpdate,
)
from app.models.organizations import Organization
from app.models.users import User
from app.schemas.equipment import (
    EquipmentCategoryListSchema,
    EquipmentCategorySchema,
    EquipmentCreateSchema,
    EquipmentListSchema,
    EquipmentSchema,
    EquipmentUpdateSchema,
)
from app.schemas.files import FileBaseSchema
from app.services.auth import get_current_active_user
from app.services.organizations import get_current_organization, get_current_verified_organization

log = logging.getLogger("uvicorn")


router = APIRouter()


@router.post("/", response_model=EquipmentSchema)
async def create_equipment_(
    create_schema: EquipmentCreateSchema,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
):
    """Create new equipment item for current organization"""
    try:
        equipment = await create_equipment(create_schema, current_user, organization)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))

    await equipment.fetch_related("organization", "category", "documents", "photo_and_video")
    return equipment


@router.put("/{equipment_id}/", response_model=EquipmentSchema)
async def update_equipment_(
    equipment_id: int,
    update_schema: EquipmentUpdateSchema,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
):
    """Update equipment item"""
    equipment = await get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    if (
            equipment.organization != organization or
            not current_user.is_verified_organization_member and equipment.added_by != current_user
        ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to update equipment"
        )

    equipment = await update_equipment(equipment, update_schema)
    return equipment


@router.delete("/{equipment_id}/")
async def delete_equipment_(
    equipment_id: int,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Delete equipment item"""
    equipment = await get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    if equipment.organization != organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete equipment"
        )

    await delete_equipment(equipment)


@router.post("/document/", response_model=FileBaseSchema)
async def upload_equipment_document(
    document: UploadFile,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Upload equipment document"""
    file = await create_file(document, EquipmentDocument)
    return file


@router.delete("/document/{document_id}/")
async def delete_equipment_document(
    document_id: int,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Delete equipment document"""
    await delete_file(document_id, EquipmentDocument)


@router.post("/media/", response_model=FileBaseSchema)
async def upload_equipment_media(
    media: UploadFile,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Upload equipment media"""
    file = await create_file(media, EquipmentMedia)
    return file


@router.delete("/media/{media_id}/")
async def delete_equipment_media(
    media_id: int,
    organization: Organization = Depends(get_current_verified_organization),
):
    """Delete equipment media"""
    await delete_file(media_id, EquipmentMedia)


@router.get("/", response_model=EquipmentListSchema)
async def get_equipment_list_(
    category_id: int = None,
    organization_inn: str = None,
    offset: int = 0,
    limit: int = 40,
):
    """Get list of equipment to rent (all, by category or from particular organization)"""
    equipment_list = await get_equipment_list(
        organization_inn, category_id, EquipmentStatus.PUBLISHED, offset=offset, limit=limit
    )
    return equipment_list


@router.get("/my-organization/", response_model=EquipmentListSchema)
async def get_organization_equipment_list_(
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    offset: int = 0,
    limit: int = 40,
):
    """Get list of equipment of current organization"""
    if current_user.is_verified_organization_member:
        equipment_list = await get_equipment_list(organization.inn, offset=offset, limit=limit)
    else:
        equipment_list = await get_equipment_list_added_by_user(current_user, offset=offset, limit=limit)

    return equipment_list


@router.get("/me/", response_model=EquipmentListSchema)
async def get_organization_equipment_list_(
    current_user: User = Depends(get_current_active_user),
    offset: int = 0,
    limit: int = 40,
):
    """Get list of equipment added by current user"""
    equipment_list = await get_equipment_list_added_by_user(current_user, offset=offset, limit=limit)
    return equipment_list


@router.get("/categories/", response_model=EquipmentCategoryListSchema)
async def get_equipment_categories_(organization_inn: str = None):
    """Get list of equipment categories (all or from particular organization)"""
    categories = await get_equipment_categories(organization_inn)
    return categories


@router.post("/categories/", response_model=EquipmentCategorySchema, status_code=status.HTTP_201_CREATED)
async def create_equipment_category_(
    name: str,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_verified_organization),
):
    """Create new equipment category for current organization"""
    category = await create_equipment_category(name, current_user)
    return category


@router.get("/{equipment_id}/", response_model=EquipmentSchema)
async def get_equipment(equipment_id: int):
    """Get equipment item by id"""
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
    """Change equipment availability status"""
    equipment = await get_equipment_by_id(equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.organization.inn != organization.inn:
        raise HTTPException(status_code=403, detail="You don't have permission to change equipment status")

    log.info(f"Updating equipment status: {equipment} to {status.value}")

    status = EquipmentStatus(status.value)
    equipment = await update_equipment_status(equipment, status)
    return equipment


@router.get("/fill_equipment_categories_db_table")
async def init_equipment_categories_db_table_():
    """Fill new database with activities and equipment categories"""
    from app.services.equipment import init_equipment_categories_db_table

    await init_equipment_categories_db_table()
    return {"message": "OK"}
