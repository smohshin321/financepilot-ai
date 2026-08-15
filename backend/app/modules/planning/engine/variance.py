from dataclasses import dataclass
from decimal import Decimal

from app.modules.planning.engine.variance_types import (
    FinancialMetricType,
    VarianceFavorability,
)


@dataclass(frozen=True, slots=True)
class VarianceResult:
    """Represents a variance between an actual value and a comparator."""

    actual: Decimal
    comparator: Decimal
    amount: Decimal
    percentage: Decimal | None
    favorability: VarianceFavorability


class VarianceEngine:
    """Calculate and interpret financial variances."""

    @staticmethod
    def calculate(
        *,
        actual: Decimal,
        comparator: Decimal,
        metric_type: FinancialMetricType = FinancialMetricType.REVENUE,
    ) -> VarianceResult:
        """Calculate amount, percentage, and business favorability."""

        amount = actual - comparator

        percentage = amount / abs(comparator) if comparator != Decimal("0") else None

        favorability = VarianceEngine._favorability(
            amount=amount,
            metric_type=metric_type,
        )

        return VarianceResult(
            actual=actual,
            comparator=comparator,
            amount=amount,
            percentage=percentage,
            favorability=favorability,
        )

    @staticmethod
    def _favorability(
        *,
        amount: Decimal,
        metric_type: FinancialMetricType,
    ) -> VarianceFavorability:
        if amount == Decimal("0"):
            return VarianceFavorability.NEUTRAL

        if metric_type in {
            FinancialMetricType.REVENUE,
            FinancialMetricType.PROFIT,
        }:
            return (
                VarianceFavorability.FAVORABLE
                if amount > Decimal("0")
                else VarianceFavorability.UNFAVORABLE
            )

        if metric_type == FinancialMetricType.EXPENSE:
            return (
                VarianceFavorability.FAVORABLE
                if amount < Decimal("0")
                else VarianceFavorability.UNFAVORABLE
            )

        raise ValueError(f"Unsupported financial metric type: {metric_type}.")
