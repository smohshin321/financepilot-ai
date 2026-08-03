from datetime import date
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from app.modules.planning.exceptions import (
    InvalidFiscalYearError,
    InvalidPlanningCycleDateRangeError,
    PlanningCycleNotFoundError,
)
from app.modules.planning.models import (
    PlanningCycle,
    PlanningStatus,
    PlanningType,
)
from app.modules.planning.repositories import PlanningCycleRepository
from app.modules.planning.services import PlanningCycleService


def build_service() -> tuple[PlanningCycleService, AsyncMock]:
    repository = AsyncMock(spec=PlanningCycleRepository)
    service = PlanningCycleService(repository)

    return service, repository


@pytest.mark.asyncio
async def test_create_returns_persisted_planning_cycle() -> None:
    service, repository = build_service()
    organization_id = uuid4()

    repository.add.side_effect = lambda planning_cycle: planning_cycle

    planning_cycle = await service.create(
        organization_id=organization_id,
        name="  FY2027 Budget  ",
        description="  Annual operating plan  ",
        planning_type=PlanningType.BUDGET,
        fiscal_year=2027,
        start_date=date(2027, 1, 1),
        end_date=date(2027, 12, 31),
    )

    assert planning_cycle.organization_id == organization_id
    assert planning_cycle.name == "FY2027 Budget"
    assert planning_cycle.description == "Annual operating plan"
    assert planning_cycle.planning_type is PlanningType.BUDGET
    assert planning_cycle.fiscal_year == 2027
    assert planning_cycle.status is PlanningStatus.DRAFT
    assert planning_cycle.is_active is True

    repository.add.assert_awaited_once_with(planning_cycle)


@pytest.mark.asyncio
async def test_create_rejects_invalid_date_range() -> None:
    service, repository = build_service()

    with pytest.raises(InvalidPlanningCycleDateRangeError):
        await service.create(
            organization_id=uuid4(),
            name="Invalid Cycle",
            planning_type=PlanningType.BUDGET,
            fiscal_year=2027,
            start_date=date(2027, 12, 31),
            end_date=date(2027, 1, 1),
        )

    repository.add.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("fiscal_year", [1999, 2201])
async def test_create_rejects_unsupported_fiscal_year(
    fiscal_year: int,
) -> None:
    service, repository = build_service()

    with pytest.raises(InvalidFiscalYearError):
        await service.create(
            organization_id=uuid4(),
            name="Invalid Fiscal Year",
            planning_type=PlanningType.BUDGET,
            fiscal_year=fiscal_year,
            start_date=date(2027, 1, 1),
            end_date=date(2027, 12, 31),
        )

    repository.add.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_returns_planning_cycle() -> None:
    service, repository = build_service()
    planning_cycle_id = uuid4()
    organization_id = uuid4()
    planning_cycle = Mock(spec=PlanningCycle)

    repository.get_by_id.return_value = planning_cycle

    returned = await service.get(
        planning_cycle_id=planning_cycle_id,
        organization_id=organization_id,
    )

    assert returned is planning_cycle

    repository.get_by_id.assert_awaited_once_with(
        planning_cycle_id=planning_cycle_id,
        organization_id=organization_id,
    )


@pytest.mark.asyncio
async def test_get_raises_when_planning_cycle_not_found() -> None:
    service, repository = build_service()

    repository.get_by_id.return_value = None

    with pytest.raises(PlanningCycleNotFoundError):
        await service.get(
            planning_cycle_id=uuid4(),
            organization_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_list_for_organization_returns_repository_values() -> None:
    service, repository = build_service()
    organization_id = uuid4()
    planning_cycles = [
        Mock(spec=PlanningCycle),
        Mock(spec=PlanningCycle),
    ]

    repository.list_for_organization.return_value = planning_cycles

    returned = await service.list_for_organization(organization_id)

    assert returned == planning_cycles

    repository.list_for_organization.assert_awaited_once_with(organization_id)
