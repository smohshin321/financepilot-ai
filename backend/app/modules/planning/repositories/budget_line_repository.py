from uuid import UUID

from app.modules.planning.models import BudgetLine
from app.modules.planning.repositories.base import BaseRepository
from sqlalchemy import select


class BudgetLineRepository(BaseRepository):
    """Repository for budget line persistence."""

    async def get_by_id(
        self,
        budget_line_id: UUID,
        budget_version_id: UUID,
    ) -> BudgetLine | None:
        """Return a budget line within a budget version."""

        result = await self._session.execute(
            select(BudgetLine).where(
                BudgetLine.id == budget_line_id,
                BudgetLine.budget_version_id == budget_version_id,
            )
        )

        return result.scalar_one_or_none()

    async def list_for_budget_version(
        self,
        budget_version_id: UUID,
    ) -> list[BudgetLine]:
        """Return all budget lines for a budget version."""

        result = await self._session.execute(
            select(BudgetLine)
            .where(BudgetLine.budget_version_id == budget_version_id)
            .order_by(BudgetLine.period.asc())
        )

        return list(result.scalars().all())

    async def add(
        self,
        budget_line: BudgetLine,
    ) -> BudgetLine:
        """Add a budget line to the current session."""

        self._session.add(budget_line)
        await self._session.flush()
        await self._session.refresh(budget_line)

        return budget_line

    async def save(
        self,
        budget_line: BudgetLine,
    ) -> BudgetLine:
        """Persist updates."""

        await self._session.flush()
        await self._session.refresh(budget_line)

        return budget_line

    async def delete(
        self,
        budget_line: BudgetLine,
    ) -> None:
        """Delete a budget line."""

        await self._session.delete(budget_line)
        await self._session.flush()
