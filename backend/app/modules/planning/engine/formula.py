from dataclasses import dataclass
from enum import StrEnum


class FormulaOperation(StrEnum):
    """Supported operations for calculated planning metrics."""

    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


@dataclass(frozen=True, slots=True)
class FormulaDefinition:
    """Defines a calculated metric and its dependencies."""

    code: str
    operation: FormulaOperation
    operands: tuple[str, ...]
