from fastapi import APIRouter
from app.schemas.common import APIResponse
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    return APIResponse.ok(
        data={"status": "ok", "version": settings.APP_VERSION, "app": settings.APP_NAME},
        message="Service is healthy",
    )


@router.get("/ready")
async def readiness_check():
    return APIResponse.ok(
        data={"status": "ready", "database": "connected"},
        message="Service is ready",
    )
