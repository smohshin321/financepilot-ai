from decimal import Decimal

from app.modules.planning.engine.exceptions import PeriodAlignmentError
from app.modules.planning.engine.period import PlanningPeriod
from app.modules.planning.engine.series import (
    PeriodValue,
    PlanningSeries,
)


class PeriodCalculationEngine:
    """Perform period-aware FP&A calculations."""

    @staticmethod
    def _aligned_periods(
        *,
        left: PlanningSeries,
        right: PlanningSeries,
    ) -> list[PlanningPeriod]:
        left_periods = set(left.periods())
        right_periods = set(right.periods())

        if left_periods != right_periods:
            raise PeriodAlignmentError(
                left_only=left_periods - right_periods,
                right_only=right_periods - left_periods,
            )

        return sorted(left_periods)

    @staticmethod
    def multiply(
        *,
        left: PlanningSeries,
        right: PlanningSeries,
    ) -> PlanningSeries:
        """Multiply two aligned planning series period by period."""

        periods = PeriodCalculationEngine._aligned_periods(
            left=left,
            right=right,
        )

        return PlanningSeries(
            [
                PeriodValue(
                    period=period,
                    value=left.get(period) * right.get(period),
                )
                for period in periods
            ]
        )

    @staticmethod
    def subtract(
        *,
        left: PlanningSeries,
        right: PlanningSeries,
    ) -> PlanningSeries:
        """Subtract one aligned planning series from another."""

        periods = PeriodCalculationEngine._aligned_periods(
            left=left,
            right=right,
        )

        return PlanningSeries(
            [
                PeriodValue(
                    period=period,
                    value=left.get(period) - right.get(period),
                )
                for period in periods
            ]
        )

    @staticmethod
    def apply_rate(
        *,
        base: PlanningSeries,
        rate: PlanningSeries,
    ) -> PlanningSeries:
        """Apply a period-specific rate to a base series."""

        return PeriodCalculationEngine.multiply(
            left=base,
            right=rate,
        )

    @staticmethod
    def apply_growth(
        *,
        base: PlanningSeries,
        growth_rate: PlanningSeries,
    ) -> PlanningSeries:
        """Apply period-specific growth rates to a base series."""

        periods = PeriodCalculationEngine._aligned_periods(
            left=base,
            right=growth_rate,
        )

        return PlanningSeries(
            [
                PeriodValue(
                    period=period,
                    value=base.get(period) * (Decimal("1") + growth_rate.get(period)),
                )
                for period in periods
            ]
        )
