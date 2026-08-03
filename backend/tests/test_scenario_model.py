from app.modules.planning.models import PlanningCycle, Scenario
from sqlalchemy import Boolean, ForeignKeyConstraint, Index


def test_scenario_table_name() -> None:
    assert Scenario.__tablename__ == "scenarios"


def test_scenario_has_expected_columns() -> None:
    table = Scenario.__table__

    assert set(table.c.keys()) == {
        "id",
        "planning_cycle_id",
        "code",
        "name",
        "description",
        "is_default",
        "is_active",
        "created_at",
        "updated_at",
    }


def test_scenario_required_columns_are_not_nullable() -> None:
    table = Scenario.__table__

    required_columns = (
        "planning_cycle_id",
        "code",
        "name",
        "is_default",
        "is_active",
    )

    for column_name in required_columns:
        assert table.c[column_name].nullable is False

    assert table.c.description.nullable is True


def test_scenario_boolean_defaults() -> None:
    table = Scenario.__table__

    assert isinstance(table.c.is_default.type, Boolean)
    assert isinstance(table.c.is_active.type, Boolean)

    assert str(table.c.is_default.server_default.arg) == "false"
    assert str(table.c.is_active.server_default.arg) == "true"


def test_scenario_planning_cycle_foreign_key() -> None:
    table = Scenario.__table__

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

    assert foreign_keys == {"planning_cycles.id"}
    assert ondelete_actions == {"CASCADE"}


def test_scenario_indexes() -> None:
    indexes = {
        index.name: index for index in Scenario.__table__.indexes if isinstance(index, Index)
    }

    code_index = indexes["ix_scenarios_planning_cycle_code"]
    default_index = indexes["ix_scenarios_planning_cycle_default"]

    assert code_index.unique is True
    assert tuple(column.name for column in code_index.columns) == (
        "planning_cycle_id",
        "code",
    )

    assert default_index.unique is False
    assert tuple(column.name for column in default_index.columns) == (
        "planning_cycle_id",
        "is_default",
    )


def test_scenario_relationships_are_bidirectional() -> None:
    scenario_relationship = Scenario.__mapper__.relationships["planning_cycle"]
    cycle_relationship = PlanningCycle.__mapper__.relationships["scenarios"]

    assert scenario_relationship.back_populates == "scenarios"
    assert scenario_relationship.lazy == "selectin"

    assert cycle_relationship.back_populates == "planning_cycle"
    assert cycle_relationship.lazy == "selectin"
    assert "delete-orphan" in cycle_relationship.cascade
