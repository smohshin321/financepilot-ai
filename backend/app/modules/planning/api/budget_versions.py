from uuid import UUID

from app.modules.identity.api.dependencies import CurrentUserDependency
from app.modules.planning.api.authorization import (
    require_budget_manage,
    require_budget_read,
    require_budget_write,
)
from app.modules.planning.api.dependencies import (
    BudgetVersionServiceDependency,
    PlanningCycleServiceDependency,
    ScenarioServiceDependency,
)
from app.modules.planning.exceptions import (
    BudgetVersionNotFoundError,
    PlanningCycleNotFoundError,
)
from app.modules.planning.models import BudgetVersion
from app.modules.planning.schemas import (
    BudgetVersionCreate,
    BudgetVersionResponse,
)
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(
    prefix=("/planning-cycles/{planning_cycle_id}/scenarios/{scenario_id}/budget-versions"),
    tags=["Planning"],
)


async def ensure_scenario_scope(
    *,
    planning_cycle_id: UUID,
    scenario_id: UUID,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
) -> None:
    """Validate organization, planning-cycle, and scenario ownership."""

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


@router.post(
    "",
    response_model=BudgetVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_budget_version(
    planning_cycle_id: UUID,
    scenario_id: UUID,
    payload: BudgetVersionCreate,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    budget_version_service: BudgetVersionServiceDependency,
    _: None = Depends(require_budget_write),
) -> BudgetVersionResponse:
    """Create a budget version within an authorized scenario."""

    await ensure_scenario_scope(
        planning_cycle_id=planning_cycle_id,
        scenario_id=scenario_id,
        current_user=current_user,
        planning_cycle_service=planning_cycle_service,
        scenario_service=scenario_service,
    )

    budget_version = BudgetVersion(
        scenario_id=scenario_id,
        version_number=payload.version_number,
        version_name=payload.version_name.strip(),
        description=payload.description.strip() if payload.description else None,
        is_active=True,
        is_locked=False,
    )

    created = await budget_version_service.create(budget_version)

    return BudgetVersionResponse.model_validate(created)


@router.get(
    "",
    response_model=list[BudgetVersionResponse],
)
async def list_budget_versions(
    planning_cycle_id: UUID,
    scenario_id: UUID,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    budget_version_service: BudgetVersionServiceDependency,
    _: None = Depends(require_budget_read),
) -> list[BudgetVersionResponse]:
    """List budget versions within an authorized scenario."""

    await ensure_scenario_scope(
        planning_cycle_id=planning_cycle_id,
        scenario_id=scenario_id,
        current_user=current_user,
        planning_cycle_service=planning_cycle_service,
        scenario_service=scenario_service,
    )

    versions = await budget_version_service.list_for_scenario(scenario_id)

    return [BudgetVersionResponse.model_validate(version) for version in versions]


@router.get(
    "/{budget_version_id}",
    response_model=BudgetVersionResponse,
)
async def get_budget_version(
    planning_cycle_id: UUID,
    scenario_id: UUID,
    budget_version_id: UUID,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    budget_version_service: BudgetVersionServiceDependency,
    _: None = Depends(require_budget_read),
) -> BudgetVersionResponse:
    """Return a budget version within an authorized scenario."""

    await ensure_scenario_scope(
        planning_cycle_id=planning_cycle_id,
        scenario_id=scenario_id,
        current_user=current_user,
        planning_cycle_service=planning_cycle_service,
        scenario_service=scenario_service,
    )

    try:
        budget_version = await budget_version_service.get(
            budget_version_id=budget_version_id,
            scenario_id=scenario_id,
        )
    except BudgetVersionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget version not found.",
        ) from error

    return BudgetVersionResponse.model_validate(budget_version)


@router.post(
    "/{budget_version_id}/activate",
    response_model=BudgetVersionResponse,
)
async def activate_budget_version(
    planning_cycle_id: UUID,
    scenario_id: UUID,
    budget_version_id: UUID,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    budget_version_service: BudgetVersionServiceDependency,
    _: None = Depends(require_budget_manage),
) -> BudgetVersionResponse:
    """Activate a budget version."""

    await ensure_scenario_scope(
        planning_cycle_id=planning_cycle_id,
        scenario_id=scenario_id,
        current_user=current_user,
        planning_cycle_service=planning_cycle_service,
        scenario_service=scenario_service,
    )

    try:
        version = await budget_version_service.activate(
            budget_version_id=budget_version_id,
            scenario_id=scenario_id,
        )
    except BudgetVersionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget version not found.",
        ) from error

    return BudgetVersionResponse.model_validate(version)


@router.post(
    "/{budget_version_id}/lock",
    response_model=BudgetVersionResponse,
)
async def lock_budget_version(
    planning_cycle_id: UUID,
    scenario_id: UUID,
    budget_version_id: UUID,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    budget_version_service: BudgetVersionServiceDependency,
    _: None = Depends(require_budget_manage),
) -> BudgetVersionResponse:
    """Lock a budget version."""

    await ensure_scenario_scope(
        planning_cycle_id=planning_cycle_id,
        scenario_id=scenario_id,
        current_user=current_user,
        planning_cycle_service=planning_cycle_service,
        scenario_service=scenario_service,
    )

    try:
        version = await budget_version_service.lock(
            budget_version_id=budget_version_id,
            scenario_id=scenario_id,
        )
    except BudgetVersionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget version not found.",
        ) from error

    return BudgetVersionResponse.model_validate(version)
