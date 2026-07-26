from app.modules.identity.models import Organization, OrganizationStatus
from sqlalchemy import CheckConstraint, Enum, Index, UniqueConstraint


def test_organization_table_name() -> None:
    assert Organization.__tablename__ == "organizations"


def test_organization_has_expected_columns() -> None:
    table = Organization.__table__

    assert set(table.c.keys()) == {
        "id",
        "code",
        "legal_name",
        "display_name",
        "base_currency",
        "timezone",
        "fiscal_year_start_month",
        "status",
        "created_at",
        "updated_at",
    }


def test_organization_status_values() -> None:
    assert OrganizationStatus.ACTIVE.value == "active"
    assert OrganizationStatus.INACTIVE.value == "inactive"
    assert OrganizationStatus.SUSPENDED.value == "suspended"


def test_organization_required_columns_are_not_nullable() -> None:
    table = Organization.__table__

    required_columns = (
        "code",
        "legal_name",
        "display_name",
        "base_currency",
        "timezone",
        "fiscal_year_start_month",
        "status",
    )

    for column_name in required_columns:
        assert table.c[column_name].nullable is False


def test_organization_has_fiscal_month_check_constraint() -> None:
    constraints = [
        constraint
        for constraint in Organization.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    ]

    assert any(
        constraint.name == "ck_organizations_fiscal_year_start_month_range"
        for constraint in constraints
    )


def test_organization_status_is_indexed() -> None:
    indexes = [index for index in Organization.__table__.indexes if isinstance(index, Index)]

    assert any(index.name == "ix_organizations_status" for index in indexes)


def test_organization_status_uses_named_enum() -> None:
    status_type = Organization.__table__.c.status.type

    assert isinstance(status_type, Enum)
    assert status_type.name == "organization_status"


def test_organization_unique_constraints_exist() -> None:
    constraints = [
        constraint
        for constraint in Organization.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    constrained_columns = {
        tuple(column.name for column in constraint.columns) for constraint in constraints
    }

    assert ("code",) in constrained_columns
    assert ("legal_name",) in constrained_columns
