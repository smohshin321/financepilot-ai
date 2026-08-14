from decimal import Decimal
from uuid import UUID

from app.modules.planning.exceptions import (
    BudgetLineNotFoundError,
    InvalidBudgetAmountError,
)
from app.modules.planning.models import BudgetLine
from app.modules.planning.repositories import BudgetLineRepository


class BudgetLineService:
    """Business service for budget lines."""

    def __init__(
        self,
        repository: BudgetLineRepository,
    ) -> None:
        self._repository = repository

    async def create(
        self,
        budget_line: BudgetLine,
    ) -> BudgetLine:
        self.validate_amount(budget_line.amount)

        return await self._repository.add(budget_line)

    async def get(
        self,
        budget_line_id: UUID,
        budget_version_id: UUID,
    ) -> BudgetLine:
        budget_line = await self._repository.get_by_id(
            budget_line_id=budget_line_id,
            budget_version_id=budget_version_id,
        )

        if budget_line is None:
            raise BudgetLineNotFoundError(budget_line_id)

        return budget_line

    async def list_for_budget_version(
        self,
        budget_version_id: UUID,
    ) -> list[BudgetLine]:
        """Return budget lines for a budget version."""

        return await self._repository.list_for_budget_version(budget_version_id)

    async def update(
        self,
        budget_line: BudgetLine,
    ) -> BudgetLine:
        self.validate_amount(budget_line.amount)

        return await self._repository.save(budget_line)

    async def delete(
        self,
        budget_line_id: UUID,
        budget_version_id: UUID,
    ) -> None:
        budget_line = await self.get(
            budget_line_id,
            budget_version_id,
        )

        await self._repository.delete(budget_line)

    @staticmethod
    def validate_amount(
        amount: Decimal,
    ) -> None:
        if amount < Decimal("0"):
            raise InvalidBudgetAmountError(amount)
