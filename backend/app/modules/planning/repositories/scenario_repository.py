from uuid import UUID

from app.modules.planning.models import Scenario
from app.modules.planning.repositories.base import BaseRepository
from sqlalchemy import select


class ScenarioRepository(BaseRepository):
    """Repository for planning-scenario persistence."""

    async def get_by_id(
        self,
        scenario_id: UUID,
        planning_cycle_id: UUID,
    ) -> Scenario | None:
        """Return a scenario within a planning cycle."""

        result = await self._session.execute(
            select(Scenario).where(
                Scenario.id == scenario_id,
                Scenario.planning_cycle_id == planning_cycle_id,
            )
        )

        return result.scalar_one_or_none()

    async def list_for_planning_cycle(
        self,
        planning_cycle_id: UUID,
    ) -> list[Scenario]:
        """Return active scenarios for a planning cycle."""

        result = await self._session.execute(
            select(Scenario)
            .where(
                Scenario.planning_cycle_id == planning_cycle_id,
                Scenario.is_active.is_(True),
            )
            .order_by(
                Scenario.is_default.desc(),
                Scenario.name.asc(),
            )
        )

        return list(result.scalars().all())

    async def add(self, scenario: Scenario) -> Scenario:
        """Add a scenario to the current database session."""

        self._session.add(scenario)
        await self._session.flush()
        await self._session.refresh(scenario)

        return scenario

    async def save(self, scenario: Scenario) -> Scenario:
        """Persist changes to an existing scenario."""

        await self._session.flush()
        await self._session.refresh(scenario)

        return scenario

    async def get_default_for_planning_cycle(
        self,
        planning_cycle_id: UUID,
    ) -> Scenario | None:
        """Return the default scenario for a planning cycle."""

        result = await self._session.execute(
            select(Scenario).where(
                Scenario.planning_cycle_id == planning_cycle_id,
                Scenario.is_default.is_(True),
            )
        )

        return result.scalar_one_or_none()

    async def clear_default_for_planning_cycle(
        self,
        planning_cycle_id: UUID,
    ) -> None:
        """Clear the default flag for all scenarios in a planning cycle."""

        result = await self._session.execute(
            select(Scenario).where(
                Scenario.planning_cycle_id == planning_cycle_id,
                Scenario.is_default.is_(True),
            )
        )

        scenarios = list(result.scalars().all())

        for scenario in scenarios:
            scenario.is_default = False

        await self._session.flush()
