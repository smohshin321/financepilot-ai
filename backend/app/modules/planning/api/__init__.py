from app.modules.planning.api.budget_lines import router as budget_line_router
from app.modules.planning.api.budget_versions import router as budget_version_router
from app.modules.planning.api.planning_cycles import router as planning_cycle_router
from app.modules.planning.api.scenarios import router as scenario_router
from fastapi import APIRouter

planning_router = APIRouter()

planning_router.include_router(planning_cycle_router)
planning_router.include_router(scenario_router)
planning_router.include_router(budget_version_router)
planning_router.include_router(budget_line_router)

__all__ = ["planning_router"]
