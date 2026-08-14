from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

import pytest
from app.modules.planning.models import BudgetLine
from app.modules.planning.schemas import (
    BudgetLineCreate,
    BudgetLineResponse,
    BudgetLineUpdate,
)
from pydantic import ValidationError


def test_budget_line_create_accepts_valid_payload() -> None:
    account_id = uuid4()
    department_id = uuid4()
    cost_center_id = uuid4()

    payload = BudgetLineCreate(
        account_id=account_id,
        department_id=department_id,
        cost_center_id=cost_center_id,
        period=1,
        amount=Decimal("125000.50"),
        currency="CAD",
        notes="January operating expense",
    )

    assert payload.account_id == account_id
    assert payload.department_id == department_id
    assert payload.cost_center_id == cost_center_id
    assert payload.period == 1
    assert payload.amount == Decimal("125000.50")
    assert payload.currency == "CAD"


def test_budget_line_create_allows_optional_dimensions() -> None:
    payload = BudgetLineCreate(
        period=12,
        amount=Decimal("0"),
        currency="USD",
    )

    assert payload.account_id is None
    assert payload.department_id is None
    assert payload.cost_center_id is None
    assert payload.notes is None


@pytest.mark.parametrize(
    "period",
    [0, 13],
)
def test_budget_line_create_rejects_invalid_period(
    period: int,
) -> None:
    with pytest.raises(ValidationError):
        BudgetLineCreate(
            period=period,
            amount=Decimal("100"),
            currency="CAD",
        )


def test_budget_line_create_rejects_negative_amount() -> None:
    with pytest.raises(ValidationError):
        BudgetLineCreate(
            period=1,
            amount=Decimal("-1"),
            currency="CAD",
        )


@pytest.mark.parametrize(
    "currency",
    ["CA", "CADA"],
)
def test_budget_line_create_rejects_invalid_currency_length(
    currency: str,
) -> None:
    with pytest.raises(ValidationError):
        BudgetLineCreate(
            period=1,
            amount=Decimal("100"),
            currency=currency,
        )


def test_budget_line_update_accepts_valid_payload() -> None:
    payload = BudgetLineUpdate(
        period=6,
        amount=Decimal("2500"),
        currency="CAD",
        notes="Updated forecast assumption",
    )

    assert payload.period == 6
    assert payload.amount == Decimal("2500")
    assert payload.currency == "CAD"
    assert payload.notes == "Updated forecast assumption"


def test_budget_line_response_supports_attribute_mapping() -> None:
    budget_line = Mock(spec=BudgetLine)

    budget_line.id = uuid4()
    budget_line.budget_version_id = uuid4()
    budget_line.account_id = uuid4()
    budget_line.department_id = uuid4()
    budget_line.cost_center_id = uuid4()
    budget_line.period = 3
    budget_line.amount = Decimal("5000.2500")
    budget_line.currency = "CAD"
    budget_line.notes = "Quarter planning assumption"

    response = BudgetLineResponse.model_validate(budget_line)

    assert response.id == budget_line.id
    assert response.budget_version_id == budget_line.budget_version_id
    assert response.period == 3
    assert response.amount == Decimal("5000.2500")
    assert response.currency == "CAD"
    assert response.notes == "Quarter planning assumption"
