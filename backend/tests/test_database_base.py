from app.shared.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class ExampleEntity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Test-only model used to validate shared ORM behavior."""

    __tablename__ = "test_example_entities"

    name: Mapped[str] = mapped_column(String(100), nullable=False)


def test_base_uses_expected_naming_convention() -> None:
    convention = Base.metadata.naming_convention

    assert convention["pk"] == "pk_%(table_name)s"
    assert convention["fk"] == ("fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s")
    assert convention["uq"] == "uq_%(table_name)s_%(column_0_name)s"


def test_uuid_primary_key_column_has_default() -> None:
    id_column = ExampleEntity.__table__.c.id

    assert id_column.primary_key is True
    assert id_column.default is not None


def test_shared_columns_are_registered() -> None:
    table = ExampleEntity.__table__

    assert table.c.created_at.nullable is False
    assert table.c.created_at.server_default is not None
    assert table.c.updated_at.nullable is False
    assert table.c.updated_at.server_default is not None
    assert table.c.updated_at.onupdate is not None
