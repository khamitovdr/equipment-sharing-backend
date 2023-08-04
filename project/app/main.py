import logging

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app import scheduler
from app.api import equipment, notifications, orders, organizations, token, users
from app.db import init_db
from app.db_signals import files_signals, orders_signals  # noqa: F401

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
    await scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
    await scheduler.stop()


# Swagger ui dark theme
@app.get("/docs-dark", include_in_schema=False)
async def custom_swagger_ui_html_cdn():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        # swagger_ui_dark.css CDN link
        swagger_css_url="https://cdn.jsdelivr.net/gh/Itz-fork/Fastapi-Swagger-UI-Dark/assets/swagger_ui_dark.min.css",
    )


@app.get("/fill_db")
async def init_activities_db():
    """Fill new database with activities and equipment categories"""
    from app.services.equipment import init_equipment_categories_db_table
    from app.services.organizations import init_activities_db_table

    await init_activities_db_table()
    await init_equipment_categories_db_table()

    return {"message": "OK"}
