from decimal import Decimal

from app.modules.planning.engine import (
    FinancialPlanEngine,
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
            for index, value in enumerate(values, start=1)
        ]
    )


def test_calculates_monthly_financial_plan() -> None:
    result = FinancialPlanEngine.calculate(
        volume=build_series(
            2027,
            ["100", "120", "150"],
        ),
        unit_price=build_series(
            2027,
            ["10", "10", "12"],
        ),
        gross_margin_rate=build_series(
            2027,
            ["0.40", "0.40", "0.40"],
        ),
        headcount=build_series(
            2027,
            ["2", "2", "3"],
        ),
        cost_per_employee=build_series(
            2027,
            ["100", "100", "100"],
        ),
        opex=build_series(
            2027,
            ["50", "60", "70"],
        ),
    )

    january = PlanningPeriod(2027, 1)
    february = PlanningPeriod(2027, 2)
    march = PlanningPeriod(2027, 3)

    assert result.revenue.get(january) == Decimal("1000")
    assert result.revenue.get(february) == Decimal("1200")
    assert result.revenue.get(march) == Decimal("1800")

    assert result.gross_profit.get(january) == Decimal("400.00")
    assert result.payroll.get(january) == Decimal("200")

    assert result.ebitda.get(january) == Decimal("150.00")
    assert result.ebitda.get(february) == Decimal("220.00")
    assert result.ebitda.get(march) == Decimal("350.00")


def test_calculates_annual_totals() -> None:
    result = FinancialPlanEngine.calculate(
        volume=build_series(
            2027,
            ["100", "120", "150"],
        ),
        unit_price=build_series(
            2027,
            ["10", "10", "12"],
        ),
        gross_margin_rate=build_series(
            2027,
            ["0.40", "0.40", "0.40"],
        ),
        headcount=build_series(
            2027,
            ["2", "2", "3"],
        ),
        cost_per_employee=build_series(
            2027,
            ["100", "100", "100"],
        ),
        opex=build_series(
            2027,
            ["50", "60", "70"],
        ),
    )

    assert result.annual_revenue == Decimal("4000")
    assert result.annual_gross_profit == Decimal("1600.00")
    assert result.annual_payroll == Decimal("700")
    assert result.annual_opex == Decimal("180")
    assert result.annual_ebitda == Decimal("720.00")


def test_supports_full_twelve_month_plan() -> None:
    result = FinancialPlanEngine.calculate(
        volume=build_series(
            2027,
            ["100"] * 12,
        ),
        unit_price=build_series(
            2027,
            ["10"] * 12,
        ),
        gross_margin_rate=build_series(
            2027,
            ["0.40"] * 12,
        ),
        headcount=build_series(
            2027,
            ["2"] * 12,
        ),
        cost_per_employee=build_series(
            2027,
            ["100"] * 12,
        ),
        opex=build_series(
            2027,
            ["50"] * 12,
        ),
    )

    assert len(result.revenue.periods()) == 12

    assert result.annual_revenue == Decimal("12000")
    assert result.annual_gross_profit == Decimal("4800.00")
    assert result.annual_payroll == Decimal("2400")
    assert result.annual_opex == Decimal("600")
    assert result.annual_ebitda == Decimal("1800.00")
