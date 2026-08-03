from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from app.modules.planning.models import BudgetLine
from app.modules.planning.repositories import BudgetLineRepository
from sqlalchemy.ext.asyncio import AsyncSession


def build_repository() -> tuple[BudgetLineRepository, AsyncMock]:
    session = AsyncMock(spec=AsyncSession)
    repository = BudgetLineRepository(session)

    return repository, session


@pytest.mark.asyncio
async def test_get_by_id_returns_budget_line() -> None:
    repository, session = build_repository()

    budget_line = Mock(spec=BudgetLine)

    result = Mock()
    result.scalar_one_or_none.return_value = budget_line

    session.execute.return_value = result

    returned = await repository.get_by_id(
        budget_line_id=uuid4(),
        budget_version_id=uuid4(),
    )

    assert returned is budget_line
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_not_found() -> None:
    repository, session = build_repository()

    result = Mock()
    result.scalar_one_or_none.return_value = None

    session.execute.return_value = result

    returned = await repository.get_by_id(
        budget_line_id=uuid4(),
        budget_version_id=uuid4(),
    )

    assert returned is None
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_for_budget_version_returns_budget_lines() -> None:
    repository, session = build_repository()

    budget_lines = [
        Mock(spec=BudgetLine),
        Mock(spec=BudgetLine),
    ]

    scalar_result = Mock()
    scalar_result.all.return_value = budget_lines

    result = Mock()
    result.scalars.return_value = scalar_result

    session.execute.return_value = result

    returned = await repository.list_for_budget_version(uuid4())

    assert returned == budget_lines
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_for_budget_version_returns_empty_list() -> None:
    repository, session = build_repository()

    scalar_result = Mock()
    scalar_result.all.return_value = []

    result = Mock()
    result.scalars.return_value = scalar_result

    session.execute.return_value = result

    returned = await repository.list_for_budget_version(uuid4())

    assert returned == []
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_persists_and_returns_budget_line() -> None:
    repository, session = build_repository()

    budget_line = Mock(spec=BudgetLine)

    returned = await repository.add(budget_line)

    assert returned is budget_line

    session.add.assert_called_once_with(budget_line)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(budget_line)
