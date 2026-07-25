from app.core.config import Settings


def test_database_urls_are_derived_from_typed_settings() -> None:
    settings = Settings(
        postgres_host="db.internal",
        postgres_port=5433,
        postgres_db="financepilot_test",
        postgres_user="finance_user",
        postgres_password="p@ss word",
    )
    expected = "postgresql+psycopg://finance_user:p%40ss+word@db.internal:5433/financepilot_test"
    assert settings.database_url == expected
    assert settings.alembic_database_url == expected
