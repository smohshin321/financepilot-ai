# Sprint Pack 2 Windows Runbook

## Upgrade the extracted Sprint Pack

This ZIP contains the complete repository through Sprint Pack 2. Extract it to a new folder rather than copying individual files into Sprint Pack 1.

## Local Python plus Docker PostgreSQL

From `financepilot-ai\backend` in Command Prompt:

```cmd
copy .env.example .env
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install uv
uv pip install -e ".[dev]"
docker compose up -d postgres
alembic upgrade head
pytest -m "not integration"
python -m uvicorn app.main:app --reload --reload-dir app
```

Open:

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/health/ready
- http://127.0.0.1:8000/docs

Run the PostgreSQL integration test:

```cmd
pytest -m integration
```

## Complete Docker stack

```cmd
copy .env.example .env
docker compose up --build
```

Verify:

```cmd
docker compose ps
docker compose logs migrations
docker compose exec postgres psql -U financepilot -d financepilot -c "select version_num from alembic_version;"
```

Stop while retaining database data:

```cmd
docker compose down
```

Stop and delete the local PostgreSQL volume:

```cmd
docker compose down -v
```
