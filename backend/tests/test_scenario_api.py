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
from app.modules.planning.api.dependencies import (
    get_planning_cycle_service,
    get_scenario_service,
)
from app.modules.planning.exceptions import PlanningCycleNotFoundError
from app.modules.planning.models import PlanningCycle, Scenario
from fastapi.testclient import TestClient


def build_current_user() -> CurrentUserContext:
    return CurrentUserContext(
        user_id=uuid4(),
        membership_id=uuid4(),
        organization_id=uuid4(),
        role_ids=[],
    )


def build_planning_cycle(organization_id) -> Mock:
    planning_cycle = Mock(spec=PlanningCycle)
    planning_cycle.id = uuid4()
    planning_cycle.organization_id = organization_id
    return planning_cycle


def build_scenario(planning_cycle_id) -> Mock:
    scenario = Mock(spec=Scenario)
    scenario.id = uuid4()
    scenario.planning_cycle_id = planning_cycle_id
    scenario.code = "BASE"
    scenario.name = "Base Case"
    scenario.description = "Management base-case assumptions"
    scenario.is_default = True
    scenario.is_active = True
    return scenario


def test_create_scenario_uses_authenticated_organization_scope() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.create.return_value = scenario

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/planning-cycles/{planning_cycle.id}/scenarios",
                json={
                    "code": "BASE",
                    "name": "Base Case",
                    "description": "Management base-case assumptions",
                    "is_default": True,
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["planning_cycle_id"] == str(planning_cycle.id)
    assert response.json()["code"] == "BASE"

    planning_cycle_service.get.assert_awaited_once_with(
        planning_cycle_id=planning_cycle.id,
        organization_id=current_user.organization_id,
    )

    scenario_service.create.assert_awaited_once()


def test_create_scenario_returns_404_when_planning_cycle_not_found() -> None:
    current_user = build_current_user()
    planning_cycle_id = uuid4()

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()

    planning_cycle_service.get.side_effect = PlanningCycleNotFoundError(planning_cycle_id)

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/planning-cycles/{planning_cycle_id}/scenarios",
                json={
                    "code": "BASE",
                    "name": "Base Case",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Planning cycle not found."}

    scenario_service.create.assert_not_awaited()


def test_list_scenarios_returns_scenarios_for_planning_cycle() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)

    scenarios = [
        build_scenario(planning_cycle.id),
        build_scenario(planning_cycle.id),
    ]

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.list_for_planning_cycle.return_value = scenarios

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.get(f"/api/v1/planning-cycles/{planning_cycle.id}/scenarios")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 2

    planning_cycle_service.get.assert_awaited_once_with(
        planning_cycle_id=planning_cycle.id,
        organization_id=current_user.organization_id,
    )

    scenario_service.list_for_planning_cycle.assert_awaited_once_with(planning_cycle.id)


def test_get_scenario_returns_scenario() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None
    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/planning-cycles/{planning_cycle.id}/scenarios/{scenario.id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == str(scenario.id)

    scenario_service.get.assert_awaited_once_with(
        scenario_id=scenario.id,
        planning_cycle_id=planning_cycle.id,
    )


def test_get_scenario_returns_404_when_scenario_not_found() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario_id = uuid4()

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = None

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/planning-cycles/{planning_cycle.id}/scenarios/{scenario_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Scenario not found."}


def test_set_default_scenario_updates_default_scenario() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.set_default.return_value = scenario

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/planning-cycles/{planning_cycle.id}/scenarios/{scenario.id}/set-default"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["is_default"] is True

    scenario_service.set_default.assert_awaited_once_with(
        scenario_id=scenario.id,
        planning_cycle_id=planning_cycle.id,
    )


def test_set_default_scenario_returns_404_when_scenario_not_found() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario_id = uuid4()

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.set_default.return_value = None

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/planning-cycles/{planning_cycle.id}/scenarios/{scenario_id}/set-default"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Scenario not found."}
