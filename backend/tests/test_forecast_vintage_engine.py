from decimal import Decimal

from app.modules.planning.engine import (
    FinancialMetricType,
    ForecastVintage,
    ForecastVintageEngine,
    PeriodValue,
    PlanningPeriod,
    PlanningSeries,
    VarianceFavorability,
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


def test_actual_vs_plan_and_latest_forecast() -> None:
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

    result = ForecastVintageEngine.compare_actual(
        period=period,
        actual=actual,
        plan=plan,
        latest_forecast=latest_forecast,
        metric_type=FinancialMetricType.REVENUE,
    )

    assert result.actual == Decimal("200")
    assert result.plan == Decimal("150")
    assert result.latest_forecast == Decimal("180")

    assert result.actual_vs_plan.amount == Decimal("50")
    assert result.actual_vs_forecast.amount == Decimal("20")

    assert result.actual_vs_plan.favorability == VarianceFavorability.FAVORABLE

    assert result.actual_vs_forecast.favorability == VarianceFavorability.FAVORABLE


def test_forecast_revision_between_vintages() -> None:
    period = PlanningPeriod(2027, 2)

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

    result = ForecastVintageEngine.compare_forecasts(
        period=period,
        prior_forecast=prior_forecast,
        latest_forecast=latest_forecast,
    )

    assert result.prior_forecast == Decimal("150")
    assert result.latest_forecast == Decimal("180")
    assert result.revision_amount == Decimal("30")
    assert result.revision_percentage == Decimal("0.2")


def test_forecast_revision_handles_zero_prior_value() -> None:
    period = PlanningPeriod(2027, 2)

    prior_forecast = ForecastVintage(
        code="RF_JAN",
        as_of_period=PlanningPeriod(2027, 1),
        values=build_series(
            2027,
            ["100", "0", "200"],
        ),
    )

    latest_forecast = ForecastVintage(
        code="RF_FEB",
        as_of_period=PlanningPeriod(2027, 2),
        values=build_series(
            2027,
            ["100", "50", "220"],
        ),
    )

    result = ForecastVintageEngine.compare_forecasts(
        period=period,
        prior_forecast=prior_forecast,
        latest_forecast=latest_forecast,
    )

    assert result.revision_amount == Decimal("50")
    assert result.revision_percentage is None


def test_expense_actual_vs_forecast_uses_expense_favorability() -> None:
    period = PlanningPeriod(2027, 2)

    actual = build_series(
        2027,
        ["100", "90", "100"],
    )
    plan = build_series(
        2027,
        ["100", "100", "100"],
    )

    latest_forecast = ForecastVintage(
        code="RF_FEB",
        as_of_period=PlanningPeriod(2027, 2),
        values=build_series(
            2027,
            ["100", "95", "100"],
        ),
    )

    result = ForecastVintageEngine.compare_actual(
        period=period,
        actual=actual,
        plan=plan,
        latest_forecast=latest_forecast,
        metric_type=FinancialMetricType.EXPENSE,
    )

    assert result.actual_vs_plan.amount == Decimal("-10")
    assert result.actual_vs_forecast.amount == Decimal("-5")

    assert result.actual_vs_forecast.favorability == VarianceFavorability.FAVORABLE
