from app.modules.identity.models import Membership
from sqlalchemy import Boolean, DateTime, ForeignKeyConstraint, Index


def test_membership_table_name() -> None:
    assert Membership.__tablename__ == "memberships"


def test_membership_has_expected_columns() -> None:
    table = Membership.__table__

    assert set(table.c.keys()) == {
        "id",
        "user_id",
        "organization_id",
        "is_active",
        "joined_at",
        "created_at",
        "updated_at",
    }


def test_membership_required_columns_are_not_nullable() -> None:
    table = Membership.__table__

    required_columns = (
        "user_id",
        "organization_id",
        "is_active",
        "joined_at",
    )

    for column_name in required_columns:
        assert table.c[column_name].nullable is False


def test_membership_boolean_column() -> None:
    is_active_type = Membership.__table__.c.is_active.type

    assert isinstance(is_active_type, Boolean)


def test_membership_is_active_default() -> None:
    is_active = Membership.__table__.c.is_active

    assert is_active.server_default is not None
    assert str(is_active.server_default.arg) == "true"


def test_membership_joined_at_is_timezone_aware() -> None:
    joined_at_type = Membership.__table__.c.joined_at.type

    assert isinstance(joined_at_type, DateTime)
    assert joined_at_type.timezone is True


def test_membership_foreign_keys() -> None:
    table = Membership.__table__

    foreign_keys = {
        foreign_key.target_fullname
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        for foreign_key in constraint.elements
    }

    assert foreign_keys == {
        "users.id",
        "organizations.id",
    }


def test_membership_foreign_keys_use_cascade_delete() -> None:
    table = Membership.__table__

    ondelete_actions = {
        foreign_key.ondelete
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        for foreign_key in constraint.elements
    }

    assert ondelete_actions == {"CASCADE"}


def test_membership_unique_composite_index() -> None:
    indexes = [index for index in Membership.__table__.indexes if isinstance(index, Index)]

    membership_index = next(
        index for index in indexes if index.name == "ix_memberships_user_organization"
    )

    assert membership_index.unique is True
    assert tuple(column.name for column in membership_index.columns) == (
        "user_id",
        "organization_id",
    )


def test_membership_relationships() -> None:
    relationships = Membership.__mapper__.relationships

    assert "user" in relationships
    assert "organization" in relationships

    assert relationships["user"].back_populates == "memberships"
    assert relationships["organization"].back_populates == "memberships"

    assert relationships["user"].lazy == "selectin"
    assert relationships["organization"].lazy == "selectin"
