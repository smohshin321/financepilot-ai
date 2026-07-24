# FinancePilot AI Backend — Sprint Pack 2

Production-oriented FastAPI foundation with PostgreSQL persistence infrastructure.

## Capabilities

- FastAPI application factory and structured JSON logs
- Typed environment configuration through Pydantic Settings
- SQLAlchemy 2 asynchronous engine and session factory
- PostgreSQL through Psycopg 3
- Alembic migration baseline with deterministic constraint naming
- Liveness and database-aware readiness endpoints
- Docker Compose orchestration for PostgreSQL, migrations, and API
- Unit tests plus an opt-in PostgreSQL integration test

## Local setup

```bash
copy .env.example .env
python -m venv .venv
.venv\Scripts\activate
pip install uv
uv pip install -e ".[dev]"
```

Start only PostgreSQL:

```bash
docker compose up -d postgres
alembic upgrade head
python -m uvicorn app.main:app --reload --reload-dir app
```

Run unit tests without PostgreSQL:

```bash
pytest -m "not integration"
```

Run all tests after PostgreSQL is available:

```bash
pytest
```

Run the complete stack:

```bash
docker compose up --build
```

## Endpoints

- `GET /health` — liveness; confirms the process is running
- `GET /health/ready` — readiness; confirms PostgreSQL is reachable
- `GET /api/v1/health`
- `GET /api/v1/health/ready`
- `GET /docs`

## Migration commands

```bash
alembic upgrade head
alembic current
alembic history
alembic downgrade -1
alembic revision --autogenerate -m "describe change"
```

The first migration is intentionally a no-op platform baseline. Business tables will be introduced only when their domain modules are implemented.
