# Backlog — Crypto Data Processing Platform

> Format: Epics → User Stories → Tasks → Acceptance Criteria
> Priority: 🔴 Critical (MVP) | 🟡 High | 🟢 Medium | ⚪ Low (future)

---

## Epic 1 — Project Foundation 🔴

**Goal:** A clean, runnable skeleton that every other epic builds on.

---

### Story 1.1 — Repository Structure

As a developer, I want a clean project scaffold so I can start writing domain code immediately without fighting folder structure.

**Tasks:**

- Create `src/` with `domain/`, `application/`, `infra/`, `api/` subdirectories
- Create `tests/` with `unit/`, `integration/`, `api/` subdirectories
- Add `__init__.py` files at all package levels

**Acceptance Criteria:**

- `src/` follows the layered structure from ARCHITECTURE.md exactly
- `python -c "from src.domain import *"` imports without error
- No circular imports

---

### Story 1.2 — Python Tooling

As a developer, I want linting, formatting and type-checking enforced automatically so code quality is consistent from day one.

**Tasks:**

- Create `pyproject.toml` with Ruff, Black, Mypy configured
- Create `.pre-commit-config.yaml`
- Run `pre-commit install`

**Acceptance Criteria:**

- `pre-commit run --all-files` passes on the initial scaffold
- Mypy reports no errors on an empty `src/`
- Running `ruff check src/` and `black --check src/` both return clean

---

### Story 1.3 — Docker Environment

As a developer, I want `docker compose up` to start the full stack so I never need to install PostgreSQL locally.

**Tasks:**

- Write `Dockerfile` for the API service
- Write `docker-compose.yml` with `api` + `db` services
- Write `docker-compose.test.yml` with isolated `db_test` service

**Acceptance Criteria:**

- `docker compose up` starts API on port 8000 and PostgreSQL on port 5432
- API returns `{"status": "ok"}` on `GET /health`
- `docker compose -f docker-compose.test.yml up -d db_test` starts a test DB on port 5433

---

### Story 1.4 — DevOps Foundations

As a developer, I want a `.gitignore`, `Makefile`, and basic security tooling in place from the first commit so that secrets are never leaked and common commands are standardized.

**Tasks:**

- Create `.gitignore` covering `.env`, caches, build artifacts
- Create `Makefile` with standardized developer targets
- Create `.github/dependabot.yml` targeting the `pip` ecosystem (weekly)
- Add `bandit` to `.pre-commit-config.yaml`

**Acceptance Criteria:**

- `.env` is never tracked by git
- `make test` runs the full test suite
- `make lint` runs all pre-commit hooks
- `make up` starts the full Docker stack

---

## Epic 2 — Domain Layer 🔴

**Goal:** All business rules implemented as pure Python, fully tested, with zero external dependencies.

> **Why tests matter here:** FIFO calculations involve financial arithmetic. A single incorrect rounding or wrong queue consumption can silently produce wrong P&L results. 100% test coverage of domain services is non-negotiable.

---

### Story 2.1 — Value Objects

As a developer, I want immutable value objects so that financial quantities and asset names cannot be mutated accidentally.

**Tasks:**

- Implement `Money`, `Quantity`, `AssetSymbol`, `TransactionType`, `CostBasisMethod`

**Acceptance Criteria:**

- All value objects are frozen dataclasses
- Invalid construction (negative money, empty symbol) raises `ValueError`
- `pytest tests/unit/domain/test_value_objects.py` passes with 100% branch coverage

---

### Story 2.2 — Entities

As a developer, I want domain entities that represent the core concepts of the system without any ORM or HTTP knowledge.

**Tasks:**

- Implement `Transaction`, `AssetPosition`, `ProcessingJob`, `ProcessingResult`

**Acceptance Criteria:**

- No import of SQLAlchemy, FastAPI, or Pydantic in any entity file
- Entities are plain Python dataclasses
- `Transaction` cannot be constructed with an invalid `TransactionType`

---

### Story 2.3 — Transaction Normalizer

As the system, I want to map raw dict rows from any parser into canonical `Transaction` objects so that all downstream logic works with a single model.

**Tasks:**

- Implement `TransactionNormalizer.normalize(raw: dict) -> Transaction`
- Map field name aliases (Binance CSV keys → internal field names)
- Raise `NormalizationError` on missing required fields

**Acceptance Criteria:**

- Valid dict → correct `Transaction` object
- Missing required field → `NormalizationError` with field name in message
- Unknown extra fields → silently ignored
- Date strings parsed correctly to `datetime` with timezone

**Tests (unit):**

- Valid dict → correct Transaction
- Missing `quantity` → NormalizationError
- Missing `occurred_at` → NormalizationError
- Extra unknown field → ignored
- Date in ISO format → parsed to UTC datetime
- Date in Binance format → parsed correctly

---

### Story 2.4 — Transaction Validator

As the system, I want to validate transactions against business rules so that invalid data is caught before it reaches the FIFO engine.

**Tasks:**

- Implement `TransactionValidator.validate(t: Transaction) -> list[ValidationError]`
- Rules: quantity > 0 for buy/sell, valid transaction type, required fields present, total_value ≈ quantity × unit_price

**Acceptance Criteria:**

- Valid transaction → empty error list
- Zero quantity → one ValidationError with code `ZERO_QUANTITY`
- Invalid type string → ValidationError with code `INVALID_TYPE`
- Inconsistent total_value → ValidationError with code `INCONSISTENT_TOTAL`

**Tests (unit):**

- Valid BUY → no errors
- Quantity = 0 → ZERO_QUANTITY error
- Invalid transaction type → INVALID_TYPE error
- total_value ≠ quantity × unit_price (beyond tolerance) → INCONSISTENT_TOTAL error
- Missing occurred_at → MISSING_FIELD error

---

### Story 2.5 — FIFO Cost Basis Calculator

As the system, I want to calculate the realized profit/loss for a set of transactions using FIFO so that sell events correctly consume the oldest buy lots.

**Tasks:**

- Implement `CostBasisCalculator.calculate(transactions: list[Transaction]) -> list[ProcessingResult]`
- One FIFO queue per asset
- Sort transactions by `occurred_at` before processing
- Handle partial lot consumption on sell

**Acceptance Criteria:**

- Single BUY + single SELL → correct realized P&L
- Multiple BUYs at different prices → FIFO order verified in P&L calculation
- SELL quantity > total bought → error recorded, partial match executed
- SELL with no prior BUY → error recorded, no P&L calculated
- TRANSFER and DEPOSIT → no P&L impact
- FEE in same asset as trade → adjusts cost basis of most recent lot

**Tests (unit):**

- BUY 1 BTC @ 10 USD, SELL 1 BTC @ 120 USD → realized profit = 110 USD ✓
- BUY 1 BTC @ 10, BUY 1 BTC @ 20, SELL 2 BTC @ 50 → FIFO: cost basis = 30, profit = 70 ✓
- SELL before any BUY → ProcessingError recorded
- SELL more than available → partial match + error
- Duplicate transaction ID → second one rejected with error
- Transactions out of order by timestamp → sorted, result is same as if in order
- FEE 0.001 BTC attached to BUY 1 BTC → net position = 0.999 BTC at adjusted cost basis
- TRANSFER → recorded, no P&L, position unchanged

---

## Epic 3 — CSV Parser 🔴

**Goal:** Parse Binance CSV exports reliably, collecting errors per row without halting.

> **Why tests matter here:** Real CSV files from exchanges are messy. Untested edge cases cause silent data loss or crashes in production.

---

### Story 3.1 — Binance CSV Parser

As the system, I want to parse a Binance CSV export file into a list of raw dicts so that the normalizer can convert them to domain transactions.

**Tasks:**

- Implement `BinanceCsvParser.parse(content: bytes) -> ParseResult`
- Split asset pairs (e.g. `BTCUSDT` → `BTC` + `USDT`)
- Collect per-row errors without halting

**Acceptance Criteria:**

- Valid file → correct list of raw dicts with no errors
- Row with malformed date → ParseError for that row only
- Missing required column → fatal ParseError, empty rows
- BOM-encoded file → parsed correctly

**Tests (unit):** see CHECKLIST.md Phase 2 test items.

---

## Epic 4 — Persistence 🔴

**Goal:** All domain objects persisted to PostgreSQL through clean repository implementations.

> **Why tests matter here:** Incorrect repository implementations cause data loss, duplicate records, or wrong query results. Financial data must be stored and retrieved with exact precision.

---

### Story 4.1 — Database Schema

As a developer, I want a versioned database schema managed by Alembic so that the database can be reproduced from scratch at any time.

**Acceptance Criteria:**

- `alembic upgrade head` creates all 4 tables
- `alembic downgrade -1` reverts cleanly
- All `NUMERIC` columns use scale 18 for financial precision

---

### Story 4.2 — Repository Implementations

As the system, I want concrete repository implementations so that use cases can persist and retrieve domain objects without knowing about SQL.

**Tasks:**

- Implement all 4 `Pg*Repository` classes
- Map between ORM models and domain entities explicitly

**Acceptance Criteria:**

- `save_batch([tx1, tx2])` persists both rows, rollback on any error
- `find_by_job_id(job_id)` returns exactly the persisted transactions
- `exists_by_external_id(id)` returns True/False correctly
- All repositories tested against a real PostgreSQL test database

---

## Epic 5 — Application Use Cases 🔴

**Goal:** Orchestrate domain + infra into clearly named operations.

---

### Story 5.1 — Import Transactions

**Acceptance Criteria:**

- Creates `ProcessingJob` with status `pending` at start
- Returns `job_id` after import completes
- Valid rows persisted to `transactions`
- Invalid rows recorded in `validation_errors`
- Job status updated to `imported` on success, `failed` on fatal error
- **Tests:** see CHECKLIST.md Phase 4 items

---

### Story 5.2 — Process Transactions

**Acceptance Criteria:**

- Only processes jobs in `imported` status
- Results persisted per asset to `processing_results`
- Job status updated to `processed` on success
- Domain error raised if job not found or already processed
- **Tests:** see CHECKLIST.md Phase 4 items

---

### Story 5.3 — Get Portfolio Summary

**Acceptance Criteria:**

- Returns one row per asset with: `realized_profit`, `remaining_quantity`, `remaining_cost_basis`
- Aggregates correctly across multiple processed jobs
- Returns empty list if no processed jobs exist

---

## Epic 6 — REST API 🔴

**Goal:** Expose all use cases through a typed, documented FastAPI.

---

### Story 6.1 — Import Endpoint

`POST /api/v1/imports/csv`

**Acceptance Criteria:**

- Accepts `multipart/form-data` with a file field
- Returns `{ job_id, status: "imported", valid_rows, error_rows }`
- Returns 422 if file is not a CSV or exceeds size limit
- Returns 500 with error detail if fatal parsing error occurs

---

### Story 6.2 — Process Endpoint

`POST /api/v1/process/{job_id}`

**Acceptance Criteria:**

- Returns processing results summary on success
- Returns 404 if job not found
- Returns 409 if job already processed

---

### Story 6.3 — Job Status Endpoints

`GET /api/v1/jobs` and `GET /api/v1/jobs/{job_id}`

**Acceptance Criteria:**

- Returns all job fields including status, timestamps, row counts
- Returns 404 for unknown job_id
- List endpoint returns empty array (not 404) when no jobs exist

---

### Story 6.4 — Portfolio Summary Endpoint

`GET /api/v1/portfolio/summary`

**Acceptance Criteria:**

- Returns array of per-asset summaries
- Each entry has: asset, realized_profit, remaining_quantity, remaining_cost_basis
- Returns empty array when no data exists (not 404)

---

## Epic 6.5 — CI Pipeline 🔴

**Goal:** Automate lint, test and build checks on every push so that `main` is always in a releasable state.

---

### Story 6.5.1 — CI Workflow

As a developer, I want every PR to be automatically linted and tested so that broken code cannot reach `main`.

**Tasks:**

- Create `.github/workflows/ci.yml` with lint, unit test, integration test and Docker build stages
- Configure PostgreSQL as a service container in the integration test job
- Run `alembic upgrade head` before integration tests in CI

**Acceptance Criteria:**

- Lint stage fails on any Ruff, Black or Mypy violation
- Unit test stage fails if coverage drops below 80%
- Integration stage runs against a real PostgreSQL container (not mocks)
- Docker image is pushed to GHCR only on merge to `main` (not on PRs)
- `main` branch protection requires CI to pass before merge

---

## Epic 7 — Async Queue 🟡

**Goal:** Decouple upload from processing; support large files without blocking the HTTP request.

**Stories:**

- Story 7.1: Redis + RQ integration
- Story 7.2: Background import job
- Story 7.3: Background processing job
- Story 7.4: Worker service in Docker Compose

---

## Epic 8 — Frontend 🟢

**Goal:** Minimal operational UI for upload, monitoring and result visualization.

**Stories:**

- Story 8.1: CSV upload page
- Story 8.2: Job list and status page
- Story 8.3: Portfolio summary page
- Story 8.4: Docker integration

---

## Epic 9 — Production & Cloud ⚪

**Goal:** Deploy to Azure with a proper CD pipeline, hardened application configuration, and basic observability.

**Stories:**

- Story 9.1: Application hardening — structlog JSON logging, multi-stage Dockerfile, HEALTHCHECK, CORS, rate limiting
- Story 9.2: Azure infrastructure — Container Apps, PostgreSQL, Blob Storage, Key Vault
- Story 9.3: CD staging pipeline — auto-deploy on merge to `main`, migration step, smoke test
- Story 9.4: CD production pipeline — tag-triggered (`v*`), manual approval gate, rollback on failed smoke test
- Story 9.5: JWT authentication — demo user, protected endpoints
- Story 9.6: Observability — Azure Monitor integration, structured JSON logs with `trace_id` and `job_id`

---

## Epic 10 — Premium Features ⚪

**Stories:**

- Story 10.1: Weighted average cost basis
- Story 10.2: Binance REST API integration
- Story 10.3: CSV/JSON report export
- Story 10.4: Position snapshots
- Story 10.5: Multi-user support
