from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from app.modules.planning.models import BudgetVersion
from app.modules.planning.repositories import BudgetVersionRepository
from sqlalchemy.ext.asyncio import AsyncSession


def build_repository() -> tuple[BudgetVersionRepository, AsyncMock]:
    session = AsyncMock(spec=AsyncSession)
    repository = BudgetVersionRepository(session)

    return repository, session


@pytest.mark.asyncio
async def test_get_by_id_returns_budget_version() -> None:
    repository, session = build_repository()
    budget_version = Mock(spec=BudgetVersion)

    result = Mock()
    result.scalar_one_or_none.return_value = budget_version
    session.execute.return_value = result

    returned = await repository.get_by_id(
        budget_version_id=uuid4(),
        scenario_id=uuid4(),
    )

    assert returned is budget_version
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_not_found() -> None:
    repository, session = build_repository()

    result = Mock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    returned = await repository.get_by_id(
        budget_version_id=uuid4(),
        scenario_id=uuid4(),
    )

    assert returned is None
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_for_scenario_returns_budget_versions() -> None:
    repository, session = build_repository()

    budget_versions = [
        Mock(spec=BudgetVersion),
        Mock(spec=BudgetVersion),
    ]

    scalar_result = Mock()
    scalar_result.all.return_value = budget_versions

    result = Mock()
    result.scalars.return_value = scalar_result
    session.execute.return_value = result

    returned = await repository.list_for_scenario(uuid4())

    assert returned == budget_versions
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_for_scenario_returns_empty_list() -> None:
    repository, session = build_repository()

    scalar_result = Mock()
    scalar_result.all.return_value = []

    result = Mock()
    result.scalars.return_value = scalar_result
    session.execute.return_value = result

    returned = await repository.list_for_scenario(uuid4())

    assert returned == []
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_persists_and_returns_budget_version() -> None:
    repository, session = build_repository()
    budget_version = Mock(spec=BudgetVersion)

    returned = await repository.add(budget_version)

    assert returned is budget_version
    session.add.assert_called_once_with(budget_version)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(budget_version)
