from dataclasses import dataclass
from decimal import Decimal

from app.modules.planning.engine.exceptions import (
    DuplicatePlanningPeriodError,
    MissingPlanningPeriodError,
)
from app.modules.planning.engine.period import PlanningPeriod


@dataclass(frozen=True, slots=True)
class PeriodValue:
    """Represents a financial value for a single planning period."""

    period: PlanningPeriod
    value: Decimal


class PlanningSeries:
    """Represents a period-indexed financial planning series."""

    def __init__(
        self,
        values: list[PeriodValue],
    ) -> None:
        self._values: dict[PlanningPeriod, Decimal] = {}

        for item in values:
            if item.period in self._values:
                raise DuplicatePlanningPeriodError(item.period)

            self._values[item.period] = item.value

    def get(
        self,
        period: PlanningPeriod,
    ) -> Decimal:
        """Return the value for a planning period."""

        try:
            return self._values[period]
        except KeyError as error:
            raise MissingPlanningPeriodError(period) from error

    def periods(self) -> list[PlanningPeriod]:
        """Return available periods in chronological order."""

        return sorted(self._values)

    def total(self) -> Decimal:
        """Return the total value across all periods."""

        return sum(
            self._values.values(),
            start=Decimal("0"),
        )
