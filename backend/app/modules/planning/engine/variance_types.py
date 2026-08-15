from enum import StrEnum


class FinancialMetricType(StrEnum):
    """Financial metric categories used for variance interpretation."""

    REVENUE = "revenue"
    EXPENSE = "expense"
    PROFIT = "profit"


class VarianceFavorability(StrEnum):
    """Business interpretation of a financial variance."""

    FAVORABLE = "favorable"
    UNFAVORABLE = "unfavorable"
    NEUTRAL = "neutral"
