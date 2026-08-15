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
class ForecastVintage:
    """Represents a named rolling-forecast vintage."""

    code: str
    as_of_period: PlanningPeriod
    values: PlanningSeries


@dataclass(frozen=True, slots=True)
class ForecastPeriodComparison:
    """Variance comparison for a single period across plan and forecast."""

    period: PlanningPeriod
    actual: Decimal
    plan: Decimal
    latest_forecast: Decimal
    actual_vs_plan: VarianceResult
    actual_vs_forecast: VarianceResult


@dataclass(frozen=True, slots=True)
class ForecastRevisionResult:
    """Represents the change between two forecast vintages."""

    period: PlanningPeriod
    prior_forecast: Decimal
    latest_forecast: Decimal
    revision_amount: Decimal
    revision_percentage: Decimal | None


class ForecastVintageEngine:
    """Analyze rolling-forecast vintages and actual performance."""

    @staticmethod
    def compare_actual(
        *,
        period: PlanningPeriod,
        actual: PlanningSeries,
        plan: PlanningSeries,
        latest_forecast: ForecastVintage,
        metric_type: FinancialMetricType,
    ) -> ForecastPeriodComparison:
        """Compare actual against plan and the latest forecast."""

        actual_value = actual.get(period)
        plan_value = plan.get(period)
        forecast_value = latest_forecast.values.get(period)

        return ForecastPeriodComparison(
            period=period,
            actual=actual_value,
            plan=plan_value,
            latest_forecast=forecast_value,
            actual_vs_plan=VarianceEngine.calculate(
                actual=actual_value,
                comparator=plan_value,
                metric_type=metric_type,
            ),
            actual_vs_forecast=VarianceEngine.calculate(
                actual=actual_value,
                comparator=forecast_value,
                metric_type=metric_type,
            ),
        )

    @staticmethod
    def compare_forecasts(
        *,
        period: PlanningPeriod,
        prior_forecast: ForecastVintage,
        latest_forecast: ForecastVintage,
    ) -> ForecastRevisionResult:
        """Calculate the revision between forecast vintages."""

        prior_value = prior_forecast.values.get(period)
        latest_value = latest_forecast.values.get(period)

        revision_amount = latest_value - prior_value

        revision_percentage = (
            revision_amount / abs(prior_value) if prior_value != Decimal("0") else None
        )

        return ForecastRevisionResult(
            period=period,
            prior_forecast=prior_value,
            latest_forecast=latest_value,
            revision_amount=revision_amount,
            revision_percentage=revision_percentage,
        )
