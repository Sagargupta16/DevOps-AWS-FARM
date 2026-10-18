from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from config.secrets_parser import ping_database
from config.logging import logger

router = APIRouter()


@router.get(
    "/health",
    tags=["health"],
    responses={503: {"description": "MongoDB did not answer a ping"}},
)
def health_route():
    """Liveness and readiness in one: 200 only when MongoDB answers a ping."""
    # The Docker HEALTHCHECK, the compose healthcheck and the ECS/ALB target group all call this
    try:
        ping_database()
    except PyMongoError as e:
        logger.warning("Health check failed", extra={"error": type(e).__name__})
        return JSONResponse(
            status_code=503, content={"status": "unavailable", "database": "down"}
        )
    return {"status": "ok", "database": "up"}
