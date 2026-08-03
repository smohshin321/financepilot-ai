from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from app.modules.planning.exceptions import (
    BudgetLineNotFoundError,
    InvalidBudgetAmountError,
)
from app.modules.planning.models import BudgetLine
from app.modules.planning.repositories import BudgetLineRepository
from app.modules.planning.services import BudgetLineService


def build_service() -> tuple[BudgetLineService, AsyncMock]:
    repository = AsyncMock(spec=BudgetLineRepository)
    service = BudgetLineService(repository)
    return service, repository


@pytest.mark.asyncio
async def test_create_budget_line() -> None:
    service, repository = build_service()

    budget_line = Mock(spec=BudgetLine)
    budget_line.amount = Decimal("100")

    repository.add.return_value = budget_line

    returned = await service.create(budget_line)

    assert returned is budget_line


@pytest.mark.asyncio
async def test_get_budget_line() -> None:
    service, repository = build_service()

    budget_line = Mock(spec=BudgetLine)

    repository.get_by_id.return_value = budget_line

    returned = await service.get(
        uuid4(),
        uuid4(),
    )

    assert returned is budget_line


@pytest.mark.asyncio
async def test_get_budget_line_not_found() -> None:
    service, repository = build_service()

    repository.get_by_id.return_value = None

    with pytest.raises(BudgetLineNotFoundError):
        await service.get(
            uuid4(),
            uuid4(),
        )


@pytest.mark.asyncio
async def test_update_budget_line() -> None:
    service, repository = build_service()

    budget_line = Mock(spec=BudgetLine)
    budget_line.amount = Decimal("500")

    repository.save.return_value = budget_line

    returned = await service.update(budget_line)

    assert returned is budget_line


@pytest.mark.asyncio
async def test_delete_budget_line() -> None:
    service, repository = build_service()

    budget_line = Mock(spec=BudgetLine)

    repository.get_by_id.return_value = budget_line

    await service.delete(
        uuid4(),
        uuid4(),
    )

    repository.delete.assert_awaited_once_with(budget_line)


def test_negative_amount_rejected() -> None:
    with pytest.raises(InvalidBudgetAmountError):
        BudgetLineService.validate_amount(Decimal("-1"))


def test_zero_amount_allowed() -> None:
    BudgetLineService.validate_amount(Decimal("0"))
