from uuid import UUID

from app.modules.identity.api.dependencies import CurrentUserDependency
from app.modules.planning.api.authorization import (
    require_budget_manage,
    require_budget_read,
    require_budget_write,
)
from app.modules.planning.api.dependencies import (
    PlanningCycleServiceDependency,
    ScenarioServiceDependency,
)
from app.modules.planning.exceptions import PlanningCycleNotFoundError
from app.modules.planning.models import Scenario
from app.modules.planning.schemas import ScenarioCreate, ScenarioResponse
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(
    prefix="/planning-cycles/{planning_cycle_id}/scenarios",
    tags=["Planning"],
)


@router.post(
    "",
    response_model=ScenarioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_scenario(
    planning_cycle_id: UUID,
    payload: ScenarioCreate,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    _: None = Depends(require_budget_write),
) -> ScenarioResponse:
    """Create a scenario within an organization-scoped planning cycle."""

    try:
        await planning_cycle_service.get(
            planning_cycle_id=planning_cycle_id,
            organization_id=current_user.organization_id,
        )
    except PlanningCycleNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planning cycle not found.",
        ) from error

    scenario = Scenario(
        planning_cycle_id=planning_cycle_id,
        code=payload.code.strip(),
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
        is_default=payload.is_default,
        is_active=True,
    )

    created = await scenario_service.create(scenario)

    return ScenarioResponse.model_validate(created)


@router.get(
    "",
    response_model=list[ScenarioResponse],
)
async def list_scenarios(
    planning_cycle_id: UUID,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    _: None = Depends(require_budget_read),
) -> list[ScenarioResponse]:
    """List active scenarios within an organization-scoped planning cycle."""

    try:
        await planning_cycle_service.get(
            planning_cycle_id=planning_cycle_id,
            organization_id=current_user.organization_id,
        )
    except PlanningCycleNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planning cycle not found.",
        ) from error

    scenarios = await scenario_service.list_for_planning_cycle(planning_cycle_id)

    return [ScenarioResponse.model_validate(scenario) for scenario in scenarios]


@router.get(
    "/{scenario_id}",
    response_model=ScenarioResponse,
)
async def get_scenario(
    planning_cycle_id: UUID,
    scenario_id: UUID,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    _: None = Depends(require_budget_read),
) -> ScenarioResponse:
    """Return a scenario within an organization-scoped planning cycle."""

    try:
        await planning_cycle_service.get(
            planning_cycle_id=planning_cycle_id,
            organization_id=current_user.organization_id,
        )
    except PlanningCycleNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planning cycle not found.",
        ) from error

    scenario = await scenario_service.get(
        scenario_id=scenario_id,
        planning_cycle_id=planning_cycle_id,
    )

    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found.",
        )

    return ScenarioResponse.model_validate(scenario)


@router.post(
    "/{scenario_id}/set-default",
    response_model=ScenarioResponse,
)
async def set_default_scenario(
    planning_cycle_id: UUID,
    scenario_id: UUID,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    _: None = Depends(require_budget_manage),
) -> ScenarioResponse:
    """Set the default scenario for an organization-scoped planning cycle."""

    try:
        await planning_cycle_service.get(
            planning_cycle_id=planning_cycle_id,
            organization_id=current_user.organization_id,
        )
    except PlanningCycleNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planning cycle not found.",
        ) from error

    scenario = await scenario_service.set_default(
        scenario_id=scenario_id,
        planning_cycle_id=planning_cycle_id,
    )

    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found.",
        )

    return ScenarioResponse.model_validate(scenario)
