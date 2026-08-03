from uuid import UUID

from app.modules.planning.models import BudgetVersion
from app.modules.planning.repositories.base import BaseRepository
from sqlalchemy import select


class BudgetVersionRepository(BaseRepository):
    """Repository for budget version persistence."""

    async def get_by_id(
        self,
        budget_version_id: UUID,
        scenario_id: UUID,
    ) -> BudgetVersion | None:
        """Return a budget version within a scenario."""

        result = await self._session.execute(
            select(BudgetVersion).where(
                BudgetVersion.id == budget_version_id,
                BudgetVersion.scenario_id == scenario_id,
            )
        )

        return result.scalar_one_or_none()

    async def list_for_scenario(
        self,
        scenario_id: UUID,
    ) -> list[BudgetVersion]:
        """Return budget versions for a scenario."""

        result = await self._session.execute(
            select(BudgetVersion)
            .where(BudgetVersion.scenario_id == scenario_id)
            .order_by(
                BudgetVersion.version_number.desc(),
            )
        )

        return list(result.scalars().all())

    async def add(
        self,
        budget_version: BudgetVersion,
    ) -> BudgetVersion:
        """Add a budget version to the current session."""

        self._session.add(budget_version)
        await self._session.flush()
        await self._session.refresh(budget_version)

        return budget_version

    async def save(
        self,
        budget_version: BudgetVersion,
    ) -> BudgetVersion:
        """Persist updates."""

        await self._session.flush()
        await self._session.refresh(budget_version)

        return budget_version

    async def get_active_for_scenario(
        self,
        scenario_id: UUID,
    ) -> BudgetVersion | None:
        """Return the active version."""

        result = await self._session.execute(
            select(BudgetVersion).where(
                BudgetVersion.scenario_id == scenario_id,
                BudgetVersion.is_active.is_(True),
            )
        )

        return result.scalar_one_or_none()
