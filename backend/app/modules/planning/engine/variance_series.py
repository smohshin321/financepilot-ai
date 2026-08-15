from dataclasses import dataclass
from decimal import Decimal

from app.modules.planning.engine.period import PlanningPeriod
from app.modules.planning.engine.series import PlanningSeries
from app.modules.planning.engine.variance import (
    VarianceEngine,
    VarianceResult,
)
from app.modules.planning.engine.variance_types import FinancialMetricType


@dataclass(frozen=True, slots=True)
class PeriodVarianceResult:
    """Variance result for a single planning period."""

    period: PlanningPeriod
    variance: VarianceResult


@dataclass(frozen=True, slots=True)
class AggregateVarianceResult:
    """Variance result for an aggregated period range."""

    actual: Decimal
    comparator: Decimal
    variance: VarianceResult


class VarianceSeriesEngine:
    """Calculate period and cumulative financial variances."""

    @staticmethod
    def calculate_periods(
        *,
        actual: PlanningSeries,
        comparator: PlanningSeries,
        metric_type: FinancialMetricType,
    ) -> list[PeriodVarianceResult]:
        """Calculate variance for every aligned planning period."""

        actual_periods = actual.periods()
        comparator_periods = comparator.periods()

        if actual_periods != comparator_periods:
            raise ValueError("Actual and comparator periods must align.")

        return [
            PeriodVarianceResult(
                period=period,
                variance=VarianceEngine.calculate(
                    actual=actual.get(period),
                    comparator=comparator.get(period),
                    metric_type=metric_type,
                ),
            )
            for period in actual_periods
        ]

    @staticmethod
    def calculate_ytd(
        *,
        actual: PlanningSeries,
        comparator: PlanningSeries,
        through_period: PlanningPeriod,
        metric_type: FinancialMetricType,
    ) -> AggregateVarianceResult:
        """Calculate year-to-date variance through a selected month."""

        actual_total = Decimal("0")
        comparator_total = Decimal("0")

        for period in actual.periods():
            if period.year == through_period.year and period.month <= through_period.month:
                actual_total += actual.get(period)

        for period in comparator.periods():
            if period.year == through_period.year and period.month <= through_period.month:
                comparator_total += comparator.get(period)

        variance = VarianceEngine.calculate(
            actual=actual_total,
            comparator=comparator_total,
            metric_type=metric_type,
        )

        return AggregateVarianceResult(
            actual=actual_total,
            comparator=comparator_total,
            variance=variance,
        )

    @staticmethod
    def calculate_qtd(
        *,
        actual: PlanningSeries,
        comparator: PlanningSeries,
        through_period: PlanningPeriod,
        metric_type: FinancialMetricType,
    ) -> AggregateVarianceResult:
        """Calculate quarter-to-date variance through a selected month."""

        quarter_start_month = (((through_period.month - 1) // 3) * 3) + 1

        actual_total = Decimal("0")
        comparator_total = Decimal("0")

        for period in actual.periods():
            if (
                period.year == through_period.year
                and quarter_start_month <= period.month <= through_period.month
            ):
                actual_total += actual.get(period)

        for period in comparator.periods():
            if (
                period.year == through_period.year
                and quarter_start_month <= period.month <= through_period.month
            ):
                comparator_total += comparator.get(period)

        variance = VarianceEngine.calculate(
            actual=actual_total,
            comparator=comparator_total,
            metric_type=metric_type,
        )

        return AggregateVarianceResult(
            actual=actual_total,
            comparator=comparator_total,
            variance=variance,
        )
