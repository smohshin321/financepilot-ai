from app.modules.planning.models import (
    PlanningCycle,
    PlanningStatus,
    PlanningType,
)
from sqlalchemy import Boolean, CheckConstraint, Enum, ForeignKeyConstraint, Index


def test_planning_cycle_table_name() -> None:
    assert PlanningCycle.__tablename__ == "planning_cycles"


def test_planning_cycle_has_expected_columns() -> None:
    table = PlanningCycle.__table__

    assert set(table.c.keys()) == {
        "id",
        "organization_id",
        "name",
        "description",
        "planning_type",
        "fiscal_year",
        "start_date",
        "end_date",
        "status",
        "is_active",
        "created_at",
        "updated_at",
    }


def test_planning_cycle_required_columns_are_not_nullable() -> None:
    table = PlanningCycle.__table__

    required_columns = (
        "organization_id",
        "name",
        "planning_type",
        "fiscal_year",
        "start_date",
        "end_date",
        "status",
        "is_active",
    )

    for column_name in required_columns:
        assert table.c[column_name].nullable is False

    assert table.c.description.nullable is True


def test_planning_cycle_enum_columns() -> None:
    table = PlanningCycle.__table__

    assert isinstance(table.c.planning_type.type, Enum)
    assert isinstance(table.c.status.type, Enum)

    assert table.c.planning_type.type.enum_class is PlanningType
    assert table.c.status.type.enum_class is PlanningStatus


def test_planning_cycle_defaults() -> None:
    table = PlanningCycle.__table__

    assert str(table.c.status.server_default.arg) == PlanningStatus.DRAFT.value
    assert isinstance(table.c.is_active.type, Boolean)
    assert str(table.c.is_active.server_default.arg) == "true"


def test_planning_cycle_organization_foreign_key() -> None:
    table = PlanningCycle.__table__

    foreign_keys = {
        foreign_key.target_fullname
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        for foreign_key in constraint.elements
    }

    ondelete_actions = {
        foreign_key.ondelete
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        for foreign_key in constraint.elements
    }

    assert foreign_keys == {"organizations.id"}
    assert ondelete_actions == {"CASCADE"}


def test_planning_cycle_indexes() -> None:
    indexes = {
        index.name: index for index in PlanningCycle.__table__.indexes if isinstance(index, Index)
    }

    fiscal_year_index = indexes["ix_planning_cycles_organization_fiscal_year"]
    status_index = indexes["ix_planning_cycles_organization_status"]

    assert tuple(column.name for column in fiscal_year_index.columns) == (
        "organization_id",
        "fiscal_year",
    )
    assert fiscal_year_index.unique is False

    assert tuple(column.name for column in status_index.columns) == (
        "organization_id",
        "status",
    )
    assert status_index.unique is False


def test_planning_cycle_check_constraints() -> None:
    constraints = {
        constraint.name: str(constraint.sqltext)
        for constraint in PlanningCycle.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "ck_planning_cycles_fiscal_year_range" in constraints
    assert "ck_planning_cycles_valid_date_range" in constraints

    assert (
        "fiscal_year BETWEEN 2000 AND 2200" in constraints["ck_planning_cycles_fiscal_year_range"]
    )
    assert "end_date >= start_date" in constraints["ck_planning_cycles_valid_date_range"]


def test_planning_cycle_organization_relationship() -> None:
    relationship = PlanningCycle.__mapper__.relationships["organization"]

    assert relationship.lazy == "selectin"
