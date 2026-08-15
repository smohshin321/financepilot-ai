from decimal import Decimal

from app.modules.planning.engine import (
    FinancialMetricType,
    PeriodValue,
    PlanningPeriod,
    PlanningSeries,
    VarianceFavorability,
    VarianceSeriesEngine,
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


def test_calculates_monthly_variances() -> None:
    actual = build_series(
        2027,
        ["100", "200", "250"],
    )
    plan = build_series(
        2027,
        ["100", "150", "200"],
    )

    results = VarianceSeriesEngine.calculate_periods(
        actual=actual,
        comparator=plan,
        metric_type=FinancialMetricType.REVENUE,
    )

    assert len(results) == 3
    assert results[0].variance.amount == Decimal("0")
    assert results[1].variance.amount == Decimal("50")
    assert results[2].variance.amount == Decimal("50")


def test_calculates_ytd_variance() -> None:
    actual = build_series(
        2027,
        ["100", "200", "250"],
    )
    plan = build_series(
        2027,
        ["100", "150", "200"],
    )

    result = VarianceSeriesEngine.calculate_ytd(
        actual=actual,
        comparator=plan,
        through_period=PlanningPeriod(2027, 2),
        metric_type=FinancialMetricType.REVENUE,
    )

    assert result.actual == Decimal("300")
    assert result.comparator == Decimal("250")
    assert result.variance.amount == Decimal("50")
    assert result.variance.favorability == VarianceFavorability.FAVORABLE


def test_calculates_qtd_variance_in_q1() -> None:
    actual = build_series(
        2027,
        ["100", "200", "250"],
    )
    plan = build_series(
        2027,
        ["100", "150", "200"],
    )

    result = VarianceSeriesEngine.calculate_qtd(
        actual=actual,
        comparator=plan,
        through_period=PlanningPeriod(2027, 2),
        metric_type=FinancialMetricType.REVENUE,
    )

    assert result.actual == Decimal("300")
    assert result.comparator == Decimal("250")
    assert result.variance.amount == Decimal("50")


def test_calculates_qtd_variance_in_q2() -> None:
    actual = build_series(
        2027,
        ["100", "100", "100", "200", "220"],
    )
    forecast = build_series(
        2027,
        ["100", "100", "100", "180", "200"],
    )

    result = VarianceSeriesEngine.calculate_qtd(
        actual=actual,
        comparator=forecast,
        through_period=PlanningPeriod(2027, 5),
        metric_type=FinancialMetricType.REVENUE,
    )

    assert result.actual == Decimal("420")
    assert result.comparator == Decimal("380")
    assert result.variance.amount == Decimal("40")


def test_expense_ytd_variance_uses_expense_favorability() -> None:
    actual = build_series(
        2027,
        ["90", "95", "100"],
    )
    plan = build_series(
        2027,
        ["100", "100", "100"],
    )

    result = VarianceSeriesEngine.calculate_ytd(
        actual=actual,
        comparator=plan,
        through_period=PlanningPeriod(2027, 3),
        metric_type=FinancialMetricType.EXPENSE,
    )

    assert result.variance.amount == Decimal("-15")
    assert result.variance.favorability == VarianceFavorability.FAVORABLE
