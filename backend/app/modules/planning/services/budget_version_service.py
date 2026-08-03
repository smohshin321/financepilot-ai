from uuid import UUID

from app.modules.planning.exceptions import (
    BudgetVersionLockedError,
    BudgetVersionNotFoundError,
)
from app.modules.planning.models import BudgetVersion
from app.modules.planning.repositories import BudgetVersionRepository


class BudgetVersionService:
    """Business service for budget versions."""

    def __init__(
        self,
        repository: BudgetVersionRepository,
    ) -> None:
        self._repository = repository

    async def get(
        self,
        budget_version_id: UUID,
        scenario_id: UUID,
    ) -> BudgetVersion:
        """Return one budget version."""

        version = await self._repository.get_by_id(
            budget_version_id=budget_version_id,
            scenario_id=scenario_id,
        )

        if version is None:
            raise BudgetVersionNotFoundError(budget_version_id)

        return version

    async def create(
        self,
        budget_version: BudgetVersion,
    ) -> BudgetVersion:
        """Create a version."""

        return await self._repository.add(budget_version)

    async def lock(
        self,
        budget_version_id: UUID,
        scenario_id: UUID,
    ) -> BudgetVersion:
        """Lock a version."""

        version = await self.get(
            budget_version_id,
            scenario_id,
        )

        version.is_locked = True

        return await self._repository.save(version)

    async def activate(
        self,
        budget_version_id: UUID,
        scenario_id: UUID,
    ) -> BudgetVersion:
        """Activate a version."""

        current = await self._repository.get_active_for_scenario(scenario_id)

        if current is not None:
            current.is_active = False
            await self._repository.save(current)

        version = await self.get(
            budget_version_id,
            scenario_id,
        )

        version.is_active = True

        return await self._repository.save(version)

    @staticmethod
    def validate_editable(
        version: BudgetVersion,
    ) -> None:
        """Ensure the version can still be edited."""

        if version.is_locked:
            raise BudgetVersionLockedError(version.id)
