from datetime import date
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.main import app
from app.modules.identity.api.dependencies import get_current_user_context
from app.modules.identity.schemas import CurrentUserContext
from app.modules.planning.api.authorization import (
    require_budget_manage,
    require_budget_read,
    require_budget_write,
)
from app.modules.planning.api.dependencies import get_planning_cycle_service
from app.modules.planning.exceptions import PlanningCycleNotFoundError
from app.modules.planning.models import PlanningCycle, PlanningStatus, PlanningType
from fastapi.testclient import TestClient


def build_current_user() -> CurrentUserContext:
    return CurrentUserContext(
        user_id=uuid4(),
        membership_id=uuid4(),
        organization_id=uuid4(),
        role_ids=[],
    )


def build_planning_cycle(
    organization_id,
) -> Mock:
    planning_cycle = Mock(spec=PlanningCycle)

    planning_cycle.id = uuid4()
    planning_cycle.organization_id = organization_id
    planning_cycle.name = "FY2027 Budget"
    planning_cycle.description = "Annual operating plan"
    planning_cycle.planning_type = PlanningType.BUDGET
    planning_cycle.fiscal_year = 2027
    planning_cycle.start_date = date(2027, 1, 1)
    planning_cycle.end_date = date(2027, 12, 31)
    planning_cycle.status = PlanningStatus.DRAFT
    planning_cycle.is_active = True

    return planning_cycle


def test_create_planning_cycle_uses_authenticated_organization() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    service = AsyncMock()

    service.create.return_value = planning_cycle

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/planning-cycles",
                json={
                    "name": "FY2027 Budget",
                    "description": "Annual operating plan",
                    "planning_type": "budget",
                    "fiscal_year": 2027,
                    "start_date": "2027-01-01",
                    "end_date": "2027-12-31",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["organization_id"] == str(current_user.organization_id)

    service.create.assert_awaited_once_with(
        organization_id=current_user.organization_id,
        name="FY2027 Budget",
        description="Annual operating plan",
        planning_type=PlanningType.BUDGET,
        fiscal_year=2027,
        start_date=date(2027, 1, 1),
        end_date=date(2027, 12, 31),
    )


def test_list_planning_cycles_uses_authenticated_organization() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    service = AsyncMock()

    service.list_for_organization.return_value = [planning_cycle]

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/planning-cycles")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == str(planning_cycle.id)

    service.list_for_organization.assert_awaited_once_with(current_user.organization_id)


def test_get_planning_cycle_uses_authenticated_organization() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    service = AsyncMock()

    service.get.return_value = planning_cycle

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.get(f"/api/v1/planning-cycles/{planning_cycle.id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == str(planning_cycle.id)

    service.get.assert_awaited_once_with(
        planning_cycle_id=planning_cycle.id,
        organization_id=current_user.organization_id,
    )


def test_get_planning_cycle_returns_404_when_not_found() -> None:
    current_user = build_current_user()
    service = AsyncMock()
    planning_cycle_id = uuid4()

    service.get.side_effect = PlanningCycleNotFoundError(planning_cycle_id)

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.get(f"/api/v1/planning-cycles/{planning_cycle_id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Planning cycle not found."}


def test_create_planning_cycle_rejects_invalid_payload() -> None:
    current_user = build_current_user()
    service = AsyncMock()

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/planning-cycles",
                json={
                    "name": "",
                    "planning_type": "budget",
                    "fiscal_year": 1999,
                    "start_date": "2027-01-01",
                    "end_date": "2027-12-31",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    service.create.assert_not_awaited()
