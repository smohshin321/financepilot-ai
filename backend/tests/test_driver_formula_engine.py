from decimal import Decimal

import pytest
from app.modules.planning.engine import (
    CircularDependencyError,
    DivisionByZeroFormulaError,
    FormulaDefinition,
    FormulaEvaluationError,
    FormulaEvaluator,
    FormulaOperation,
    MissingFormulaInputError,
)


def test_evaluates_revenue_from_volume_and_price() -> None:
    evaluator = FormulaEvaluator(
        values={
            "sales_volume": Decimal("1000"),
            "average_price": Decimal("25"),
        },
        formulas={
            "revenue": FormulaDefinition(
                code="revenue",
                operation=FormulaOperation.MULTIPLY,
                operands=("sales_volume", "average_price"),
            ),
        },
    )

    assert evaluator.evaluate("revenue") == Decimal("25000")


def test_evaluates_dependency_chain() -> None:
    evaluator = FormulaEvaluator(
        values={
            "sales_volume": Decimal("1000"),
            "average_price": Decimal("25"),
            "gross_margin_rate": Decimal("0.40"),
            "payroll": Decimal("5000"),
            "opex": Decimal("2000"),
        },
        formulas={
            "revenue": FormulaDefinition(
                code="revenue",
                operation=FormulaOperation.MULTIPLY,
                operands=("sales_volume", "average_price"),
            ),
            "gross_profit": FormulaDefinition(
                code="gross_profit",
                operation=FormulaOperation.MULTIPLY,
                operands=("revenue", "gross_margin_rate"),
            ),
            "ebitda": FormulaDefinition(
                code="ebitda",
                operation=FormulaOperation.SUBTRACT,
                operands=("gross_profit", "payroll", "opex"),
            ),
        },
    )

    assert evaluator.evaluate("revenue") == Decimal("25000")
    assert evaluator.evaluate("gross_profit") == Decimal("10000.00")
    assert evaluator.evaluate("ebitda") == Decimal("3000.00")


def test_adds_multiple_operands() -> None:
    evaluator = FormulaEvaluator(
        values={
            "product_a": Decimal("100"),
            "product_b": Decimal("200"),
            "product_c": Decimal("300"),
        },
        formulas={
            "total_revenue": FormulaDefinition(
                code="total_revenue",
                operation=FormulaOperation.ADD,
                operands=("product_a", "product_b", "product_c"),
            ),
        },
    )

    assert evaluator.evaluate("total_revenue") == Decimal("600")


def test_divides_values() -> None:
    evaluator = FormulaEvaluator(
        values={
            "gross_profit": Decimal("400"),
            "revenue": Decimal("1000"),
        },
        formulas={
            "gross_margin": FormulaDefinition(
                code="gross_margin",
                operation=FormulaOperation.DIVIDE,
                operands=("gross_profit", "revenue"),
            ),
        },
    )

    assert evaluator.evaluate("gross_margin") == Decimal("0.4")


def test_missing_input_raises_error() -> None:
    evaluator = FormulaEvaluator(
        values={"sales_volume": Decimal("100")},
        formulas={
            "revenue": FormulaDefinition(
                code="revenue",
                operation=FormulaOperation.MULTIPLY,
                operands=("sales_volume", "average_price"),
            ),
        },
    )

    with pytest.raises(MissingFormulaInputError):
        evaluator.evaluate("revenue")


def test_circular_dependency_raises_error() -> None:
    evaluator = FormulaEvaluator(
        values={"constant": Decimal("1")},
        formulas={
            "metric_a": FormulaDefinition(
                code="metric_a",
                operation=FormulaOperation.ADD,
                operands=("metric_b", "constant"),
            ),
            "metric_b": FormulaDefinition(
                code="metric_b",
                operation=FormulaOperation.ADD,
                operands=("metric_a", "constant"),
            ),
        },
    )

    with pytest.raises(CircularDependencyError):
        evaluator.evaluate("metric_a")


def test_division_by_zero_raises_error() -> None:
    evaluator = FormulaEvaluator(
        values={
            "gross_profit": Decimal("100"),
            "revenue": Decimal("0"),
        },
        formulas={
            "gross_margin": FormulaDefinition(
                code="gross_margin",
                operation=FormulaOperation.DIVIDE,
                operands=("gross_profit", "revenue"),
            ),
        },
    )

    with pytest.raises(DivisionByZeroFormulaError):
        evaluator.evaluate("gross_margin")


def test_formula_requires_at_least_two_operands() -> None:
    evaluator = FormulaEvaluator(
        values={"revenue": Decimal("100")},
        formulas={
            "invalid_metric": FormulaDefinition(
                code="invalid_metric",
                operation=FormulaOperation.ADD,
                operands=("revenue",),
            ),
        },
    )

    with pytest.raises(FormulaEvaluationError):
        evaluator.evaluate("invalid_metric")
