from unittest.mock import Mock
from uuid import uuid4

import pytest
from app.modules.planning.models import BudgetVersion
from app.modules.planning.schemas import (
    BudgetVersionCreate,
    BudgetVersionResponse,
)
from pydantic import ValidationError


def test_budget_version_create_accepts_valid_payload() -> None:
    payload = BudgetVersionCreate(
        version_number=1,
        version_name="Working Budget",
        description="Initial management working version",
    )

    assert payload.version_number == 1
    assert payload.version_name == "Working Budget"
    assert payload.description == "Initial management working version"


def test_budget_version_create_description_is_optional() -> None:
    payload = BudgetVersionCreate(
        version_number=2,
        version_name="Management Review",
    )

    assert payload.description is None


def test_budget_version_create_rejects_invalid_version_number() -> None:
    with pytest.raises(ValidationError):
        BudgetVersionCreate(
            version_number=0,
            version_name="Invalid Version",
        )


def test_budget_version_create_rejects_empty_name() -> None:
    with pytest.raises(ValidationError):
        BudgetVersionCreate(
            version_number=1,
            version_name="",
        )


def test_budget_version_create_rejects_name_over_maximum_length() -> None:
    with pytest.raises(ValidationError):
        BudgetVersionCreate(
            version_number=1,
            version_name="A" * 151,
        )


def test_budget_version_response_supports_attribute_mapping() -> None:
    budget_version = Mock(spec=BudgetVersion)

    budget_version.id = uuid4()
    budget_version.scenario_id = uuid4()
    budget_version.version_number = 1
    budget_version.version_name = "Working Budget"
    budget_version.description = "Initial management working version"
    budget_version.is_active = True
    budget_version.is_locked = False

    response = BudgetVersionResponse.model_validate(budget_version)

    assert response.id == budget_version.id
    assert response.scenario_id == budget_version.scenario_id
    assert response.version_number == 1
    assert response.version_name == "Working Budget"
    assert response.is_active is True
    assert response.is_locked is False
