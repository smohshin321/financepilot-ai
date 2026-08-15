from dataclasses import dataclass
from enum import StrEnum

from app.modules.planning.engine.period import PlanningPeriod
from app.modules.planning.engine.series import PeriodValue, PlanningSeries


class ForecastCadence(StrEnum):
    """Supported rolling-forecast refresh cadences."""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass(frozen=True, slots=True)
class RollingForecastVintage:
    """Represents a preserved rolling-forecast planning vintage."""

    code: str
    as_of_period: PlanningPeriod
    cadence: ForecastCadence
    values: PlanningSeries


@dataclass(frozen=True, slots=True)
class RollingForecastPlan:
    """Combined actual and forecast view for a rolling forecast."""

    closed_through: PlanningPeriod
    values: PlanningSeries


class RollingForecastEngine:
    """Manage rolling-forecast vintage lifecycle rules."""

    @staticmethod
    def latest_vintage(
        vintages: list[RollingForecastVintage],
    ) -> RollingForecastVintage:
        """Return the most recent forecast vintage."""

        if not vintages:
            raise ValueError("At least one forecast vintage is required.")

        return max(
            vintages,
            key=lambda vintage: (
                vintage.as_of_period.year,
                vintage.as_of_period.month,
            ),
        )

    @staticmethod
    def next_as_of_period(
        *,
        current_period: PlanningPeriod,
        cadence: ForecastCadence,
    ) -> PlanningPeriod:
        """Return the next forecast refresh period."""

        months_to_add = 1 if cadence == ForecastCadence.MONTHLY else 3

        month_index = current_period.year * 12 + current_period.month - 1 + months_to_add

        year, zero_based_month = divmod(month_index, 12)

        return PlanningPeriod(
            year=year,
            month=zero_based_month + 1,
        )

    @staticmethod
    def compose(
        *,
        actual: PlanningSeries,
        forecast: PlanningSeries,
        closed_through: PlanningPeriod,
    ) -> RollingForecastPlan:
        """Combine closed actual periods with open forecast periods."""

        actual_periods = set(actual.periods())
        forecast_periods = set(forecast.periods())

        all_periods = sorted(
            actual_periods | forecast_periods,
            key=lambda period: (period.year, period.month),
        )

        values: list[PeriodValue] = []

        for period in all_periods:
            is_closed = period.year < closed_through.year or (
                period.year == closed_through.year and period.month <= closed_through.month
            )

            value = actual.get(period) if is_closed else forecast.get(period)

            values.append(
                PeriodValue(
                    period=period,
                    value=value,
                )
            )

        return RollingForecastPlan(
            closed_through=closed_through,
            values=PlanningSeries(values),
        )
