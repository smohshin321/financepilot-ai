from decimal import Decimal

from app.modules.planning.engine import (
    FinancialMetricType,
    VarianceEngine,
    VarianceFavorability,
)


def test_actual_above_plan() -> None:
    result = VarianceEngine.calculate(
        actual=Decimal("200"),
        comparator=Decimal("150"),
    )

    assert result.actual == Decimal("200")
    assert result.comparator == Decimal("150")
    assert result.amount == Decimal("50")
    assert result.percentage == Decimal("50") / Decimal("150")


def test_actual_below_plan() -> None:
    result = VarianceEngine.calculate(
        actual=Decimal("120"),
        comparator=Decimal("150"),
    )

    assert result.amount == Decimal("-30")
    assert result.percentage == Decimal("-30") / Decimal("150")


def test_actual_equals_plan() -> None:
    result = VarianceEngine.calculate(
        actual=Decimal("150"),
        comparator=Decimal("150"),
    )

    assert result.amount == Decimal("0")
    assert result.percentage == Decimal("0")


def test_zero_comparator_has_no_percentage_variance() -> None:
    result = VarianceEngine.calculate(
        actual=Decimal("100"),
        comparator=Decimal("0"),
    )

    assert result.amount == Decimal("100")
    assert result.percentage is None


def test_negative_comparator_uses_absolute_denominator() -> None:
    result = VarianceEngine.calculate(
        actual=Decimal("-80"),
        comparator=Decimal("-100"),
    )

    assert result.amount == Decimal("20")
    assert result.percentage == Decimal("0.2")


def test_actual_vs_plan_and_rolling_forecast() -> None:
    actual = Decimal("200")
    plan = Decimal("150")
    rolling_forecast = Decimal("180")

    versus_plan = VarianceEngine.calculate(
        actual=actual,
        comparator=plan,
    )

    versus_forecast = VarianceEngine.calculate(
        actual=actual,
        comparator=rolling_forecast,
    )

    assert versus_plan.amount == Decimal("50")
    assert versus_forecast.amount == Decimal("20")


def test_revenue_positive_variance_is_favorable() -> None:
    result = VarianceEngine.calculate(
        actual=Decimal("200"),
        comparator=Decimal("150"),
        metric_type=FinancialMetricType.REVENUE,
    )

    assert result.favorability == VarianceFavorability.FAVORABLE


def test_revenue_negative_variance_is_unfavorable() -> None:
    result = VarianceEngine.calculate(
        actual=Decimal("120"),
        comparator=Decimal("150"),
        metric_type=FinancialMetricType.REVENUE,
    )

    assert result.favorability == VarianceFavorability.UNFAVORABLE


def test_expense_positive_variance_is_unfavorable() -> None:
    result = VarianceEngine.calculate(
        actual=Decimal("120"),
        comparator=Decimal("100"),
        metric_type=FinancialMetricType.EXPENSE,
    )

    assert result.favorability == VarianceFavorability.UNFAVORABLE


def test_expense_negative_variance_is_favorable() -> None:
    result = VarianceEngine.calculate(
        actual=Decimal("80"),
        comparator=Decimal("100"),
        metric_type=FinancialMetricType.EXPENSE,
    )

    assert result.favorability == VarianceFavorability.FAVORABLE


def test_zero_variance_is_neutral() -> None:
    result = VarianceEngine.calculate(
        actual=Decimal("100"),
        comparator=Decimal("100"),
        metric_type=FinancialMetricType.EXPENSE,
    )

    assert result.favorability == VarianceFavorability.NEUTRAL


def test_profit_positive_variance_is_favorable() -> None:
    result = VarianceEngine.calculate(
        actual=Decimal("300"),
        comparator=Decimal("250"),
        metric_type=FinancialMetricType.PROFIT,
    )

    assert result.favorability == VarianceFavorability.FAVORABLE
