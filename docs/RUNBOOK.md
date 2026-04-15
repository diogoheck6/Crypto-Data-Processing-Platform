# Runbook — Crypto Data Processing Platform

> Operational reference for running, testing, migrating, and debugging the system locally.
> Read this when you need to know _how_ to do something, not _why_ it was designed that way.
> For the why, see [ARCHITECTURE.md](./ARCHITECTURE.md) and [ADR/](./ADR/).

---

## Prerequisites

| Tool           | Version                       | Check                    |
| -------------- | ----------------------------- | ------------------------ |
| Docker         | ≥ 24                          | `docker --version`       |
| Docker Compose | ≥ 2.20                        | `docker compose version` |
| Make           | any                           | `make --version`         |
| Python         | 3.12 (for local tooling only) | `python --version`       |

> All application code runs inside Docker containers. Python is only needed locally for pre-commit hooks and IDE tooling.

---

## Starting and Stopping the Stack

### Start everything

```bash
make up
# or explicitly:
docker compose up --build
```

Services started:

- `api` — FastAPI app on `http://localhost:8000`
- `db` — PostgreSQL 16 on `localhost:5432`

### Start in background

```bash
docker compose up -d
```

### Stop all services

```bash
make down
# or:
docker compose down
```

### Stop and remove volumes (full reset)

```bash
docker compose down -v
```

> ⚠️ This deletes all database data. Use it to reset to a clean state.

### View logs

```bash
# All services
docker compose logs -f

# API only
docker compose logs -f api

# Database only
docker compose logs -f db
```

### Rebuild after code changes

```bash
docker compose up --build
```

---

## Environment Configuration

```bash
# Copy the example file
cp .env.example .env

# Edit if needed (defaults work for local development)
nano .env
```

The `.env` file is git-ignored and must never be committed. Required variables are documented in [`.env.example`](../.env.example).

---

## Database Migrations (Alembic)

### Apply all pending migrations

```bash
make migrate
# or:
docker compose exec api alembic upgrade head
```

### Check current migration state

```bash
docker compose exec api alembic current
```

### Generate a new migration after model changes

```bash
docker compose exec api alembic revision --autogenerate -m "describe your change"
```

> Always review the generated migration file before applying. Auto-generated migrations can miss complex changes.

### Revert the last migration

```bash
docker compose exec api alembic downgrade -1
```

### Revert all migrations (empty schema)

```bash
docker compose exec api alembic downgrade base
```

---

## Running Tests

### All tests

```bash
make test
```

This requires the test database to be running. If it is not:

```bash
docker compose -f docker-compose.test.yml up -d db_test
make test
```

### Unit tests only (no database required)

```bash
make test-unit
# or:
pytest tests/unit/ -v
```

Unit tests cover domain logic only — value objects, entities, and domain services. They run in seconds and require no external dependencies.

### Integration tests (requires test DB)

```bash
make test-integration
# or:
docker compose -f docker-compose.test.yml up -d db_test
pytest tests/integration/ tests/api/ -v
```

### With coverage report

```bash
pytest --cov=src --cov-report=term-missing
```

### Run a specific test file

```bash
pytest tests/unit/domain/test_cost_basis_calculator.py -v
```

### Run tests matching a name pattern

```bash
pytest -k "fifo" -v
```

---

## Running the API Manually

The API starts automatically with `make up`. If you need to restart only the API:

```bash
docker compose restart api
```

To run the API outside Docker (with a local Python environment):

```bash
pip install -e ".[dev]"
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## Running the Queue Worker (Phase 6+)

Once Redis and the async queue are implemented:

```bash
# Start the worker service
docker compose up worker

# Or run it directly
docker compose exec worker python -m rq worker --url $REDIS_URL
```

---

## Quick Demo with Sample Data

```bash
# 1. Start the stack
make up

# 2. Upload the sample CSV
curl -X POST http://localhost:8000/api/v1/imports/csv \
  -F "file=@data/sample/binance_spot_trades_valid.csv"
# → note the job_id in the response

# 3. Trigger FIFO processing
curl -X POST http://localhost:8000/api/v1/process/{job_id}

# 4. View the portfolio summary
curl http://localhost:8000/api/v1/portfolio/summary | python -m json.tool
```

---

## Common Issues

### `docker compose up` fails — port already in use

```
Error: port 5432 is already allocated
```

**Fix:** Another PostgreSQL instance is running locally. Stop it:

```bash
sudo systemctl stop postgresql    # Linux
brew services stop postgresql     # macOS
```

Or change the host port in `docker-compose.yml` (e.g., `"5433:5432"`).

---

### Migration fails — relation already exists

```
sqlalchemy.exc.ProgrammingError: relation "transactions" already exists
```

**Fix:** The database has a schema that conflicts with Alembic's state. Options:

```bash
# Option 1: Reset the database entirely
docker compose down -v && docker compose up -d db
make migrate

# Option 2: Mark the migration as applied without running it
docker compose exec api alembic stamp head
```

---

### `pytest` cannot find `src` module

```
ModuleNotFoundError: No module named 'src'
```

**Fix:** Install the project in editable mode:

```bash
pip install -e ".[dev]"
```

Or ensure `PYTHONPATH` includes the project root:

```bash
PYTHONPATH=. pytest tests/unit/
```

---

### API returns 500 on file upload

Check the API logs:

```bash
docker compose logs -f api
```

Common causes:

- Database not reachable (check `db` service is running)
- Migrations not applied (`make migrate`)
- File encoding issue (try saving the CSV as UTF-8)

---

### Pre-commit hook fails

```bash
# Run hooks manually to see full output
pre-commit run --all-files

# Auto-fix formatting issues
black src/ tests/
ruff check src/ tests/ --fix
```

---

## Makefile Reference

| Target                  | Description                                |
| ----------------------- | ------------------------------------------ |
| `make up`               | Build and start all Docker services        |
| `make down`             | Stop all services                          |
| `make test`             | Run the full test suite (requires test DB) |
| `make test-unit`        | Run unit tests only (no DB required)       |
| `make test-integration` | Run integration and API tests              |
| `make lint`             | Run all pre-commit hooks                   |
| `make format`           | Auto-format code with Black + Ruff         |
| `make migrate`          | Apply all pending Alembic migrations       |
| `make shell`            | Open a shell inside the API container      |
