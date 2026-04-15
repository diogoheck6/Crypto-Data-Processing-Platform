# Roadmap — Crypto Data Processing Platform

> Phases are ordered by logical dependency. Each phase must be fully done (code + tests) before the next begins.
> Frontend and cloud are deliberately last — the backend core must be solid first.

---

## Phase 0 — Project Foundation

**Goal:** A clean, runnable project skeleton with tooling, Docker and an empty but structured codebase.

**Deliverables:**

- Repository structure matching Clean Architecture
- `pyproject.toml` with all initial dependencies
- `Dockerfile` + `docker-compose.yml` (app + PostgreSQL)
- `.env.example` and `python-dotenv` wiring
- Ruff + Black + Mypy configured
- Pre-commit hooks installed and passing (including `bandit` for security linting)
- `pytest` baseline running (even if no tests yet)
- `README.md` skeleton with how-to-run instructions
- `.gitignore` covering `.env`, caches and build artifacts
- `Makefile` with targets: `up`, `down`, `test`, `test-unit`, `test-integration`, `lint`, `migrate`
- `.github/dependabot.yml` for automated pip dependency updates (weekly)
- Branch strategy documented in `README.md`: `main` protected; work on `feature/*` branches

**Dependencies:** None  
**Exit criteria:** `docker compose up` starts the app; `pre-commit run --all-files` passes clean; `make test` runs the suite.

---

## Phase 1 — Domain Layer

**Goal:** The entire business logic implemented as pure Python — no database, no HTTP, no framework.

**Deliverables:**

- Entities: `Transaction`, `AssetPosition`, `ProcessingJob`, `ProcessingResult`
- Value Objects: `Money`, `Quantity`, `AssetSymbol`, `TransactionType`, `CostBasisMethod`
- Domain Services: `TransactionValidator`, `TransactionNormalizer`, `CostBasisCalculator` (FIFO), `ProfitLossCalculator`
- Abstract repository interfaces (ports): `ITransactionRepository`, `IJobRepository`, `IResultRepository`
- 100% unit test coverage of all value objects and domain services
- Tests must cover all edge cases defined in MVP_SCOPE.md

**Dependencies:** Phase 0  
**Exit criteria:** `pytest tests/unit/` passes with 100% coverage; no import outside `src/domain/`.

---

## Phase 2 — CSV Parser

**Goal:** Parse a real Binance CSV export into internal `Transaction` objects.

**Deliverables:**

- `BinanceCsvParser` adapter in `src/infra/parsers/`
- Handles: header detection, date parsing, asset pair splitting, fee column extraction
- Returns a list of raw dicts + a list of parse errors (does not raise on bad rows)
- Unit tests: valid CSV, missing columns, malformed dates, empty file, BOM encoding, extra whitespace

**Dependencies:** Phase 1 (needs `Transaction` model to map to)  
**Exit criteria:** `pytest tests/unit/test_binance_parser.py` passes; all edge cases covered.

---

## Phase 3 — Persistence (PostgreSQL + Repositories)

**Goal:** Persist all domain objects to PostgreSQL through clean repository implementations.

**Deliverables:**

- SQLAlchemy ORM models for: `transactions`, `processing_jobs`, `processing_results`, `validation_errors`
- Alembic: initial migration
- Concrete repository implementations: `PgTransactionRepository`, `PgJobRepository`, `PgResultRepository`, `PgValidationErrorRepository`
- Integration tests for all repositories using a dedicated test database
- `pytest` fixture: isolated DB session per test (transactions rolled back after each test)

**Dependencies:** Phase 1 (repository interfaces), Phase 0 (Docker + PostgreSQL)  
**Exit criteria:** `pytest tests/integration/test_repositories.py` passes against a real DB; migrations apply cleanly.

---

## Phase 4 — Application Layer (Use Cases)

**Goal:** Orchestrate domain + infra into concrete use cases that represent system operations.

**Deliverables:**

- `ImportTransactions` use case: receives raw file content → creates job → parses → normalizes → validates → persists transactions + errors
- `ProcessTransactions` use case: receives `job_id` → loads transactions → runs FIFO → persists `ProcessingResult` → updates job status
- `GetJobStatus` use case: returns current job state
- `GetPortfolioSummary` use case: aggregates results per asset, returns P&L + position
- Integration tests for all use cases (real DB, no HTTP)

**Dependencies:** Phases 1, 2, 3  
**Exit criteria:** `pytest tests/integration/test_use_cases.py` passes; all happy paths + key error paths covered.

---

## Phase 5 — API Layer (FastAPI)

**Goal:** Expose all use cases through a documented, typed REST API.

**Deliverables:**

- FastAPI app wiring (`src/api/`)
- Pydantic schemas for all request/response models
- Routes: `POST /imports/csv`, `POST /process/{job_id}`, `GET /jobs`, `GET /jobs/{job_id}`, `GET /results/{job_id}`, `GET /portfolio/summary`
- Health: `GET /health`, `GET /ready`
- Dependency injection via FastAPI `Depends` (repository + use case injection)
- API tests using `TestClient` + test database

**Dependencies:** Phase 4  
**Exit criteria:** `pytest tests/api/` passes; Swagger UI at `/docs` documents all endpoints correctly.

---

## Phase 5.5 — CI Pipeline

**Goal:** Every push is automatically linted, tested and validated before it can merge to `main`.

**Deliverables:**

- `.github/workflows/ci.yml` with four stages:
  1. **Lint** — Ruff + Black + Mypy
  2. **Unit tests** — `pytest tests/unit/` with coverage gate ≥ 80%
  3. **Integration tests** — PostgreSQL service container, `alembic upgrade head`, `pytest tests/integration/ tests/api/`
  4. **Build** — Docker image built on every run; pushed to GHCR only on merge to `main`
- `main` branch protection: CI must pass before merge
- CI badge added to `README.md`

**Dependencies:** Phase 5 (all tests must exist for CI to be meaningful)  
**Exit criteria:** A PR that drops coverage below 80% is blocked; green CI badge on `main`.

---

## Phase 6 — Async Processing Queue

**Goal:** Decouple CSV upload from processing using Redis + a task queue.

**Deliverables:**

- Redis added to `docker-compose.yml`
- Task queue integration (RQ or Dramatiq)
- `ImportTransactions` and `ProcessTransactions` dispatched as background jobs
- `POST /imports/csv` returns immediately with `job_id`; processing happens asynchronously
- Job status polling via `GET /jobs/{job_id}`
- Worker process defined and runnable via Docker
- Integration tests for async flow (enqueue → worker → result)

**Dependencies:** Phase 5  
**Exit criteria:** Upload returns `202 Accepted` with `job_id`; result appears after worker runs.

---

## Phase 7 — Frontend (Next.js)

**Goal:** Minimal operational UI for upload, job monitoring and result visualization.

**Deliverables:**

- Next.js + TypeScript app in `frontend/`
- Pages: Upload CSV, Job List, Job Detail, Portfolio Summary
- API client using `fetch` or React Query
- Responsive layout with Tailwind CSS
- No authentication in MVP frontend (demo mode)

**Dependencies:** Phase 5 (API must be stable)  
**Exit criteria:** Full upload → view result flow works end-to-end in browser.

---

## Phase 8 — Production Hardening & Cloud Deploy

**Goal:** Deploy to Azure with a proper CD pipeline, hardened application config, and basic observability.

**Deliverables:**

- Structured logging with `structlog` (JSON format with `trace_id`, `job_id`, `level`, `timestamp`)
- Production-optimized `Dockerfile` (multi-stage build, non-root user, `HEALTHCHECK` instruction)
- CORS production config, rate limiting, JWT authentication (demo user)
- Azure infrastructure: Container Apps + PostgreSQL + Blob Storage + Redis Cache
- Secrets via Azure Key Vault / environment variables (never in code or CI logs)
- `.github/workflows/deploy-staging.yml` — auto-triggers on merge to `main`; runs `alembic upgrade head` then deploys
- `.github/workflows/deploy-prod.yml` — triggers on git tag `v*`; requires manual approval
- Post-deploy smoke test: `GET /ready` must return 200 before deploy is marked successful
- Rollback: re-deploy previous image SHA if smoke test fails
- Azure Monitor / Application Insights configured to ingest structured JSON logs
- `README.md` updated with deploy instructions and live demo link

**Dependencies:** Phases 6, 7  
**Exit criteria:** Merge to `main` triggers staging deploy automatically; app is live at an Azure URL; `/ready` returns 200.

---

## Phase 9 — Premium Evolutions

**Goal:** Extend the platform with advanced features for a production-grade portfolio piece.

**Deliverables:**

- Weighted average cost basis (alternative to FIFO)
- Binance REST API integration (real-time transaction fetch)
- Multi-user support with proper data isolation
- Position snapshots (historical state at any point in time)
- CSV/JSON export of reports
- Advanced dashboard: per-asset charts, P&L timeline
- Observability: metrics, health dashboard, error alerting

**Dependencies:** Phase 8  
**Exit criteria:** Defined per feature when implemented.

---

## Dependency Graph

```
Phase 0 (Foundation)
    └── Phase 1 (Domain)
            ├── Phase 2 (CSV Parser)
            └── Phase 3 (Persistence)
                    └── Phase 4 (Use Cases)
                            └── Phase 5 (API)
                                    └── Phase 5.5 (CI Pipeline)
                                            ├── Phase 6 (Queue)
                                            └── Phase 7 (Frontend)
                                                    └── Phase 8 (Deploy)
                                                            └── Phase 9 (Premium)
```

---

## Current Status

| Phase                   | Status         |
| ----------------------- | -------------- |
| Phase 0 — Foundation    | 🔴 Not Started |
| Phase 1 — Domain        | 🔴 Not Started |
| Phase 2 — CSV Parser    | 🔴 Not Started |
| Phase 3 — Persistence   | 🔴 Not Started |
| Phase 4 — Use Cases     | 🔴 Not Started |
| Phase 5 — API           | 🔴 Not Started |
| Phase 5.5 — CI Pipeline | 🔴 Not Started |
| Phase 6 — Queue         | 🔴 Not Started |
| Phase 7 — Frontend      | 🔴 Not Started |
| Phase 8 — Deploy        | 🔴 Not Started |
| Phase 9 — Premium       | 🔴 Not Started |
