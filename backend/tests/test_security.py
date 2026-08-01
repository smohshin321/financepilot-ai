from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_is_not_plaintext() -> None:
    password = "FinancePilot2026!"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)


def test_password_verification_fails_for_wrong_password() -> None:
    password_hash = hash_password("FinancePilot2026!")

    assert verify_password("WrongPassword", password_hash) is False


def test_create_and_decode_access_token() -> None:
    user_id = uuid4()
    organization_id = uuid4()
    membership_id = uuid4()
    role_ids = [uuid4(), uuid4()]

    token = create_access_token(
        user_id=user_id,
        organization_id=organization_id,
        membership_id=membership_id,
        role_ids=role_ids,
    )

    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["org"] == str(organization_id)
    assert payload["membership_id"] == str(membership_id)
    assert payload["role_ids"] == [str(role) for role in role_ids]
    assert payload["type"] == "access"

    assert "iat" in payload
    assert "exp" in payload
    assert "jti" in payload


def test_invalid_signature_raises_exception() -> None:
    token = create_access_token(
        user_id=uuid4(),
        organization_id=uuid4(),
        membership_id=uuid4(),
        role_ids=[],
    )

    tampered = token[:-5] + "abcde"

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(tampered)


def test_wrong_token_type_is_rejected() -> None:
    settings = get_settings()

    payload = {
        "sub": str(uuid4()),
        "type": "refresh",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(minutes=30),
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)
