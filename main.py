import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pymongo.errors import PyMongoError
from config.logging import logger
from routes import blog_routes, health_routes, user_routes
from services.user_services import ensure_indexes

FRONTEND_DIR = "client_build"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Start even when MongoDB is down or holds duplicate emails: /health reports the outage
    # and the duplicate check in create_user still applies without the index
    try:
        ensure_indexes()
    except PyMongoError as e:
        logger.warning("Could not create the unique email index", extra={"error": str(e)})
    yield


app = FastAPI(title="DevOps AWS FARM", lifespan=lifespan)

app.include_router(health_routes.router)
app.include_router(blog_routes.router)
app.include_router(user_routes.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
        },
    )
    return response


# Serve the built React app when it exists; without it the API still runs (tests, API-only dev)
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    logger.warning(
        "client_build/ not found, serving the API only (run npm run build in client/)"
    )
