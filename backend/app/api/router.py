from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.modules.identity.api import identity_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(identity_router)
