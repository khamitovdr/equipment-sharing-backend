import json

from app.crud.equipment import create_categories


async def init_equipment_categories_db_table():
    with open("app/data/equipment/categories.json", "r") as f:
        okveds = json.load(f)
        await create_categories(okveds["verified"], verified=True)
        await create_categories(okveds["users"])
