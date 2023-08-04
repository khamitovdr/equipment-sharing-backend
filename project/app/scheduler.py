import asyncio
import logging

from rocketry import Rocketry

log = logging.getLogger("uvicorn")

app = Rocketry(config={"task_execution": "async"})


async def start():
    """Start the scheduler"""
    log.info("Starting up Rocketry scheduler")

    # hook the rocketry scheduler into the FastAPI event loop
    fastapi_event_loop = asyncio.get_running_loop()
    fastapi_event_loop.create_task(app.serve())


async def stop():
    """Stop the scheduler"""
    log.info("Stopping Rocketry scheduler")
    app.session.shut_down()
