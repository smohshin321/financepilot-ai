from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from app.modules.planning.models import Scenario
from app.modules.planning.repositories import ScenarioRepository
from app.modules.planning.services import ScenarioService


def build_service() -> tuple[ScenarioService, AsyncMock]:
    repository = AsyncMock(spec=ScenarioRepository)
    service = ScenarioService(repository)

    return service, repository


@pytest.mark.asyncio
async def test_create_returns_created_scenario() -> None:
    service, repository = build_service()
    scenario = Mock(spec=Scenario)

    repository.add.return_value = scenario

    returned = await service.create(scenario)

    assert returned is scenario
    repository.add.assert_awaited_once_with(scenario)


@pytest.mark.asyncio
async def test_get_returns_scenario() -> None:
    service, repository = build_service()
    scenario = Mock(spec=Scenario)

    repository.get_by_id.return_value = scenario

    returned = await service.get(
        uuid4(),
        uuid4(),
    )

    assert returned is scenario


@pytest.mark.asyncio
async def test_list_returns_repository_values() -> None:
    service, repository = build_service()

    scenarios = [
        Mock(spec=Scenario),
        Mock(spec=Scenario),
    ]

    repository.list_for_planning_cycle.return_value = scenarios

    returned = await service.list_for_planning_cycle(uuid4())

    assert returned == scenarios


@pytest.mark.asyncio
async def test_set_default_updates_default_flag() -> None:
    service, repository = build_service()
    scenario = Mock(spec=Scenario)

    repository.get_by_id.return_value = scenario
    repository.save.return_value = scenario

    returned = await service.set_default(
        uuid4(),
        uuid4(),
    )

    assert returned is scenario
    assert scenario.is_default is True

    repository.clear_default_for_planning_cycle.assert_awaited_once()
    repository.save.assert_awaited_once_with(scenario)


@pytest.mark.asyncio
async def test_set_default_returns_none_when_not_found() -> None:
    service, repository = build_service()

    repository.get_by_id.return_value = None

    returned = await service.set_default(
        uuid4(),
        uuid4(),
    )

    assert returned is None
    repository.save.assert_not_awaited()
