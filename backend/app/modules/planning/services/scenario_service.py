from uuid import UUID

from app.modules.planning.models import Scenario
from app.modules.planning.repositories import ScenarioRepository


class ScenarioService:
    """Business service for planning scenarios."""

    def __init__(
        self,
        scenario_repository: ScenarioRepository,
    ) -> None:
        self._repository = scenario_repository

    async def create(
        self,
        scenario: Scenario,
    ) -> Scenario:
        """Create a new scenario."""

        return await self._repository.add(scenario)

    async def get(
        self,
        scenario_id: UUID,
        planning_cycle_id: UUID,
    ) -> Scenario | None:
        """Return a scenario."""

        return await self._repository.get_by_id(
            scenario_id=scenario_id,
            planning_cycle_id=planning_cycle_id,
        )

    async def list_for_planning_cycle(
        self,
        planning_cycle_id: UUID,
    ) -> list[Scenario]:
        """Return planning scenarios."""

        return await self._repository.list_for_planning_cycle(planning_cycle_id)

    async def set_default(
        self,
        scenario_id: UUID,
        planning_cycle_id: UUID,
    ) -> Scenario | None:
        """Make exactly one scenario the default."""

        await self._repository.clear_default_for_planning_cycle(planning_cycle_id)

        scenario = await self._repository.get_by_id(
            scenario_id=scenario_id,
            planning_cycle_id=planning_cycle_id,
        )

        if scenario is None:
            return None

        scenario.is_default = True

        return await self._repository.save(scenario)
