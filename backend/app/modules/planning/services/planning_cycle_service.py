from datetime import date
from uuid import UUID

from app.modules.planning.exceptions import (
    InvalidFiscalYearError,
    InvalidPlanningCycleDateRangeError,
    PlanningCycleNotFoundError,
)
from app.modules.planning.models import (
    PlanningCycle,
    PlanningStatus,
    PlanningType,
)
from app.modules.planning.repositories import PlanningCycleRepository


class PlanningCycleService:
    """Business service for organization-scoped planning cycles."""

    def __init__(
        self,
        planning_cycle_repository: PlanningCycleRepository,
    ) -> None:
        self._planning_cycles = planning_cycle_repository

    async def create(
        self,
        *,
        organization_id: UUID,
        name: str,
        planning_type: PlanningType,
        fiscal_year: int,
        start_date: date,
        end_date: date,
        description: str | None = None,
    ) -> PlanningCycle:
        """Validate and create a planning cycle."""

        self._validate_fiscal_year(fiscal_year)
        self._validate_date_range(
            start_date=start_date,
            end_date=end_date,
        )

        planning_cycle = PlanningCycle(
            organization_id=organization_id,
            name=name.strip(),
            description=description.strip() if description else None,
            planning_type=planning_type,
            fiscal_year=fiscal_year,
            start_date=start_date,
            end_date=end_date,
            status=PlanningStatus.DRAFT,
            is_active=True,
        )

        return await self._planning_cycles.add(planning_cycle)

    async def get(
        self,
        *,
        planning_cycle_id: UUID,
        organization_id: UUID,
    ) -> PlanningCycle:
        """Return a planning cycle or raise a domain exception."""

        planning_cycle = await self._planning_cycles.get_by_id(
            planning_cycle_id=planning_cycle_id,
            organization_id=organization_id,
        )

        if planning_cycle is None:
            raise PlanningCycleNotFoundError(planning_cycle_id)

        return planning_cycle

    async def list_for_organization(
        self,
        organization_id: UUID,
    ) -> list[PlanningCycle]:
        """Return all planning cycles for an organization."""

        return await self._planning_cycles.list_for_organization(organization_id)

    @staticmethod
    def _validate_date_range(
        *,
        start_date: date,
        end_date: date,
    ) -> None:
        if end_date < start_date:
            raise InvalidPlanningCycleDateRangeError

    @staticmethod
    def _validate_fiscal_year(fiscal_year: int) -> None:
        if not 2000 <= fiscal_year <= 2200:
            raise InvalidFiscalYearError(fiscal_year)
