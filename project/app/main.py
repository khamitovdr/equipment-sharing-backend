import logging

from fastapi import FastAPI

from app.api import token, users
from app.db import init_db
from app.fns.api import router as fns_router

log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(token.router, prefix="/token", tags=["auth token"])
    application.include_router(users.router, prefix="/users", tags=["users"])
    application.include_router(fns_router, prefix="/fns", tags=["fns"])

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
