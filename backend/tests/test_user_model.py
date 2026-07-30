from app.modules.identity.models import User
from app.shared.constants import (
    EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PASSWORD_HASH_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)
from sqlalchemy import Boolean, DateTime, Index, String, UniqueConstraint


def test_user_table_name() -> None:
    assert User.__tablename__ == "users"


def test_user_has_expected_columns() -> None:
    table = User.__table__

    assert set(table.c.keys()) == {
        "id",
        "email",
        "username",
        "first_name",
        "last_name",
        "hashed_password",
        "is_active",
        "is_superuser",
        "email_verified",
        "last_login_at",
        "created_at",
        "updated_at",
    }


def test_user_required_columns_are_not_nullable() -> None:
    table = User.__table__

    required_columns = (
        "email",
        "first_name",
        "last_name",
        "hashed_password",
        "is_active",
        "is_superuser",
        "email_verified",
    )

    for column_name in required_columns:
        assert table.c[column_name].nullable is False


def test_user_optional_columns_are_nullable() -> None:
    table = User.__table__

    assert table.c.username.nullable is True
    assert table.c.last_login_at.nullable is True


def test_user_email_and_username_are_unique() -> None:
    constraints = [
        constraint
        for constraint in User.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    constrained_columns = {
        tuple(column.name for column in constraint.columns) for constraint in constraints
    }

    assert ("email",) in constrained_columns
    assert ("username",) in constrained_columns


def test_user_email_is_indexed() -> None:
    indexes = [index for index in User.__table__.indexes if isinstance(index, Index)]

    assert any(index.name == "ix_users_email" for index in indexes)


def test_user_string_column_lengths() -> None:
    table = User.__table__

    assert isinstance(table.c.email.type, String)
    assert table.c.email.type.length == EMAIL_MAX_LENGTH

    assert isinstance(table.c.username.type, String)
    assert table.c.username.type.length == USERNAME_MAX_LENGTH

    assert isinstance(table.c.first_name.type, String)
    assert table.c.first_name.type.length == NAME_MAX_LENGTH

    assert isinstance(table.c.last_name.type, String)
    assert table.c.last_name.type.length == NAME_MAX_LENGTH

    assert isinstance(table.c.hashed_password.type, String)
    assert table.c.hashed_password.type.length == PASSWORD_HASH_MAX_LENGTH


def test_user_boolean_columns_use_boolean_type() -> None:
    table = User.__table__

    assert isinstance(table.c.is_active.type, Boolean)
    assert isinstance(table.c.is_superuser.type, Boolean)
    assert isinstance(table.c.email_verified.type, Boolean)


def test_user_boolean_server_defaults() -> None:
    table = User.__table__

    assert table.c.is_active.server_default is not None
    assert table.c.is_superuser.server_default is not None
    assert table.c.email_verified.server_default is not None

    assert str(table.c.is_active.server_default.arg) == "true"
    assert str(table.c.is_superuser.server_default.arg) == "false"
    assert str(table.c.email_verified.server_default.arg) == "false"


def test_user_last_login_uses_timezone_aware_datetime() -> None:
    last_login_type = User.__table__.c.last_login_at.type

    assert isinstance(last_login_type, DateTime)
    assert last_login_type.timezone is True
