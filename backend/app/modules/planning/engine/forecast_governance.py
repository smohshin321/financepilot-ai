from app.modules.planning.engine.period import PlanningPeriod
from app.modules.planning.engine.rolling_forecast import (
    ForecastCadence,
    RollingForecastVintage,
)


class ForecastGovernanceError(ValueError):
    """Raised when a rolling-forecast lifecycle rule is violated."""


class ForecastGovernanceEngine:
    """Validate rolling-forecast vintage sequencing and cadence."""

    @staticmethod
    def validate_next_vintage(
        *,
        prior_vintage: RollingForecastVintage,
        new_as_of_period: PlanningPeriod,
    ) -> None:
        """Validate that a new vintage follows the configured cadence."""

        expected_period = ForecastGovernanceEngine.expected_next_period(
            prior_vintage=prior_vintage,
        )

        if new_as_of_period != expected_period:
            raise ForecastGovernanceError(
                "Invalid forecast vintage sequence: "
                f"expected '{expected_period.code}', "
                f"received '{new_as_of_period.code}'."
            )

    @staticmethod
    def expected_next_period(
        *,
        prior_vintage: RollingForecastVintage,
    ) -> PlanningPeriod:
        """Return the next valid as-of period for a forecast vintage."""

        months_to_add = 1 if prior_vintage.cadence == ForecastCadence.MONTHLY else 3

        return ForecastGovernanceEngine._add_months(
            prior_vintage.as_of_period,
            months_to_add,
        )

    @staticmethod
    def validate_unique_as_of_periods(
        vintages: list[RollingForecastVintage],
    ) -> None:
        """Reject multiple vintages for the same as-of period."""

        periods: set[PlanningPeriod] = set()

        for vintage in vintages:
            if vintage.as_of_period in periods:
                raise ForecastGovernanceError(
                    f"Duplicate forecast vintage as-of period: '{vintage.as_of_period.code}'."
                )

            periods.add(vintage.as_of_period)

    @staticmethod
    def validate_consistent_cadence(
        vintages: list[RollingForecastVintage],
    ) -> None:
        """Require all vintages in a sequence to use the same cadence."""

        if not vintages:
            return

        expected_cadence = vintages[0].cadence

        for vintage in vintages[1:]:
            if vintage.cadence != expected_cadence:
                raise ForecastGovernanceError("Forecast vintage sequence contains mixed cadences.")

    @staticmethod
    def _add_months(
        period: PlanningPeriod,
        months: int,
    ) -> PlanningPeriod:
        month_index = period.year * 12 + period.month - 1 + months

        year, zero_based_month = divmod(
            month_index,
            12,
        )

        return PlanningPeriod(
            year=year,
            month=zero_based_month + 1,
        )
