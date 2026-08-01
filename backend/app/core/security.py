from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import Settings, get_settings

_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plaintext password using the recommended Argon2id settings."""

    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against its stored hash."""

    return _password_hash.verify(password, password_hash)


def create_access_token(
    *,
    user_id: UUID,
    organization_id: UUID,
    membership_id: UUID,
    role_ids: list[UUID],
    settings: Settings | None = None,
    now: datetime | None = None,
) -> str:
    """Create a signed JWT access token."""

    resolved_settings = settings or get_settings()
    issued_at = now or datetime.now(UTC)
    expires_at = issued_at + timedelta(minutes=resolved_settings.access_token_expire_minutes)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "org": str(organization_id),
        "membership_id": str(membership_id),
        "role_ids": [str(role_id) for role_id in role_ids],
        "type": "access",
        "iat": issued_at,
        "exp": expires_at,
        "jti": str(uuid4()),
    }

    return jwt.encode(
        payload,
        resolved_settings.jwt_secret_key.get_secret_value(),
        algorithm=resolved_settings.jwt_algorithm,
    )


def decode_access_token(
    token: str,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Decode and validate a JWT access token."""

    resolved_settings = settings or get_settings()

    payload = jwt.decode(
        token,
        resolved_settings.jwt_secret_key.get_secret_value(),
        algorithms=[resolved_settings.jwt_algorithm],
    )

    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Invalid token type")

    return payload
