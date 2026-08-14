from typing import Annotated

from app.core.database import get_db_session
from app.modules.planning.repositories import (
    BudgetLineRepository,
    BudgetVersionRepository,
    PlanningCycleRepository,
    ScenarioRepository,
)
from app.modules.planning.services import (
    BudgetLineService,
    BudgetVersionService,
    PlanningCycleService,
    ScenarioService,
)
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_planning_cycle_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PlanningCycleService:
    """Build the planning-cycle service for the current request."""

    return PlanningCycleService(
        planning_cycle_repository=PlanningCycleRepository(session),
    )


def get_scenario_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ScenarioService:
    """Build the scenario service for the current request."""

    return ScenarioService(
        scenario_repository=ScenarioRepository(session),
    )


PlanningCycleServiceDependency = Annotated[
    PlanningCycleService,
    Depends(get_planning_cycle_service),
]

ScenarioServiceDependency = Annotated[
    ScenarioService,
    Depends(get_scenario_service),
]


def get_budget_version_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> BudgetVersionService:
    """Build the budget-version service for the current request."""

    return BudgetVersionService(
        repository=BudgetVersionRepository(session),
    )


BudgetVersionServiceDependency = Annotated[
    BudgetVersionService,
    Depends(get_budget_version_service),
]


def get_budget_line_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> BudgetLineService:
    """Build the budget-line service for the current request."""

    return BudgetLineService(
        repository=BudgetLineRepository(session),
    )


BudgetLineServiceDependency = Annotated[
    BudgetLineService,
    Depends(get_budget_line_service),
]
