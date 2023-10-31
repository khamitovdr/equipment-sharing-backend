import logging

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
import sentry_sdk

from app import scheduler
from app.api import (
    equipment,
    notifications,
    orders,
    organizations,
    reviews,
    token,
    users,
    order_process_renter,
    order_process_owner,
    payments,
)
from app.config import get_settings
from app.db import init_db
from app.db_signals import files_signals, orders_signals  # noqa: F401
from app.services.equipment import init_equipment_categories_db_table

log = logging.getLogger("uvicorn")

sentry_sdk.init(
    dsn=get_settings().sentry_dsn,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    send_default_pii=True # send user data (id, email, ip, etc.)
)

def create_application() -> FastAPI:
    application = FastAPI(title="Equipment sharing service")
    application.include_router(token.router, prefix="/login", tags=["auth token"])
    application.include_router(users.router, prefix="/users", tags=["users"])
    application.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
    application.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
    application.include_router(orders.router, prefix="/orders", tags=["orders"])
    application.include_router(order_process_renter.router, prefix="/renter/orders", tags=["order renter process"])
    application.include_router(order_process_owner.router, prefix="/owner/orders", tags=["order owner process"])
    application.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
    application.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
    application.include_router(payments.router, prefix="/payments", tags=["payments"])

    application.mount("/static", StaticFiles(directory=get_settings().static_dir), name="static")

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(app)
    await scheduler.start()

    session = scheduler.app.session
    task = session[init_equipment_categories_db_table]
    task.run()


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
    await scheduler.stop()
