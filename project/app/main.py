import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import equipment, notifications, orders, organizations, token, users
from app.db import init_db
from app.db_signals import orders_signals

log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(token.router, prefix="/login", tags=["auth token"])
    application.include_router(users.router, prefix="/users", tags=["users"])
    application.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
    application.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
    application.include_router(orders.router, prefix="/orders", tags=["orders"])
    application.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

    application.mount("/static", StaticFiles(directory="static"), name="static")

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")


@app.get("/fill_db")
async def init_activities_db():
    from app.services.equipment import init_equipment_categories_db_table
    from app.services.organizations import init_activities_db_table

    await init_activities_db_table()
    await init_equipment_categories_db_table()

    return {"message": "OK"}
