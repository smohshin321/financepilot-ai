from app.modules.planning.models import BudgetLine, BudgetVersion
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index, Numeric


def test_budget_line_table_name() -> None:
    assert BudgetLine.__tablename__ == "budget_lines"


def test_budget_line_has_expected_columns() -> None:
    table = BudgetLine.__table__

    assert set(table.c.keys()) == {
        "id",
        "budget_version_id",
        "account_id",
        "department_id",
        "cost_center_id",
        "period",
        "amount",
        "currency",
        "notes",
        "created_at",
        "updated_at",
    }


def test_budget_line_required_columns_are_not_nullable() -> None:
    table = BudgetLine.__table__

    required_columns = (
        "budget_version_id",
        "period",
        "amount",
        "currency",
    )

    for column_name in required_columns:
        assert table.c[column_name].nullable is False

    nullable_columns = (
        "account_id",
        "department_id",
        "cost_center_id",
        "notes",
    )

    for column_name in nullable_columns:
        assert table.c[column_name].nullable is True


def test_budget_line_amount_configuration() -> None:
    amount_column = BudgetLine.__table__.c.amount

    assert isinstance(amount_column.type, Numeric)
    assert amount_column.type.precision == 20
    assert amount_column.type.scale == 4
    assert str(amount_column.server_default.arg) == "0"


def test_budget_line_currency_length() -> None:
    currency_type = BudgetLine.__table__.c.currency.type

    assert currency_type.length == 3


def test_budget_line_budget_version_foreign_key() -> None:
    table = BudgetLine.__table__

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

    assert foreign_keys == {"budget_versions.id"}
    assert ondelete_actions == {"CASCADE"}


def test_budget_line_period_constraint() -> None:
    constraints = {
        constraint.name: str(constraint.sqltext)
        for constraint in BudgetLine.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    constraint_name = "ck_budget_lines_period_range"

    assert constraint_name in constraints
    assert "period BETWEEN 1 AND 12" in constraints[constraint_name]


def test_budget_line_indexes() -> None:
    indexes = {
        index.name: index for index in BudgetLine.__table__.indexes if isinstance(index, Index)
    }

    period_index = indexes["ix_budget_lines_version_period"]
    dimensions_index = indexes["ix_budget_lines_version_dimensions"]

    assert period_index.unique is False
    assert tuple(column.name for column in period_index.columns) == (
        "budget_version_id",
        "period",
    )

    assert dimensions_index.unique is False
    assert tuple(column.name for column in dimensions_index.columns) == (
        "budget_version_id",
        "account_id",
        "department_id",
        "cost_center_id",
    )


def test_budget_line_dimension_columns_do_not_have_foreign_keys_yet() -> None:
    table = BudgetLine.__table__

    assert not table.c.account_id.foreign_keys
    assert not table.c.department_id.foreign_keys
    assert not table.c.cost_center_id.foreign_keys


def test_budget_line_relationships_are_bidirectional() -> None:
    line_relationship = BudgetLine.__mapper__.relationships["budget_version"]
    version_relationship = BudgetVersion.__mapper__.relationships["budget_lines"]

    assert line_relationship.back_populates == "budget_lines"
    assert line_relationship.lazy == "selectin"

    assert version_relationship.back_populates == "budget_version"
    assert version_relationship.lazy == "selectin"
    assert "delete-orphan" in version_relationship.cascade
