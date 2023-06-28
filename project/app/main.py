import logging

from fastapi import FastAPI

from app.api import token, users, organizations
from app.db import init_db


log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(token.router, prefix="/token", tags=["auth token"])
    application.include_router(users.router, prefix="/users", tags=["users"])
    application.include_router(organizations.router, prefix="/organizations", tags=["organizations"])

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")


@app.get("/init_activities_db")
async def init_activities_db():
    from app.services.organizations import init_activities_db_table
    await init_activities_db_table()
    return {"message": "OK"}
