from decimal import Decimal
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
    get_budget_line_service,
    get_budget_version_service,
    get_planning_cycle_service,
    get_scenario_service,
)
from app.modules.planning.exceptions import (
    BudgetLineNotFoundError,
    BudgetVersionLockedError,
)
from app.modules.planning.models import (
    BudgetLine,
    BudgetVersion,
    PlanningCycle,
    Scenario,
)
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
    budget_version.is_locked = False
    return budget_version


def build_budget_line(budget_version_id) -> Mock:
    budget_line = Mock(spec=BudgetLine)
    budget_line.id = uuid4()
    budget_line.budget_version_id = budget_version_id
    budget_line.account_id = uuid4()
    budget_line.department_id = uuid4()
    budget_line.cost_center_id = uuid4()
    budget_line.period = 1
    budget_line.amount = Decimal("1000.0000")
    budget_line.currency = "CAD"
    budget_line.notes = "January budget"
    return budget_line


def apply_overrides(
    current_user,
    planning_cycle_service,
    scenario_service,
    budget_version_service,
    budget_line_service,
) -> None:
    app.dependency_overrides[get_current_user_context] = lambda: current_user
    app.dependency_overrides[get_planning_cycle_service] = lambda: planning_cycle_service
    app.dependency_overrides[get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[get_budget_version_service] = lambda: budget_version_service
    app.dependency_overrides[get_budget_line_service] = lambda: budget_line_service
    app.dependency_overrides[require_budget_read] = lambda: None
    app.dependency_overrides[require_budget_write] = lambda: None
    app.dependency_overrides[require_budget_manage] = lambda: None


def test_create_budget_line() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)
    budget_line = build_budget_line(budget_version.id)

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()
    budget_line_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.get.return_value = budget_version
    budget_line_service.create.return_value = budget_line

    apply_overrides(
        current_user,
        planning_cycle_service,
        scenario_service,
        budget_version_service,
        budget_line_service,
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}/budget-lines",
                json={
                    "account_id": str(budget_line.account_id),
                    "department_id": str(budget_line.department_id),
                    "cost_center_id": str(budget_line.cost_center_id),
                    "period": 1,
                    "amount": "1000.0000",
                    "currency": "cad",
                    "notes": "January budget",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["budget_version_id"] == str(budget_version.id)
    assert response.json()["currency"] == "CAD"

    budget_line_service.create.assert_awaited_once()


def test_list_budget_lines() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)

    lines = [
        build_budget_line(budget_version.id),
        build_budget_line(budget_version.id),
    ]

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()
    budget_line_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.get.return_value = budget_version
    budget_line_service.list_for_budget_version.return_value = lines

    apply_overrides(
        current_user,
        planning_cycle_service,
        scenario_service,
        budget_version_service,
        budget_line_service,
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}/budget-lines"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 2

    budget_line_service.list_for_budget_version.assert_awaited_once_with(budget_version.id)


def test_get_budget_line() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)
    budget_line = build_budget_line(budget_version.id)

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()
    budget_line_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.get.return_value = budget_version
    budget_line_service.get.return_value = budget_line

    apply_overrides(
        current_user,
        planning_cycle_service,
        scenario_service,
        budget_version_service,
        budget_line_service,
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}"
                f"/budget-lines/{budget_line.id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == str(budget_line.id)

    budget_line_service.get.assert_awaited_once_with(
        budget_line_id=budget_line.id,
        budget_version_id=budget_version.id,
    )


def test_get_budget_line_returns_404_when_not_found() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)
    budget_line_id = uuid4()

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()
    budget_line_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.get.return_value = budget_version
    budget_line_service.get.side_effect = BudgetLineNotFoundError(budget_line_id)

    apply_overrides(
        current_user,
        planning_cycle_service,
        scenario_service,
        budget_version_service,
        budget_line_service,
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}"
                f"/budget-lines/{budget_line_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Budget line not found."}


def test_update_budget_line() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)
    budget_line = build_budget_line(budget_version.id)

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()
    budget_line_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.get.return_value = budget_version
    budget_version_service.validate_editable = Mock()
    budget_line_service.get.return_value = budget_line
    budget_line_service.update.return_value = budget_line

    apply_overrides(
        current_user,
        planning_cycle_service,
        scenario_service,
        budget_version_service,
        budget_line_service,
    )

    try:
        with TestClient(app) as client:
            response = client.put(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}"
                f"/budget-lines/{budget_line.id}",
                json={
                    "account_id": str(budget_line.account_id),
                    "department_id": str(budget_line.department_id),
                    "cost_center_id": str(budget_line.cost_center_id),
                    "period": 2,
                    "amount": "1500.0000",
                    "currency": "usd",
                    "notes": "Updated budget",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    budget_line_service.update.assert_awaited_once_with(budget_line)


def test_update_budget_line_returns_404_when_not_found() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)
    budget_line_id = uuid4()

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()
    budget_line_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.get.return_value = budget_version
    budget_version_service.validate_editable = Mock()
    budget_line_service.get.side_effect = BudgetLineNotFoundError(budget_line_id)

    apply_overrides(
        current_user,
        planning_cycle_service,
        scenario_service,
        budget_version_service,
        budget_line_service,
    )

    try:
        with TestClient(app) as client:
            response = client.put(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}"
                f"/budget-lines/{budget_line_id}",
                json={
                    "period": 2,
                    "amount": "1500.0000",
                    "currency": "CAD",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Budget line not found."}


def test_update_budget_line_returns_409_when_version_locked() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)
    budget_version.is_locked = True
    budget_line = build_budget_line(budget_version.id)

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()
    budget_line_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.get.return_value = budget_version

    budget_version_service.validate_editable = Mock(
        side_effect=BudgetVersionLockedError(budget_version.id)
    )

    apply_overrides(
        current_user,
        planning_cycle_service,
        scenario_service,
        budget_version_service,
        budget_line_service,
    )

    try:
        with TestClient(app) as client:
            response = client.put(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}"
                f"/budget-lines/{budget_line.id}",
                json={
                    "period": 2,
                    "amount": "1500.0000",
                    "currency": "CAD",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {"detail": "Budget version is locked."}

    budget_line_service.update.assert_not_awaited()


def test_delete_budget_line() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)
    budget_line = build_budget_line(budget_version.id)

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()
    budget_line_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.get.return_value = budget_version
    budget_version_service.validate_editable = Mock()

    apply_overrides(
        current_user,
        planning_cycle_service,
        scenario_service,
        budget_version_service,
        budget_line_service,
    )

    try:
        with TestClient(app) as client:
            response = client.delete(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}"
                f"/budget-lines/{budget_line.id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 204

    budget_line_service.delete.assert_awaited_once_with(
        budget_line_id=budget_line.id,
        budget_version_id=budget_version.id,
    )


def test_delete_budget_line_returns_404_when_not_found() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)
    budget_line_id = uuid4()

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()
    budget_line_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.get.return_value = budget_version
    budget_version_service.validate_editable = Mock()
    budget_line_service.delete.side_effect = BudgetLineNotFoundError(budget_line_id)

    apply_overrides(
        current_user,
        planning_cycle_service,
        scenario_service,
        budget_version_service,
        budget_line_service,
    )

    try:
        with TestClient(app) as client:
            response = client.delete(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}"
                f"/budget-lines/{budget_line_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Budget line not found."}


def test_delete_budget_line_returns_409_when_version_locked() -> None:
    current_user = build_current_user()
    planning_cycle = build_planning_cycle(current_user.organization_id)
    scenario = build_scenario(planning_cycle.id)
    budget_version = build_budget_version(scenario.id)
    budget_version.is_locked = True
    budget_line = build_budget_line(budget_version.id)

    planning_cycle_service = AsyncMock()
    scenario_service = AsyncMock()
    budget_version_service = AsyncMock()
    budget_line_service = AsyncMock()

    planning_cycle_service.get.return_value = planning_cycle
    scenario_service.get.return_value = scenario
    budget_version_service.get.return_value = budget_version

    budget_version_service.validate_editable = Mock(
        side_effect=BudgetVersionLockedError(budget_version.id)
    )

    apply_overrides(
        current_user,
        planning_cycle_service,
        scenario_service,
        budget_version_service,
        budget_line_service,
    )

    try:
        with TestClient(app) as client:
            response = client.delete(
                f"/api/v1/planning-cycles/{planning_cycle.id}"
                f"/scenarios/{scenario.id}"
                f"/budget-versions/{budget_version.id}"
                f"/budget-lines/{budget_line.id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {"detail": "Budget version is locked."}

    budget_line_service.delete.assert_not_awaited()
