from app.modules.planning.models import BudgetVersion, Scenario
from sqlalchemy import Boolean, ForeignKeyConstraint, Index


def test_budget_version_table_name() -> None:
    assert BudgetVersion.__tablename__ == "budget_versions"


def test_budget_version_has_expected_columns() -> None:
    table = BudgetVersion.__table__

    assert set(table.c.keys()) == {
        "id",
        "scenario_id",
        "version_number",
        "version_name",
        "description",
        "is_active",
        "is_locked",
        "created_at",
        "updated_at",
    }


def test_budget_version_required_columns_are_not_nullable() -> None:
    table = BudgetVersion.__table__

    required_columns = (
        "scenario_id",
        "version_number",
        "version_name",
        "is_active",
        "is_locked",
    )

    for column_name in required_columns:
        assert table.c[column_name].nullable is False

    assert table.c.description.nullable is True


def test_budget_version_boolean_defaults() -> None:
    table = BudgetVersion.__table__

    assert isinstance(table.c.is_active.type, Boolean)
    assert isinstance(table.c.is_locked.type, Boolean)

    assert str(table.c.is_active.server_default.arg) == "true"
    assert str(table.c.is_locked.server_default.arg) == "false"


def test_budget_version_scenario_foreign_key() -> None:
    table = BudgetVersion.__table__

    foreign_keys = {
        fk.target_fullname
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        for fk in constraint.elements
    }

    ondelete_actions = {
        fk.ondelete
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        for fk in constraint.elements
    }

    assert foreign_keys == {"scenarios.id"}
    assert ondelete_actions == {"CASCADE"}


def test_budget_version_indexes() -> None:
    indexes = {
        index.name: index for index in BudgetVersion.__table__.indexes if isinstance(index, Index)
    }

    version_index = indexes["ix_budget_versions_scenario_number"]
    active_index = indexes["ix_budget_versions_scenario_active"]

    assert version_index.unique is True
    assert tuple(column.name for column in version_index.columns) == (
        "scenario_id",
        "version_number",
    )

    assert active_index.unique is False
    assert tuple(column.name for column in active_index.columns) == (
        "scenario_id",
        "is_active",
    )


def test_budget_version_relationships_are_bidirectional() -> None:
    version_relationship = BudgetVersion.__mapper__.relationships["scenario"]
    scenario_relationship = Scenario.__mapper__.relationships["budget_versions"]

    assert version_relationship.back_populates == "budget_versions"
    assert version_relationship.lazy == "selectin"

    assert scenario_relationship.back_populates == "scenario"
    assert scenario_relationship.lazy == "selectin"
    assert "delete-orphan" in scenario_relationship.cascade
