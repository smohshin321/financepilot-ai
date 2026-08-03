from uuid import UUID

from app.modules.planning.models import PlanningCycle
from app.modules.planning.repositories.base import BaseRepository
from sqlalchemy import select


class PlanningCycleRepository(BaseRepository):
    """Repository for organization-scoped planning cycle persistence."""

    async def get_by_id(
        self,
        planning_cycle_id: UUID,
        organization_id: UUID,
    ) -> PlanningCycle | None:
        """Return a planning cycle by ID within an organization."""

        result = await self._session.execute(
            select(PlanningCycle).where(
                PlanningCycle.id == planning_cycle_id,
                PlanningCycle.organization_id == organization_id,
            )
        )

        return result.scalar_one_or_none()

    async def list_for_organization(
        self,
        organization_id: UUID,
    ) -> list[PlanningCycle]:
        """Return planning cycles for an organization."""

        result = await self._session.execute(
            select(PlanningCycle)
            .where(PlanningCycle.organization_id == organization_id)
            .order_by(
                PlanningCycle.fiscal_year.desc(),
                PlanningCycle.name.asc(),
            )
        )

        return list(result.scalars().all())

    async def add(
        self,
        planning_cycle: PlanningCycle,
    ) -> PlanningCycle:
        """Add a planning cycle to the current database session."""

        self._session.add(planning_cycle)
        await self._session.flush()
        await self._session.refresh(planning_cycle)

        return planning_cycle
