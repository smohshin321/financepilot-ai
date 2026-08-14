from uuid import UUID

from app.modules.identity.api.dependencies import CurrentUserDependency
from app.modules.planning.api.authorization import (
    require_budget_read,
    require_budget_write,
)
from app.modules.planning.api.dependencies import (
    BudgetLineServiceDependency,
    BudgetVersionServiceDependency,
    PlanningCycleServiceDependency,
    ScenarioServiceDependency,
)
from app.modules.planning.exceptions import (
    BudgetLineNotFoundError,
    BudgetVersionLockedError,
    BudgetVersionNotFoundError,
    PlanningCycleNotFoundError,
)
from app.modules.planning.models import BudgetLine
from app.modules.planning.schemas import (
    BudgetLineCreate,
    BudgetLineResponse,
    BudgetLineUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(
    prefix=(
        "/planning-cycles/{planning_cycle_id}"
        "/scenarios/{scenario_id}"
        "/budget-versions/{budget_version_id}"
        "/budget-lines"
    ),
    tags=["Planning"],
)


async def ensure_budget_version_scope(
    *,
    planning_cycle_id: UUID,
    scenario_id: UUID,
    budget_version_id: UUID,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    budget_version_service: BudgetVersionServiceDependency,
) -> None:
    """Validate the full organization-to-budget-version ownership chain."""

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

    try:
        await budget_version_service.get(
            budget_version_id=budget_version_id,
            scenario_id=scenario_id,
        )
    except BudgetVersionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget version not found.",
        ) from error


@router.post(
    "",
    response_model=BudgetLineResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_budget_line(
    planning_cycle_id: UUID,
    scenario_id: UUID,
    budget_version_id: UUID,
    payload: BudgetLineCreate,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    budget_version_service: BudgetVersionServiceDependency,
    budget_line_service: BudgetLineServiceDependency,
    _: None = Depends(require_budget_write),
) -> BudgetLineResponse:
    """Create a budget line within an authorized budget version."""

    await ensure_budget_version_scope(
        planning_cycle_id=planning_cycle_id,
        scenario_id=scenario_id,
        budget_version_id=budget_version_id,
        current_user=current_user,
        planning_cycle_service=planning_cycle_service,
        scenario_service=scenario_service,
        budget_version_service=budget_version_service,
    )

    budget_line = BudgetLine(
        budget_version_id=budget_version_id,
        account_id=payload.account_id,
        department_id=payload.department_id,
        cost_center_id=payload.cost_center_id,
        period=payload.period,
        amount=payload.amount,
        currency=payload.currency.upper(),
        notes=payload.notes.strip() if payload.notes else None,
    )

    created = await budget_line_service.create(budget_line)

    return BudgetLineResponse.model_validate(created)


@router.get(
    "",
    response_model=list[BudgetLineResponse],
)
async def list_budget_lines(
    planning_cycle_id: UUID,
    scenario_id: UUID,
    budget_version_id: UUID,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    budget_version_service: BudgetVersionServiceDependency,
    budget_line_service: BudgetLineServiceDependency,
    _: None = Depends(require_budget_read),
) -> list[BudgetLineResponse]:
    """List budget lines within an authorized budget version."""

    await ensure_budget_version_scope(
        planning_cycle_id=planning_cycle_id,
        scenario_id=scenario_id,
        budget_version_id=budget_version_id,
        current_user=current_user,
        planning_cycle_service=planning_cycle_service,
        scenario_service=scenario_service,
        budget_version_service=budget_version_service,
    )

    lines = await budget_line_service.list_for_budget_version(budget_version_id)

    return [BudgetLineResponse.model_validate(line) for line in lines]


@router.get(
    "/{budget_line_id}",
    response_model=BudgetLineResponse,
)
async def get_budget_line(
    planning_cycle_id: UUID,
    scenario_id: UUID,
    budget_version_id: UUID,
    budget_line_id: UUID,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    budget_version_service: BudgetVersionServiceDependency,
    budget_line_service: BudgetLineServiceDependency,
    _: None = Depends(require_budget_read),
) -> BudgetLineResponse:
    """Return a budget line within an authorized budget version."""

    await ensure_budget_version_scope(
        planning_cycle_id=planning_cycle_id,
        scenario_id=scenario_id,
        budget_version_id=budget_version_id,
        current_user=current_user,
        planning_cycle_service=planning_cycle_service,
        scenario_service=scenario_service,
        budget_version_service=budget_version_service,
    )

    try:
        budget_line = await budget_line_service.get(
            budget_line_id=budget_line_id,
            budget_version_id=budget_version_id,
        )
    except BudgetLineNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget line not found.",
        ) from error

    return BudgetLineResponse.model_validate(budget_line)


@router.put(
    "/{budget_line_id}",
    response_model=BudgetLineResponse,
)
async def update_budget_line(
    planning_cycle_id: UUID,
    scenario_id: UUID,
    budget_version_id: UUID,
    budget_line_id: UUID,
    payload: BudgetLineUpdate,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    budget_version_service: BudgetVersionServiceDependency,
    budget_line_service: BudgetLineServiceDependency,
    _: None = Depends(require_budget_write),
) -> BudgetLineResponse:
    """Update a budget line within an authorized and editable version."""

    await ensure_budget_version_scope(
        planning_cycle_id=planning_cycle_id,
        scenario_id=scenario_id,
        budget_version_id=budget_version_id,
        current_user=current_user,
        planning_cycle_service=planning_cycle_service,
        scenario_service=scenario_service,
        budget_version_service=budget_version_service,
    )

    try:
        budget_version = await budget_version_service.get(
            budget_version_id=budget_version_id,
            scenario_id=scenario_id,
        )

        budget_version_service.validate_editable(budget_version)

        budget_line = await budget_line_service.get(
            budget_line_id=budget_line_id,
            budget_version_id=budget_version_id,
        )
    except BudgetLineNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget line not found.",
        ) from error
    except BudgetVersionLockedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Budget version is locked.",
        ) from error

    budget_line.account_id = payload.account_id
    budget_line.department_id = payload.department_id
    budget_line.cost_center_id = payload.cost_center_id
    budget_line.period = payload.period
    budget_line.amount = payload.amount
    budget_line.currency = payload.currency.upper()
    budget_line.notes = payload.notes.strip() if payload.notes else None

    updated = await budget_line_service.update(budget_line)

    return BudgetLineResponse.model_validate(updated)


@router.delete(
    "/{budget_line_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_budget_line(
    planning_cycle_id: UUID,
    scenario_id: UUID,
    budget_version_id: UUID,
    budget_line_id: UUID,
    current_user: CurrentUserDependency,
    planning_cycle_service: PlanningCycleServiceDependency,
    scenario_service: ScenarioServiceDependency,
    budget_version_service: BudgetVersionServiceDependency,
    budget_line_service: BudgetLineServiceDependency,
    _: None = Depends(require_budget_write),
) -> None:
    """Delete a budget line from an authorized and editable version."""

    await ensure_budget_version_scope(
        planning_cycle_id=planning_cycle_id,
        scenario_id=scenario_id,
        budget_version_id=budget_version_id,
        current_user=current_user,
        planning_cycle_service=planning_cycle_service,
        scenario_service=scenario_service,
        budget_version_service=budget_version_service,
    )

    try:
        budget_version = await budget_version_service.get(
            budget_version_id=budget_version_id,
            scenario_id=scenario_id,
        )

        budget_version_service.validate_editable(budget_version)

        await budget_line_service.delete(
            budget_line_id=budget_line_id,
            budget_version_id=budget_version_id,
        )
    except BudgetLineNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget line not found.",
        ) from error
    except BudgetVersionLockedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Budget version is locked.",
        ) from error
