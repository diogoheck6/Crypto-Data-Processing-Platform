# Checklist — Crypto Data Processing Platform

> Operational checklist. Work through tasks top to bottom, one at a time.
> Mark tasks as done only after code is written **and** tests pass.
> Update STATUS.md and NEXT_STEP.md after completing each section.

---

## Phase 0 — Project Foundation

### Repository structure

- [x] Create top-level directories: `src/`, `tests/`, `docs/`, `docker/`, `alembic/`
- [x] Create `src/__init__.py` and subdirectory structure: `domain/`, `application/`, `infra/`, `api/`
- [x] Create `tests/` subdirectory structure: `unit/`, `integration/`, `api/`
- [x] Mirror `src/domain/` inside `tests/unit/domain/`: `value_objects/`, `entities/`, `services/`, `ports/`

### Python project setup

- [x] Create `pyproject.toml` with project metadata and dependencies
- [x] Pin versions for: `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `psycopg2-binary`, `pydantic`, `python-dotenv`, `pytest`, `pytest-cov`, `ruff`, `black`, `mypy`
- [x] Create `.env.example` with all required environment variables documented
- [x] Create `src/config.py` to load settings from environment using `python-dotenv`

### Docker

- [x] Write `Dockerfile` for the API (non-root user, multi-stage build not needed yet)
- [x] Write `docker-compose.yml` with services: `api`, `db` (PostgreSQL 16)
- [x] Write `docker-compose.test.yml` with isolated test database
- [x] Verify `docker compose up` starts the app and DB successfully
- [x] Verify `docker compose -f docker-compose.test.yml up -d db_test` starts the test DB

### Tooling

- [x] Create `ruff.toml` or configure ruff in `pyproject.toml`
- [x] Create `mypy.ini` or configure mypy in `pyproject.toml`
- [x] Create `.pre-commit-config.yaml` with: ruff, black, mypy
- [x] Run `pre-commit install`
- [x] Run `pre-commit run --all-files` — must pass clean
- [x] Create `pytest.ini` or configure pytest in `pyproject.toml` (testpaths, coverage settings)
- [x] Verify `pytest` runs (even with zero tests, must not error)

### README skeleton

- [x] Add project title, description, tech stack section
- [x] Add "How to run locally" section (docker compose commands)
- [x] Add "How to run tests" section
- [x] Add "Architecture overview" section (link to ARCHITECTURE.md)

### DevOps foundations

- [x] Create `.gitignore` covering: `.env`, `__pycache__`, `.mypy_cache`, `.pytest_cache`, `dist/`, `*.egg-info`, `.ruff_cache`
- [x] Create `Makefile` with targets: `up`, `down`, `test`, `test-unit`, `test-integration`, `lint`, `format`, `migrate`, `shell`
- [ ] Create `.github/dependabot.yml` for pip dependency updates (weekly) ← deferred to Phase 5.5
- [x] Add `bandit` to `.pre-commit-config.yaml`
- [x] Document branch strategy in `README.md`: `main` protected; work on `feature/*` branches; PR required to merge
- [x] List all required GitHub Secrets in `.env.example` comments

**Phase 0 exit check:** ✅ `docker compose up` starts → `pre-commit run --all-files` clean → `pytest` runs without error → `GET /health` returns `{"status": "ok"}`.

---

## Phase 1 — Domain Layer

### Value Objects

- [x] Implement `Money(amount: Decimal, currency: str)` — frozen dataclass, validates positive amount
- [x] Implement `Quantity(amount: Decimal)` — frozen dataclass, validates non-negative
- [x] Implement `AssetSymbol(symbol: str)` — frozen dataclass, uppercase normalization
- [x] Implement `TransactionType` — Enum: `BUY`, `SELL`, `FEE`, `DEPOSIT`, `WITHDRAWAL`, `TRANSFER`
- [x] Implement `CostBasisMethod` — Enum: `FIFO`, `WEIGHTED_AVERAGE`

### Unit tests — Value Objects

- [x] `test_money.py`: valid creation, negative amount raises, zero amount raises, equality
- [x] `test_quantity.py`: valid creation, negative raises, zero is valid (no-op position)
- [x] `test_asset_symbol.py`: uppercase normalization, empty string raises
- [x] `test_transaction_type.py`: all members present, invalid string raises

### Entities

- [x] Implement `Transaction` dataclass (all fields from DB schema, plus `transaction_type: TransactionType`)
- [x] Implement `AssetPosition(asset: AssetSymbol, queue: deque[Transaction])` — FIFO queue holder
- [x] Implement `ProcessingJob` dataclass (id, status, source_type, timestamps)
- [x] Implement `ProcessingResult` dataclass (asset, realized_profit, cost_basis, remaining_quantity, remaining_cost_basis)

### Repository Ports (Abstract Interfaces)

- [ ] `ITransactionRepository`: `save_batch`, `find_by_job_id`, `exists_by_external_id`
- [ ] `IJobRepository`: `save`, `update_status`, `find_by_id`, `find_all`
- [ ] `IResultRepository`: `save_batch`, `find_by_job_id`
- [ ] `IValidationErrorRepository`: `save_batch`, `find_by_job_id`

### Domain Services

- [ ] Implement `TransactionNormalizer.normalize(raw: dict) -> Transaction` — maps raw keys to domain fields
- [ ] Implement `TransactionValidator.validate(t: Transaction) -> list[ValidationError]` — all rules from MVP_SCOPE.md
- [ ] Implement `CostBasisCalculator.calculate(transactions: list[Transaction]) -> list[ProcessingResult]` — FIFO per asset
- [ ] Implement `ProfitLossCalculator.calculate(fifo_output) -> ProcessingResult` — realized P&L

### Unit tests — Domain Services

- [ ] `test_transaction_normalizer.py`: valid dict, missing required field, unknown field ignored
- [ ] `test_transaction_validator.py`: valid transaction passes, zero quantity fails, invalid date fails, unknown type fails, duplicate detection
- [ ] `test_cost_basis_calculator.py`:
  - [ ] Single buy + single sell → correct P&L
  - [ ] Multiple buys at different prices + sell (FIFO order verified)
  - [ ] Sell quantity exceeds total bought → error recorded, partial match
  - [ ] Sell with no prior buy → error recorded
  - [ ] Fee in same asset reduces cost basis
  - [ ] Fee in different asset does not affect cost basis
  - [ ] Transactions out of chronological order → sorted before processing
  - [ ] Transfer and deposit → do not generate P&L
  - [ ] Duplicate transaction ID → rejected
  - [ ] Zero quantity transaction → rejected

**Phase 1 exit check:** `pytest tests/unit/ --cov=src/domain --cov-fail-under=100 --cov-report=term-missing` → 100% domain coverage. See ARCHITECTURE.md § Test Coverage Standards for per-layer targets.

---

## Phase 2 — CSV Parser

### BinanceCsvParser

- [ ] Implement `BinanceCsvParser.parse(content: bytes) -> ParseResult`
- [ ] `ParseResult` contains: `rows: list[dict]`, `errors: list[ParseError]`
- [ ] Handle BOM encoding (`utf-8-sig`)
- [ ] Detect and skip empty rows
- [ ] Split asset pairs (e.g. `BTCUSDT` → asset=`BTC`, quote=`USDT`)
- [ ] Map Binance column names to internal raw field names
- [ ] Collect per-row parse errors without stopping (non-fatal mode)
- [ ] Handle missing required columns (fatal error, return empty rows + one error)

### Unit tests — BinanceCsvParser

- [ ] Valid Binance CSV (buy + sell + fee rows) → correct list[dict]
- [ ] Missing required column → ParseResult with one fatal error, empty rows
- [ ] Row with malformed date → ParseError for that row, other rows parsed
- [ ] Row with non-numeric amount → ParseError for that row
- [ ] Empty file → ParseResult with one error, empty rows
- [ ] File with only headers, no data rows → ParseResult with zero rows, no error
- [ ] BOM-encoded file → parsed correctly
- [ ] Extra unknown columns → ignored silently

**Phase 2 exit check:** `pytest tests/unit/parsers/` passes; all edge cases covered.

---

## Phase 3 — Persistence

### ORM Models (SQLAlchemy)

- [ ] Define `TransactionModel` mapping to `transactions` table
- [ ] Define `ProcessingJobModel` mapping to `processing_jobs` table
- [ ] Define `ProcessingResultModel` mapping to `processing_results` table
- [ ] Define `ValidationErrorModel` mapping to `validation_errors` table
- [ ] Define `Base` and import all models in one place for Alembic

### Alembic

- [ ] Initialize Alembic (`alembic init`)
- [ ] Configure `alembic/env.py` to use app's `DATABASE_URL` and `Base.metadata`
- [ ] Generate initial migration: `alembic revision --autogenerate -m "initial schema"`
- [ ] Verify migration applies cleanly: `alembic upgrade head`
- [ ] Verify `alembic downgrade -1` reverts cleanly

### Repository Implementations

- [ ] Implement `PgTransactionRepository` (implements `ITransactionRepository`)
- [ ] Implement `PgJobRepository` (implements `IJobRepository`)
- [ ] Implement `PgResultRepository` (implements `IResultRepository`)
- [ ] Implement `PgValidationErrorRepository` (implements `IValidationErrorRepository`)
- [ ] Each repository maps between ORM model ↔ domain entity explicitly

### Integration tests — Repositories

- [ ] `conftest.py`: pytest fixture that creates a test DB session, rolls back after each test
- [ ] `test_pg_transaction_repository.py`: `save_batch`, `find_by_job_id`, `exists_by_external_id`
- [ ] `test_pg_job_repository.py`: `save`, `update_status`, `find_by_id`, `find_all`
- [ ] `test_pg_result_repository.py`: `save_batch`, `find_by_job_id`
- [ ] `test_pg_validation_error_repository.py`: `save_batch`, `find_by_job_id`

**Phase 3 exit check:** `pytest tests/integration/repositories/` passes against test DB.

---

## Phase 4 — Application / Use Cases

### Use Case Implementations

- [ ] Implement `ImportTransactions(parser, normalizer, validator, tx_repo, job_repo, error_repo)`
  - [ ] Creates `ProcessingJob` with status `pending`
  - [ ] Calls parser → normalizer → validator
  - [ ] Persists valid transactions + validation errors
  - [ ] Updates job status to `imported` (or `failed` on fatal error)
  - [ ] Returns `job_id`
- [ ] Implement `ProcessTransactions(job_repo, tx_repo, calculator, result_repo)`
  - [ ] Loads job, validates status is `imported`
  - [ ] Loads all transactions for job, sorts by `occurred_at`
  - [ ] Runs FIFO calculator
  - [ ] Persists `ProcessingResult` per asset
  - [ ] Updates job status to `processed` (or `failed`)
- [ ] Implement `GetJobStatus(job_repo)` → returns job DTO
- [ ] Implement `GetPortfolioSummary(result_repo)` → returns aggregated P&L + positions

### Integration tests — Use Cases

- [ ] `test_import_transactions.py`: valid CSV → job created + transactions persisted + job status=imported
- [ ] `test_import_transactions.py`: CSV with bad rows → valid rows persisted + errors recorded + job status=imported
- [ ] `test_import_transactions.py`: fatal parse error → job status=failed, no transactions
- [ ] `test_process_transactions.py`: valid job → results calculated and persisted + job status=processed
- [ ] `test_process_transactions.py`: job not found → domain error raised
- [ ] `test_process_transactions.py`: job already processed → domain error raised
- [ ] `test_get_portfolio_summary.py`: multiple processed jobs → correct aggregation

**Phase 4 exit check:** `pytest tests/integration/use_cases/` passes; all paths covered.

---

## Phase 5 — API Layer

### FastAPI Setup

- [ ] Create `src/api/main.py` with `create_app()` factory function
- [ ] Register all routers with `/api/v1` prefix
- [ ] Register health router at root (`/health`, `/ready`)
- [ ] Configure CORS (permissive for development)
- [ ] Configure global exception handler for domain errors → HTTP 422/400/404
- [ ] Configure upload size limit

### Dependency Injection

- [ ] `src/api/dependencies.py`: DB session factory via `Depends`
- [ ] Inject repositories per request
- [ ] Inject use cases via repositories

### Schemas

- [ ] `ImportResponseSchema`: `job_id`, `status`, `message`
- [ ] `JobStatusSchema`: all `ProcessingJob` fields
- [ ] `JobListSchema`: list of `JobStatusSchema`
- [ ] `ProcessingResultSchema`: per-asset result fields
- [ ] `PortfolioSummarySchema`: list of per-asset summaries + totals
- [ ] `ValidationErrorSchema`: for displaying import errors

### Routers

- [ ] `POST /api/v1/imports/csv` → calls `ImportTransactions`, returns `ImportResponseSchema`
- [ ] `POST /api/v1/process/{job_id}` → calls `ProcessTransactions`, returns `ProcessingResultSchema`
- [ ] `GET /api/v1/jobs` → calls `GetJobStatus` list, returns `JobListSchema`
- [ ] `GET /api/v1/jobs/{job_id}` → calls `GetJobStatus`, returns `JobStatusSchema`
- [ ] `GET /api/v1/results/{job_id}` → calls result query, returns list of `ProcessingResultSchema`
- [ ] `GET /api/v1/portfolio/summary` → calls `GetPortfolioSummary`, returns `PortfolioSummarySchema`
- [ ] `GET /health` → returns `{"status": "ok"}`
- [ ] `GET /ready` → checks DB connection, returns 200 or 503

### API tests

- [ ] `conftest.py`: `TestClient` fixture with test DB and clean state per test
- [ ] `test_imports_api.py`: upload valid CSV → 200 + job_id; upload invalid file → 422
- [ ] `test_jobs_api.py`: get existing job → 200; get unknown job → 404; list jobs → 200
- [ ] `test_process_api.py`: trigger processing → 200; trigger on unknown job → 404
- [ ] `test_results_api.py`: get results after processing → 200 with correct data
- [ ] `test_portfolio_api.py`: portfolio summary after processing → correct aggregation
- [ ] `test_health_api.py`: `/health` → 200; `/ready` → 200 when DB is up

**Phase 5 exit check:** `pytest tests/api/` passes; `/docs` shows all endpoints.

---

## Phase 5.5 — CI Pipeline

### GitHub Actions workflow

- [ ] Create `.github/workflows/ci.yml`
- [ ] Stage 1 — Lint: `ruff check src/` + `black --check src/` + `mypy src/`
- [ ] Stage 2 — Unit tests: `pytest tests/unit/ --cov=src --cov-fail-under=80`
- [ ] Stage 3 — Integration + API tests: postgres service in CI, `alembic upgrade head`, `pytest tests/integration/ tests/api/`
- [ ] Stage 4 — Docker build: build image on every run; push to GHCR only on merge to `main`
- [ ] Enable branch protection on `main`: require CI to pass before merge
- [ ] Add CI status badge to `README.md`

**Phase 5.5 exit check:** PR with a failing test is blocked by CI; green badge appears on `main` after a clean push.

---

## Phase 6 — Async Queue

- [ ] Add `redis` service to `docker-compose.yml`
- [ ] Add RQ (or Dramatiq) to dependencies
- [ ] Extract `ImportTransactions` call into a background task function
- [ ] Extract `ProcessTransactions` call into a background task function
- [ ] `POST /api/v1/imports/csv` → enqueues job → returns `202 Accepted` with `job_id`
- [ ] Create `worker.py` entrypoint for the queue worker
- [ ] Add `worker` service to `docker-compose.yml`
- [ ] Integration test: enqueue → poll status → result appears

---

## Phase 7 — Frontend

- [ ] Initialize Next.js app in `frontend/` (`npx create-next-app`)
- [ ] Configure TypeScript + Tailwind CSS
- [ ] Create API client (`lib/api.ts`) with typed fetch wrappers
- [ ] Page: Upload CSV (form + file picker + progress)
- [ ] Page: Job List (table of all jobs with status badges)
- [ ] Page: Job Detail (status, error count, link to results)
- [ ] Page: Portfolio Summary (per-asset table with P&L)
- [ ] Add `frontend` service to `docker-compose.yml`
- [ ] End-to-end test: upload CSV → poll → view results in browser

---

## Phase 8 — Production & Cloud

### Application hardening

- [ ] Add `structlog` structured logging (JSON format with fields: `timestamp`, `level`, `trace_id`, `job_id`, `asset`)
- [ ] Optimize `Dockerfile`: multi-stage build, non-root user, `HEALTHCHECK` instruction
- [ ] Add CORS production config (specific allowed origins only)
- [ ] Add rate limiting middleware
- [ ] Add JWT authentication (demo user endpoint)

### Azure infrastructure

- [ ] Configure Azure Container Apps for the API
- [ ] Configure Azure Database for PostgreSQL (enable automated backups)
- [ ] Configure Azure Blob Storage for CSV uploads
- [ ] Configure Azure Cache for Redis
- [ ] Manage all secrets via Azure Key Vault (no secrets in code or CI logs)

### CD pipeline

- [ ] Create `.github/workflows/deploy-staging.yml`: auto-triggers on merge to `main`; runs `alembic upgrade head` then deploys new image
- [ ] Create `.github/workflows/deploy-prod.yml`: triggers on git tag `v*`; requires manual approval before deploy
- [ ] Tag Docker images with git SHA; `latest` always = last green `main`
- [ ] Add post-deploy smoke test: `curl /ready` must return 200 before marking deploy successful
- [ ] Configure rollback: re-deploy previous image SHA if smoke test fails
- [ ] Configure Azure Monitor / Application Insights to ingest structured JSON logs
- [ ] Update `README.md` with full deploy instructions and live demo link
