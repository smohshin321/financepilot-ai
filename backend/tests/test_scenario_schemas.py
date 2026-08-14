from unittest.mock import Mock
from uuid import uuid4

import pytest
from app.modules.planning.models import Scenario
from app.modules.planning.schemas import ScenarioCreate, ScenarioResponse
from pydantic import ValidationError


def test_scenario_create_accepts_valid_payload() -> None:
    payload = ScenarioCreate(
        code="BASE",
        name="Base Case",
        description="Management base-case assumptions",
        is_default=True,
    )

    assert payload.code == "BASE"
    assert payload.name == "Base Case"
    assert payload.description == "Management base-case assumptions"
    assert payload.is_default is True


def test_scenario_create_uses_default_values() -> None:
    payload = ScenarioCreate(
        code="UPSIDE",
        name="Upside Case",
    )

    assert payload.description is None
    assert payload.is_default is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("code", ""),
        ("name", ""),
    ],
)
def test_scenario_create_rejects_empty_required_fields(
    field: str,
    value: str,
) -> None:
    payload = {
        "code": "BASE",
        "name": "Base Case",
    }
    payload[field] = value

    with pytest.raises(ValidationError):
        ScenarioCreate(**payload)


def test_scenario_create_rejects_code_over_maximum_length() -> None:
    with pytest.raises(ValidationError):
        ScenarioCreate(
            code="A" * 101,
            name="Base Case",
        )


def test_scenario_response_supports_attribute_mapping() -> None:
    scenario = Mock(spec=Scenario)

    scenario.id = uuid4()
    scenario.planning_cycle_id = uuid4()
    scenario.code = "BASE"
    scenario.name = "Base Case"
    scenario.description = "Management base-case assumptions"
    scenario.is_default = True
    scenario.is_active = True

    response = ScenarioResponse.model_validate(scenario)

    assert response.id == scenario.id
    assert response.planning_cycle_id == scenario.planning_cycle_id
    assert response.code == "BASE"
    assert response.name == "Base Case"
    assert response.is_default is True
    assert response.is_active is True
