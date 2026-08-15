from decimal import Decimal

import pytest
from app.modules.planning.engine import (
    DuplicatePlanningPeriodError,
    MissingPlanningPeriodError,
    PeriodAlignmentError,
    PeriodCalculationEngine,
    PeriodValue,
    PlanningPeriod,
    PlanningSeries,
)


def build_series(
    year: int,
    values: list[str],
) -> PlanningSeries:
    return PlanningSeries(
        [
            PeriodValue(
                period=PlanningPeriod(
                    year=year,
                    month=index,
                ),
                value=Decimal(value),
            )
            for index, value in enumerate(
                values,
                start=1,
            )
        ]
    )


def test_planning_period_code() -> None:
    period = PlanningPeriod(
        year=2027,
        month=3,
    )

    assert period.code == "2027-03"


@pytest.mark.parametrize(
    "month",
    [0, 13],
)
def test_planning_period_rejects_invalid_month(
    month: int,
) -> None:
    with pytest.raises(ValueError):
        PlanningPeriod(
            year=2027,
            month=month,
        )


def test_series_returns_period_value() -> None:
    series = build_series(
        2027,
        ["100", "200", "300"],
    )

    assert series.get(PlanningPeriod(2027, 2)) == Decimal("200")


def test_series_total() -> None:
    series = build_series(
        2027,
        ["100", "200", "300"],
    )

    assert series.total() == Decimal("600")


def test_period_revenue_calculation() -> None:
    volume = build_series(
        2027,
        ["100", "120", "150"],
    )
    price = build_series(
        2027,
        ["10", "10", "12"],
    )

    revenue = PeriodCalculationEngine.multiply(
        left=volume,
        right=price,
    )

    assert revenue.get(PlanningPeriod(2027, 1)) == Decimal("1000")

    assert revenue.get(PlanningPeriod(2027, 2)) == Decimal("1200")

    assert revenue.get(PlanningPeriod(2027, 3)) == Decimal("1800")

    assert revenue.total() == Decimal("4000")


def test_period_percent_of_revenue_calculation() -> None:
    revenue = build_series(
        2027,
        ["1000", "1200", "1800"],
    )

    marketing_rate = build_series(
        2027,
        ["0.05", "0.05", "0.06"],
    )

    marketing = PeriodCalculationEngine.apply_rate(
        base=revenue,
        rate=marketing_rate,
    )

    assert marketing.get(PlanningPeriod(2027, 1)) == Decimal("50.00")

    assert marketing.get(PlanningPeriod(2027, 3)) == Decimal("108.00")


def test_period_growth_calculation() -> None:
    base = build_series(
        2027,
        ["1000", "1100", "1200"],
    )

    growth = build_series(
        2027,
        ["0.10", "0.05", "0.20"],
    )

    result = PeriodCalculationEngine.apply_growth(
        base=base,
        growth_rate=growth,
    )

    assert result.get(PlanningPeriod(2027, 1)) == Decimal("1100.00")

    assert result.get(PlanningPeriod(2027, 2)) == Decimal("1155.00")

    assert result.get(PlanningPeriod(2027, 3)) == Decimal("1440.00")


def test_period_subtraction_calculation() -> None:
    gross_profit = build_series(
        2027,
        ["500", "600", "700"],
    )

    opex = build_series(
        2027,
        ["100", "150", "200"],
    )

    ebitda = PeriodCalculationEngine.subtract(
        left=gross_profit,
        right=opex,
    )

    assert ebitda.get(PlanningPeriod(2027, 1)) == Decimal("400")

    assert ebitda.get(PlanningPeriod(2027, 3)) == Decimal("500")


def test_missing_period_raises_error() -> None:
    series = build_series(
        2027,
        ["100"],
    )

    with pytest.raises(MissingPlanningPeriodError):
        series.get(PlanningPeriod(2027, 2))


def test_duplicate_period_is_rejected() -> None:
    period = PlanningPeriod(2027, 1)

    with pytest.raises(DuplicatePlanningPeriodError):
        PlanningSeries(
            [
                PeriodValue(
                    period=period,
                    value=Decimal("100"),
                ),
                PeriodValue(
                    period=period,
                    value=Decimal("200"),
                ),
            ]
        )


def test_multiply_rejects_misaligned_periods() -> None:
    left = build_series(
        2027,
        ["100", "200", "300"],
    )
    right = build_series(
        2027,
        ["10", "20"],
    )

    with pytest.raises(PeriodAlignmentError):
        PeriodCalculationEngine.multiply(
            left=left,
            right=right,
        )


def test_subtract_rejects_misaligned_periods() -> None:
    left = build_series(
        2027,
        ["500", "600"],
    )
    right = build_series(
        2027,
        ["100"],
    )

    with pytest.raises(PeriodAlignmentError):
        PeriodCalculationEngine.subtract(
            left=left,
            right=right,
        )


def test_growth_rejects_misaligned_periods() -> None:
    base = build_series(
        2027,
        ["1000", "1100", "1200"],
    )
    growth = build_series(
        2027,
        ["0.10", "0.05"],
    )

    with pytest.raises(PeriodAlignmentError):
        PeriodCalculationEngine.apply_growth(
            base=base,
            growth_rate=growth,
        )
