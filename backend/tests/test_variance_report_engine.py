from decimal import Decimal

from app.modules.planning.engine import (
    FinancialMetricType,
    ForecastVintage,
    PeriodValue,
    PlanningPeriod,
    PlanningSeries,
    VarianceFavorability,
    VarianceReportEngine,
)


def build_series(
    year: int,
    values: list[str],
) -> PlanningSeries:
    return PlanningSeries(
        [
            PeriodValue(
                period=PlanningPeriod(year, month),
                value=Decimal(value),
            )
            for month, value in enumerate(values, start=1)
        ]
    )


def test_builds_period_variance_report() -> None:
    period = PlanningPeriod(2027, 2)

    actual = build_series(
        2027,
        ["100", "200", "250"],
    )

    plan = build_series(
        2027,
        ["100", "150", "200"],
    )

    latest_forecast = ForecastVintage(
        code="RF_FEB",
        as_of_period=PlanningPeriod(2027, 2),
        values=build_series(
            2027,
            ["100", "180", "220"],
        ),
    )

    report = VarianceReportEngine.calculate(
        period=period,
        actual=actual,
        plan=plan,
        latest_forecast=latest_forecast,
        metric_type=FinancialMetricType.REVENUE,
    )

    assert report.period.period == period
    assert report.period.latest_forecast_code == "RF_FEB"

    assert report.period.actual_vs_plan.amount == Decimal("50")
    assert report.period.actual_vs_forecast.amount == Decimal("20")

    assert report.period.actual_vs_plan.favorability == VarianceFavorability.FAVORABLE


def test_includes_forecast_revision() -> None:
    period = PlanningPeriod(2027, 2)

    actual = build_series(
        2027,
        ["100", "200", "250"],
    )

    plan = build_series(
        2027,
        ["100", "150", "200"],
    )

    prior_forecast = ForecastVintage(
        code="RF_JAN",
        as_of_period=PlanningPeriod(2027, 1),
        values=build_series(
            2027,
            ["100", "150", "200"],
        ),
    )

    latest_forecast = ForecastVintage(
        code="RF_FEB",
        as_of_period=PlanningPeriod(2027, 2),
        values=build_series(
            2027,
            ["100", "180", "220"],
        ),
    )

    report = VarianceReportEngine.calculate(
        period=period,
        actual=actual,
        plan=plan,
        prior_forecast=prior_forecast,
        latest_forecast=latest_forecast,
        metric_type=FinancialMetricType.REVENUE,
    )

    assert report.period.prior_forecast_code == "RF_JAN"
    assert report.period.latest_forecast_code == "RF_FEB"

    assert report.period.forecast_revision is not None

    assert report.period.forecast_revision.revision_amount == Decimal("30")

    assert report.period.forecast_revision.revision_percentage == Decimal("0.2")


def test_prior_forecast_is_optional() -> None:
    period = PlanningPeriod(2027, 2)

    report = VarianceReportEngine.calculate(
        period=period,
        actual=build_series(
            2027,
            ["100", "200"],
        ),
        plan=build_series(
            2027,
            ["100", "150"],
        ),
        latest_forecast=ForecastVintage(
            code="RF_FEB",
            as_of_period=period,
            values=build_series(
                2027,
                ["100", "180"],
            ),
        ),
        metric_type=FinancialMetricType.REVENUE,
    )

    assert report.period.prior_forecast_code is None
    assert report.period.forecast_revision is None


def test_builds_ytd_variance_report() -> None:
    period = PlanningPeriod(2027, 3)

    report = VarianceReportEngine.calculate(
        period=period,
        actual=build_series(
            2027,
            ["100", "200", "250"],
        ),
        plan=build_series(
            2027,
            ["100", "150", "200"],
        ),
        latest_forecast=ForecastVintage(
            code="RF_MAR",
            as_of_period=period,
            values=build_series(
                2027,
                ["100", "180", "220"],
            ),
        ),
        metric_type=FinancialMetricType.REVENUE,
    )

    assert report.ytd.actual_vs_plan.actual == Decimal("550")
    assert report.ytd.actual_vs_plan.comparator == Decimal("450")
    assert report.ytd.actual_vs_plan.variance.amount == Decimal("100")

    assert report.ytd.actual_vs_forecast.actual == Decimal("550")
    assert report.ytd.actual_vs_forecast.comparator == Decimal("500")
    assert report.ytd.actual_vs_forecast.variance.amount == Decimal("50")


def test_builds_qtd_variance_report() -> None:
    period = PlanningPeriod(2027, 5)

    report = VarianceReportEngine.calculate(
        period=period,
        actual=build_series(
            2027,
            ["100", "100", "100", "200", "220"],
        ),
        plan=build_series(
            2027,
            ["100", "100", "100", "170", "190"],
        ),
        latest_forecast=ForecastVintage(
            code="RF_MAY",
            as_of_period=period,
            values=build_series(
                2027,
                ["100", "100", "100", "180", "200"],
            ),
        ),
        metric_type=FinancialMetricType.REVENUE,
    )

    assert report.qtd.actual_vs_plan.actual == Decimal("420")
    assert report.qtd.actual_vs_plan.comparator == Decimal("360")
    assert report.qtd.actual_vs_plan.variance.amount == Decimal("60")

    assert report.qtd.actual_vs_forecast.comparator == Decimal("380")
    assert report.qtd.actual_vs_forecast.variance.amount == Decimal("40")
