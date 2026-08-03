from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from app.modules.planning.models import PlanningCycle
from app.modules.planning.repositories import PlanningCycleRepository
from sqlalchemy.ext.asyncio import AsyncSession


def build_repository() -> tuple[PlanningCycleRepository, AsyncMock]:
    session = AsyncMock(spec=AsyncSession)
    repository = PlanningCycleRepository(session)

    return repository, session


@pytest.mark.asyncio
async def test_get_by_id_returns_planning_cycle() -> None:
    repository, session = build_repository()
    planning_cycle = Mock(spec=PlanningCycle)

    result = Mock()
    result.scalar_one_or_none.return_value = planning_cycle
    session.execute.return_value = result

    returned = await repository.get_by_id(
        planning_cycle_id=uuid4(),
        organization_id=uuid4(),
    )

    assert returned is planning_cycle
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_not_found() -> None:
    repository, session = build_repository()

    result = Mock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    returned = await repository.get_by_id(
        planning_cycle_id=uuid4(),
        organization_id=uuid4(),
    )

    assert returned is None
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_for_organization_returns_cycles() -> None:
    repository, session = build_repository()

    cycles = [
        Mock(spec=PlanningCycle),
        Mock(spec=PlanningCycle),
    ]

    scalar_result = Mock()
    scalar_result.all.return_value = cycles

    result = Mock()
    result.scalars.return_value = scalar_result
    session.execute.return_value = result

    returned = await repository.list_for_organization(uuid4())

    assert returned == cycles
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_persists_and_returns_cycle() -> None:
    repository, session = build_repository()
    planning_cycle = Mock(spec=PlanningCycle)

    returned = await repository.add(planning_cycle)

    assert returned is planning_cycle
    session.add.assert_called_once_with(planning_cycle)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(planning_cycle)
