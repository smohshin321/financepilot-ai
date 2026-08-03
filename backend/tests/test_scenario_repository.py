from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from app.modules.planning.models import Scenario
from app.modules.planning.repositories import ScenarioRepository
from sqlalchemy.ext.asyncio import AsyncSession


def build_repository() -> tuple[ScenarioRepository, AsyncMock]:
    session = AsyncMock(spec=AsyncSession)
    repository = ScenarioRepository(session)

    return repository, session


@pytest.mark.asyncio
async def test_get_by_id_returns_scenario() -> None:
    repository, session = build_repository()
    scenario = Mock(spec=Scenario)

    result = Mock()
    result.scalar_one_or_none.return_value = scenario
    session.execute.return_value = result

    returned = await repository.get_by_id(
        scenario_id=uuid4(),
        planning_cycle_id=uuid4(),
    )

    assert returned is scenario
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_not_found() -> None:
    repository, session = build_repository()

    result = Mock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    returned = await repository.get_by_id(
        scenario_id=uuid4(),
        planning_cycle_id=uuid4(),
    )

    assert returned is None
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_for_planning_cycle_returns_scenarios() -> None:
    repository, session = build_repository()

    scenarios = [
        Mock(spec=Scenario),
        Mock(spec=Scenario),
    ]

    scalar_result = Mock()
    scalar_result.all.return_value = scenarios

    result = Mock()
    result.scalars.return_value = scalar_result
    session.execute.return_value = result

    returned = await repository.list_for_planning_cycle(uuid4())

    assert returned == scenarios
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_for_planning_cycle_returns_empty_list() -> None:
    repository, session = build_repository()

    scalar_result = Mock()
    scalar_result.all.return_value = []

    result = Mock()
    result.scalars.return_value = scalar_result
    session.execute.return_value = result

    returned = await repository.list_for_planning_cycle(uuid4())

    assert returned == []
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_persists_and_returns_scenario() -> None:
    repository, session = build_repository()
    scenario = Mock(spec=Scenario)

    returned = await repository.add(scenario)

    assert returned is scenario
    session.add.assert_called_once_with(scenario)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(scenario)
