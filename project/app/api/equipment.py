import logging

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.equipment import EquipmentCreateForm, EquipmentSchema
from app.crud.equipment import create_equipment


log = logging.getLogger("uvicorn")


router = APIRouter()


@router.post("/", response_model=EquipmentSchema)
async def submit(payload: EquipmentCreateForm = Depends()):

    from app.models.users import User
    user = await User.filter(email="johndoe@example.com").first()

    equipment = await create_equipment(payload, user)
    await equipment.fetch_related("category", "documents", "photo_and_video")
    log.info(f"Equipment created fetch_related: {list(equipment.photo_and_video)}")
    return equipment
