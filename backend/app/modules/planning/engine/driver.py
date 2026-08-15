from dataclasses import dataclass
from decimal import Decimal

from app.modules.planning.engine.driver_types import DriverType


@dataclass(frozen=True, slots=True)
class PlanningDriver:
    """Represents an input driver used by the planning engine."""

    code: str
    driver_type: DriverType
    value: Decimal
