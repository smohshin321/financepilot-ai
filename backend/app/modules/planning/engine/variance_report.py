from dataclasses import dataclass

from app.modules.planning.engine.forecast_vintage import (
    ForecastRevisionResult,
    ForecastVintage,
    ForecastVintageEngine,
)
from app.modules.planning.engine.period import PlanningPeriod
from app.modules.planning.engine.series import PlanningSeries
from app.modules.planning.engine.variance import VarianceResult
from app.modules.planning.engine.variance_series import (
    AggregateVarianceResult,
    VarianceSeriesEngine,
)
from app.modules.planning.engine.variance_types import FinancialMetricType


@dataclass(frozen=True, slots=True)
class PeriodVarianceSnapshot:
    """Structured variance output for a single financial metric and period."""

    period: PlanningPeriod
    metric_type: FinancialMetricType

    actual_vs_plan: VarianceResult
    actual_vs_forecast: VarianceResult

    latest_forecast_code: str
    prior_forecast_code: str | None

    forecast_revision: ForecastRevisionResult | None


@dataclass(frozen=True, slots=True)
class AggregateVarianceSnapshot:
    """Structured QTD or YTD variance comparison."""

    actual_vs_plan: AggregateVarianceResult
    actual_vs_forecast: AggregateVarianceResult


@dataclass(frozen=True, slots=True)
class VarianceReport:
    """Complete variance-analysis result for a selected period."""

    period: PeriodVarianceSnapshot
    qtd: AggregateVarianceSnapshot
    ytd: AggregateVarianceSnapshot


class VarianceReportEngine:
    """Orchestrate period, QTD, YTD, and rolling-forecast variance analysis."""

    @staticmethod
    def calculate(
        *,
        period: PlanningPeriod,
        actual: PlanningSeries,
        plan: PlanningSeries,
        latest_forecast: ForecastVintage,
        metric_type: FinancialMetricType,
        prior_forecast: ForecastVintage | None = None,
    ) -> VarianceReport:
        """Build a complete variance-analysis report."""

        period_comparison = ForecastVintageEngine.compare_actual(
            period=period,
            actual=actual,
            plan=plan,
            latest_forecast=latest_forecast,
            metric_type=metric_type,
        )

        forecast_revision = (
            ForecastVintageEngine.compare_forecasts(
                period=period,
                prior_forecast=prior_forecast,
                latest_forecast=latest_forecast,
            )
            if prior_forecast is not None
            else None
        )

        period_snapshot = PeriodVarianceSnapshot(
            period=period,
            metric_type=metric_type,
            actual_vs_plan=period_comparison.actual_vs_plan,
            actual_vs_forecast=period_comparison.actual_vs_forecast,
            latest_forecast_code=latest_forecast.code,
            prior_forecast_code=(prior_forecast.code if prior_forecast is not None else None),
            forecast_revision=forecast_revision,
        )

        qtd_snapshot = AggregateVarianceSnapshot(
            actual_vs_plan=VarianceSeriesEngine.calculate_qtd(
                actual=actual,
                comparator=plan,
                through_period=period,
                metric_type=metric_type,
            ),
            actual_vs_forecast=VarianceSeriesEngine.calculate_qtd(
                actual=actual,
                comparator=latest_forecast.values,
                through_period=period,
                metric_type=metric_type,
            ),
        )

        ytd_snapshot = AggregateVarianceSnapshot(
            actual_vs_plan=VarianceSeriesEngine.calculate_ytd(
                actual=actual,
                comparator=plan,
                through_period=period,
                metric_type=metric_type,
            ),
            actual_vs_forecast=VarianceSeriesEngine.calculate_ytd(
                actual=actual,
                comparator=latest_forecast.values,
                through_period=period,
                metric_type=metric_type,
            ),
        )

        return VarianceReport(
            period=period_snapshot,
            qtd=qtd_snapshot,
            ytd=ytd_snapshot,
        )
