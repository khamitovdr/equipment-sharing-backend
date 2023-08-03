import asyncio
import logging
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from app.api import equipment, notifications, orders, organizations, token, users
from app.db import init_db
from app.db_signals import files_signals, orders_signals  # noqa: F401
from app.scheduler import app as app_rocketry

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


# swagger ui dark theme
@app.get("/docs-dark", include_in_schema=False)
async def custom_swagger_ui_html_cdn():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        # swagger_ui_dark.css CDN link
        swagger_css_url="https://cdn.jsdelivr.net/gh/Itz-fork/Fastapi-Swagger-UI-Dark/assets/swagger_ui_dark.min.css",
    )


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")


@app.get("/fill_db")
async def init_activities_db():
    """Fill new database with activities and equipment categories"""
    from app.services.equipment import init_equipment_categories_db_table
    from app.services.organizations import init_activities_db_table

    await init_activities_db_table()
    await init_equipment_categories_db_table()

    return {"message": "OK"}


class Server(uvicorn.Server):
    """Customized uvicorn.Server

    Uvicorn server overrides signals and we need to include
    Rocketry to the signals."""

    def handle_exit(self, sig: int, frame) -> None:
        app_rocketry.session.shut_down()
        return super().handle_exit(sig, frame)


async def main():
    "Run scheduler and the API"

    # https://www.uvicorn.org/settings/
    server = Server(
        config=uvicorn.Config(
            app, workers=1, loop="asyncio", host="0.0.0.0", port=8000, reload=True, reload_dirs=["app"]
        )
    )

    api = asyncio.create_task(server.serve())
    sched = asyncio.create_task(app_rocketry.serve())

    await asyncio.wait([sched, api])


if __name__ == "__main__":
    asyncio.run(main())
