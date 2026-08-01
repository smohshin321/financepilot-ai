from app.modules.identity.models import (
    MembershipRole,
    Permission,
    Role,
    RolePermission,
)
from sqlalchemy import Boolean, ForeignKeyConstraint


def test_role_has_expected_columns() -> None:
    table = Role.__table__

    assert set(table.c.keys()) == {
        "id",
        "organization_id",
        "code",
        "name",
        "description",
        "is_system",
        "is_active",
        "created_at",
        "updated_at",
    }


def test_role_required_columns_are_not_nullable() -> None:
    table = Role.__table__

    for column_name in (
        "organization_id",
        "code",
        "name",
        "is_system",
        "is_active",
    ):
        assert table.c[column_name].nullable is False

    assert table.c.description.nullable is True


def test_role_boolean_defaults() -> None:
    table = Role.__table__

    assert isinstance(table.c.is_system.type, Boolean)
    assert isinstance(table.c.is_active.type, Boolean)

    assert str(table.c.is_system.server_default.arg) == "false"
    assert str(table.c.is_active.server_default.arg) == "true"


def test_role_organization_foreign_key() -> None:
    foreign_keys = {
        foreign_key.target_fullname
        for constraint in Role.__table__.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        for foreign_key in constraint.elements
    }

    assert foreign_keys == {"organizations.id"}


def test_role_has_organization_scoped_unique_index() -> None:
    role_index = next(
        index for index in Role.__table__.indexes if index.name == "ix_roles_organization_code"
    )

    assert role_index.unique is True
    assert tuple(column.name for column in role_index.columns) == (
        "organization_id",
        "code",
    )


def test_permission_has_expected_columns() -> None:
    table = Permission.__table__

    assert set(table.c.keys()) == {
        "id",
        "code",
        "name",
        "description",
        "created_at",
        "updated_at",
    }


def test_permission_code_is_globally_unique() -> None:
    permission_index = next(
        index for index in Permission.__table__.indexes if index.name == "ix_permissions_code"
    )

    assert permission_index.unique is True
    assert tuple(column.name for column in permission_index.columns) == ("code",)


def test_membership_role_foreign_keys() -> None:
    foreign_keys = {
        foreign_key.target_fullname
        for constraint in MembershipRole.__table__.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        for foreign_key in constraint.elements
    }

    assert foreign_keys == {
        "memberships.id",
        "roles.id",
    }


def test_membership_role_unique_index() -> None:
    assignment_index = next(
        index
        for index in MembershipRole.__table__.indexes
        if index.name == "ix_membership_roles_membership_role"
    )

    assert assignment_index.unique is True
    assert tuple(column.name for column in assignment_index.columns) == (
        "membership_id",
        "role_id",
    )


def test_role_permission_foreign_keys() -> None:
    foreign_keys = {
        foreign_key.target_fullname
        for constraint in RolePermission.__table__.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        for foreign_key in constraint.elements
    }

    assert foreign_keys == {
        "roles.id",
        "permissions.id",
    }


def test_role_permission_unique_index() -> None:
    permission_index = next(
        index
        for index in RolePermission.__table__.indexes
        if index.name == "ix_role_permissions_role_permission"
    )

    assert permission_index.unique is True
    assert tuple(column.name for column in permission_index.columns) == (
        "role_id",
        "permission_id",
    )


def test_rbac_relationships_are_bidirectional() -> None:
    assert Role.__mapper__.relationships["organization"].back_populates == "roles"
    assert Role.__mapper__.relationships["membership_roles"].back_populates == "role"
    assert Role.__mapper__.relationships["role_permissions"].back_populates == "role"

    assert Permission.__mapper__.relationships["role_permissions"].back_populates == "permission"

    assert (
        MembershipRole.__mapper__.relationships["membership"].back_populates == "membership_roles"
    )
    assert MembershipRole.__mapper__.relationships["role"].back_populates == "membership_roles"

    assert RolePermission.__mapper__.relationships["role"].back_populates == "role_permissions"
    assert (
        RolePermission.__mapper__.relationships["permission"].back_populates == "role_permissions"
    )
