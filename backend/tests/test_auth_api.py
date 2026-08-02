from uuid import uuid4

import pytest
from app.main import app
from app.modules.identity.api.dependencies import (
    get_authentication_service,
)
from app.modules.identity.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    MembershipNotFoundError,
)
from app.modules.identity.schemas import AuthenticatedUserContext
from fastapi.testclient import TestClient


class StubAuthenticationService:
    """Controllable authentication service used by API tests."""

    exception: Exception | None = None

    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> AuthenticatedUserContext:
        if self.exception is not None:
            raise self.exception

        return AuthenticatedUserContext(
            user_id=uuid4(),
            membership_id=uuid4(),
            organization_id=uuid4(),
            email=email.strip().lower(),
            role_ids=[uuid4()],
            access_token="test-access-token",
        )


@pytest.fixture
def auth_service() -> StubAuthenticationService:
    return StubAuthenticationService()


@pytest.fixture
def client(
    auth_service: StubAuthenticationService,
) -> TestClient:
    app.dependency_overrides[get_authentication_service] = lambda: auth_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_login_returns_access_token(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "ANALYST@FINANCEPILOT.AI",
            "password": "SecurePassword123!",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["access_token"] == "test-access-token"
    assert body["token_type"] == "bearer"
    assert body["email"] == "analyst@financepilot.ai"
    assert len(body["role_ids"]) == 1


@pytest.mark.parametrize(
    ("exception", "expected_status"),
    [
        (InvalidCredentialsError(), 401),
        (InactiveUserError(), 403),
        (MembershipNotFoundError(), 403),
    ],
)
def test_login_maps_domain_errors(
    client: TestClient,
    auth_service: StubAuthenticationService,
    exception: Exception,
    expected_status: int,
) -> None:
    auth_service.exception = exception

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "analyst@financepilot.ai",
            "password": "SecurePassword123!",
        },
    )

    assert response.status_code == expected_status


def test_me_requires_bearer_token(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
