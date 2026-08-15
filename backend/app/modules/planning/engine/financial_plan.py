from dataclasses import dataclass
from decimal import Decimal

from app.modules.planning.engine.period_evaluator import PeriodCalculationEngine
from app.modules.planning.engine.series import PlanningSeries


@dataclass(frozen=True, slots=True)
class FinancialPlanResult:
    """Calculated outputs for a driver-based financial plan."""

    revenue: PlanningSeries
    gross_profit: PlanningSeries
    payroll: PlanningSeries
    opex: PlanningSeries
    ebitda: PlanningSeries

    @property
    def annual_revenue(self) -> Decimal:
        return self.revenue.total()

    @property
    def annual_gross_profit(self) -> Decimal:
        return self.gross_profit.total()

    @property
    def annual_payroll(self) -> Decimal:
        return self.payroll.total()

    @property
    def annual_opex(self) -> Decimal:
        return self.opex.total()

    @property
    def annual_ebitda(self) -> Decimal:
        return self.ebitda.total()


class FinancialPlanEngine:
    """Orchestrate a period-aware driver-based financial plan."""

    @staticmethod
    def calculate(
        *,
        volume: PlanningSeries,
        unit_price: PlanningSeries,
        gross_margin_rate: PlanningSeries,
        headcount: PlanningSeries,
        cost_per_employee: PlanningSeries,
        opex: PlanningSeries,
    ) -> FinancialPlanResult:
        """Calculate revenue, gross profit, payroll, and EBITDA."""

        revenue = PeriodCalculationEngine.multiply(
            left=volume,
            right=unit_price,
        )

        gross_profit = PeriodCalculationEngine.apply_rate(
            base=revenue,
            rate=gross_margin_rate,
        )

        payroll = PeriodCalculationEngine.multiply(
            left=headcount,
            right=cost_per_employee,
        )

        profit_after_payroll = PeriodCalculationEngine.subtract(
            left=gross_profit,
            right=payroll,
        )

        ebitda = PeriodCalculationEngine.subtract(
            left=profit_after_payroll,
            right=opex,
        )

        return FinancialPlanResult(
            revenue=revenue,
            gross_profit=gross_profit,
            payroll=payroll,
            opex=opex,
            ebitda=ebitda,
        )
