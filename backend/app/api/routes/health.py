from typing import Literal

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.database import database_is_ready, get_engine

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["healthy"]
    service: str
    version: str
    environment: str


class ReadinessResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    database: Literal["available", "unavailable"]


@router.get("/health", response_model=HealthResponse, summary="Service liveness check")
def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Service readiness check",
)
async def readiness_check(response: Response) -> ReadinessResponse:
    if await database_is_ready(get_engine()):
        return ReadinessResponse(status="ready", database="available")

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(status="not_ready", database="unavailable")
