import json

from app.crud.equipment import create_categories, get_equipment_categories
from app.scheduler import app as scheduler


@scheduler.task()
async def init_equipment_categories_db_table():
    if await get_equipment_categories():
        return

    with open("app/data/equipment/categories.json", "r") as f:
        categories = json.load(f)
        await create_categories(categories, verified=True)
