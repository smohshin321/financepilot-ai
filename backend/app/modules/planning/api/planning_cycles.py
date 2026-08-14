from uuid import UUID

from app.modules.identity.api.dependencies import CurrentUserDependency
from app.modules.planning.api.authorization import (
    require_budget_read,
    require_budget_write,
)
from app.modules.planning.api.dependencies import PlanningCycleServiceDependency
from app.modules.planning.exceptions import PlanningCycleNotFoundError
from app.modules.planning.schemas import (
    PlanningCycleCreate,
    PlanningCycleResponse,
)
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(
    prefix="/planning-cycles",
    tags=["Planning"],
)


@router.post(
    "",
    response_model=PlanningCycleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_planning_cycle(
    payload: PlanningCycleCreate,
    current_user: CurrentUserDependency,
    service: PlanningCycleServiceDependency,
    _: None = Depends(require_budget_write),
) -> PlanningCycleResponse:
    """Create an organization-scoped planning cycle."""

    planning_cycle = await service.create(
        organization_id=current_user.organization_id,
        name=payload.name,
        description=payload.description,
        planning_type=payload.planning_type,
        fiscal_year=payload.fiscal_year,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )

    return PlanningCycleResponse.model_validate(planning_cycle)


@router.get(
    "",
    response_model=list[PlanningCycleResponse],
)
async def list_planning_cycles(
    current_user: CurrentUserDependency,
    service: PlanningCycleServiceDependency,
    _: None = Depends(require_budget_read),
) -> list[PlanningCycleResponse]:
    """List planning cycles for the authenticated organization."""

    planning_cycles = await service.list_for_organization(current_user.organization_id)

    return [
        PlanningCycleResponse.model_validate(planning_cycle) for planning_cycle in planning_cycles
    ]


@router.get(
    "/{planning_cycle_id}",
    response_model=PlanningCycleResponse,
)
async def get_planning_cycle(
    planning_cycle_id: UUID,
    current_user: CurrentUserDependency,
    service: PlanningCycleServiceDependency,
    _: None = Depends(require_budget_read),
) -> PlanningCycleResponse:
    """Return an organization-scoped planning cycle."""

    try:
        planning_cycle = await service.get(
            planning_cycle_id=planning_cycle_id,
            organization_id=current_user.organization_id,
        )
    except PlanningCycleNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planning cycle not found.",
        ) from error

    return PlanningCycleResponse.model_validate(planning_cycle)
