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
    get_budget_version_service,
    get_planning_cycle_service,
    get_scenario_service,
)
from app.modules.planning.exceptions import BudgetVersionNotFoundError
from app.modules.planning.models import BudgetVersion, PlanningCycle, Scenario
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
    return scenario


def build_budget_version(scenario_id) -> Mock:
    budget_version = Mock(spec=BudgetVersion)
    budget_version.id = uuid4()
    budget_version.scenario_id = scenario_id
    budget_version.version_number = 1
    budget_version.version_name = "Working Budget"
    budget_version.description = "Initial working version"
    budget_version.is_active = True
    budget_version.is_locked = False
    return budget_version


def test_create_budget_version() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.create.return_value = budget_version

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[get_budget_version_service] = lambda: budget_version_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}/budget-versions",
                json={
                    "version_number": 1,
                    "version_name": "Working Budget",
                    "description": "Initial working version",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["scenario_id"] == str(scenario.id)
    assert response.json()["version_number"] == 1
    assert response.json()["is_locked"] is False

    budget_version_service.create.assert_awaited_once()


def test_get_budget_version() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.get.return_value = budget_version

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[get_budget_version_service] = lambda: budget_version_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == str(budget_version.id)

    budget_version_service.get.assert_awaited_once_with(
        budget_version_id=budget_version.id,
        scenario_id=scenario.id,
    )


def test_get_budget_version_returns_404_when_not_found() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version_id = uuid4()

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.get.side_effect = BudgetVersionNotFoundError(budget_version_id)

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[get_budget_version_service] = lambda: budget_version_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Budget version not found."}


def test_list_budget_versions() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)

    versions = [
        build_budget_version(scenario.id),
        build_budget_version(scenario.id),
    ]

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.list_for_scenario.return_value = versions

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[get_budget_version_service] = lambda: budget_version_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}/budget-versions"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 2

    budget_version_service.list_for_scenario.assert_awaited_once_with(scenario.id)


def test_activate_budget_version() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.activate.return_value = budget_version

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[get_budget_version_service] = lambda: budget_version_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}/activate"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    budget_version_service.activate.assert_awaited_once_with(
        budget_version_id=budget_version.id,
        scenario_id=scenario.id,
    )


def test_lock_budget_version() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)
    budget_version.is_locked = True

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.lock.return_value = budget_version

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[get_budget_version_service] = lambda: budget_version_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}/lock"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["is_locked"] is True

    budget_version_service.lock.assert_awaited_once_with(
        budget_version_id=budget_version.id,
        scenario_id=scenario.id,
    )


def test_activate_budget_version_returns_404_when_not_found() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version_id = uuid4()

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.activate.side_effect = BudgetVersionNotFoundError(budget_version_id)

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[get_budget_version_service] = lambda: budget_version_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version_id}/activate"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Budget version not found."}


def test_lock_budget_version_returns_404_when_not_found() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version_id = uuid4()

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.lock.side_effect = BudgetVersionNotFoundError(budget_version_id)

    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[get_budget_version_service] = lambda: budget_version_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version_id}/lock"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Budget version not found."}
