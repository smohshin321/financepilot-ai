from decimal import Decimal

from app.modules.planning.engine.formula import (
    FormulaDefinition,
    FormulaOperation,
)


class FormulaEvaluationError(Exception):
    """Base exception for formula-evaluation failures."""


class MissingFormulaInputError(FormulaEvaluationError):
    """Raised when neither a value nor formula exists for an input."""

    def __init__(self, code: str) -> None:
        super().__init__(f"Formula input '{code}' is missing.")
        self.code = code


class CircularDependencyError(FormulaEvaluationError):
    """Raised when formulas contain a circular dependency."""

    def __init__(self, code: str) -> None:
        super().__init__(f"Circular formula dependency detected at '{code}'.")
        self.code = code


class DivisionByZeroFormulaError(FormulaEvaluationError):
    """Raised when a planning formula attempts division by zero."""


class FormulaEvaluator:
    """Evaluate dependency-aware financial planning formulas."""

    def __init__(
        self,
        *,
        values: dict[str, Decimal],
        formulas: dict[str, FormulaDefinition],
    ) -> None:
        self._values = dict(values)
        self._formulas = formulas
        self._resolving: set[str] = set()

    def evaluate(self, code: str) -> Decimal:
        """Resolve a value, recursively evaluating its dependencies."""

        if code in self._values:
            return self._values[code]

        if code in self._resolving:
            raise CircularDependencyError(code)

        formula = self._formulas.get(code)

        if formula is None:
            raise MissingFormulaInputError(code)

        self._resolving.add(code)

        try:
            operands = [self.evaluate(operand) for operand in formula.operands]

            result = self._calculate(
                operation=formula.operation,
                operands=operands,
            )
        finally:
            self._resolving.remove(code)

        self._values[code] = result

        return result

    @staticmethod
    def _calculate(
        *,
        operation: FormulaOperation,
        operands: list[Decimal],
    ) -> Decimal:
        if len(operands) < 2:
            raise FormulaEvaluationError("A formula requires at least two operands.")

        result = operands[0]

        for operand in operands[1:]:
            if operation == FormulaOperation.ADD:
                result += operand
            elif operation == FormulaOperation.SUBTRACT:
                result -= operand
            elif operation == FormulaOperation.MULTIPLY:
                result *= operand
            elif operation == FormulaOperation.DIVIDE:
                if operand == Decimal("0"):
                    raise DivisionByZeroFormulaError("Formula cannot divide by zero.")
                result /= operand
            else:
                raise FormulaEvaluationError(f"Unsupported formula operation: {operation}.")

        return result
