from dataclasses import dataclass
from enum import StrEnum

from app.modules.planning.engine.period import PlanningPeriod


class ForecastHorizonType(StrEnum):
    """Supported forecast horizon conventions."""

    FISCAL_YEAR = "fiscal_year"
    ROLLING = "rolling"


@dataclass(frozen=True, slots=True)
class ForecastHorizon:
    """Configuration defining the forward-looking forecast horizon."""

    horizon_type: ForecastHorizonType
    months: int | None = None

    def __post_init__(self) -> None:
        if self.horizon_type == ForecastHorizonType.ROLLING and (
            self.months is None or self.months <= 0
        ):
            raise ValueError("Rolling forecast horizon requires a positive number of months.")

        if self.horizon_type == ForecastHorizonType.FISCAL_YEAR and self.months is not None:
            raise ValueError("Fiscal-year forecast horizon must not specify months.")


class ForecastHorizonEngine:
    """Generate periods belonging to a forecast horizon."""

    @staticmethod
    def periods(
        *,
        as_of_period: PlanningPeriod,
        horizon: ForecastHorizon,
        fiscal_year_end_month: int = 12,
    ) -> list[PlanningPeriod]:
        """Return forecastable periods after the as-of period."""

        if not 1 <= fiscal_year_end_month <= 12:
            raise ValueError("Fiscal year end month must be between 1 and 12.")

        if horizon.horizon_type == ForecastHorizonType.ROLLING:
            assert horizon.months is not None

            return [
                ForecastHorizonEngine._add_months(
                    as_of_period,
                    offset,
                )
                for offset in range(1, horizon.months + 1)
            ]

        periods: list[PlanningPeriod] = []
        period = ForecastHorizonEngine._add_months(
            as_of_period,
            1,
        )

        while True:
            periods.append(period)

            if period.month == fiscal_year_end_month:
                break

            period = ForecastHorizonEngine._add_months(
                period,
                1,
            )

        return periods

    @staticmethod
    def _add_months(
        period: PlanningPeriod,
        months: int,
    ) -> PlanningPeriod:
        """Advance a planning period by a number of months."""

        month_index = period.year * 12 + period.month - 1 + months

        year, zero_based_month = divmod(
            month_index,
            12,
        )

        return PlanningPeriod(
            year=year,
            month=zero_based_month + 1,
        )
