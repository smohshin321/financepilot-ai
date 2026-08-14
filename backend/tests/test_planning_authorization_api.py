from unittest.mock import AsyncMock
from uuid import uuid4

from app.main import app
from app.modules.identity.api.dependencies import get_current_user_context
from app.modules.identity.schemas import CurrentUserContext
from app.modules.planning.api.authorization import (
    require_budget_manage,
    require_budget_read,
    require_budget_write,
)
from app.modules.planning.api.dependencies import (
    get_planning_cycle_service,
    get_scenario_service,
)
from fastapi.testclient import TestClient


def build_current_user() -> CurrentUserContext:
    return CurrentUserContext(
        user_id=uuid4(),
        membership_id=uuid4(),
        organization_id=uuid4(),
        role_ids=[],
    )


def test_budget_read_permission_is_required() -> None:
    current_user = build_current_user()
    planning_cycle_service = AsyncMock()

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/planning-cycles")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json() == {"detail": "Permission 'budget.read' is required."}


def test_budget_write_permission_is_required() -> None:
    current_user = build_current_user()
    planning_cycle_service = AsyncMock()

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/planning-cycles",
                json={
                    "name": "FY2027 Budget",
                    "planning_type": "budget",
                    "fiscal_year": 2027,
                    "start_date": "2027-01-01",
                    "end_date": "2027-12-31",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json() == {"detail": "Permission 'budget.write' is required."}


def test_budget_manage_permission_is_required() -> None:
    current_user = build_current_user()
    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()

    planning_cycle_id = uuid4()
    scenario_id = uuid4()

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/planning-cycles/{planning_cycle_id}/scenarios/{scenario_id}/set-default"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json() == {"detail": "Permission 'budget.manage' is required."}
