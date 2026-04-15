.PHONY: up down test test-unit test-integration lint format migrate shell

## Start the full development stack (API + PostgreSQL)
up:
	docker compose up --build

## Stop all services
down:
	docker compose down

## Run the full test suite (unit + integration + API)
test:
	docker compose -f docker-compose.test.yml up -d db_test
	pytest tests/ -v

## Run unit tests only — no database required
test-unit:
	pytest tests/unit/ -v

## Run integration and API tests — requires test database
test-integration:
	docker compose -f docker-compose.test.yml up -d db_test
	pytest tests/integration/ tests/api/ -v

## Run all pre-commit hooks (lint + format + type check + security)
lint:
	pre-commit run --all-files

## Auto-format source code
format:
	black src/ tests/
	ruff check src/ tests/ --fix

## Apply all pending Alembic migrations
migrate:
	docker compose exec api alembic upgrade head

## Open a shell inside the running API container
shell:
	docker compose exec api bash
