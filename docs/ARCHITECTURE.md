# Architecture — Crypto Data Processing Platform

> Clean Architecture with hexagonal (ports & adapters) inspiration.
> The domain layer has zero external dependencies. All external concerns are adapters.

---

## Guiding Principles

1. **The domain is the center.** Business rules do not know about databases, HTTP, or files.
2. **Dependency inversion everywhere.** Application layer depends on abstract ports; infrastructure implements them.
3. **Test seams by design.** Every external dependency can be replaced with a fake/mock in tests.
4. **One-way dependency rule.** `domain ← application ← infrastructure ← api`. Never reversed.
5. **No framework inside the domain.** No FastAPI, SQLAlchemy, or Pydantic in `src/domain/`.

---

## Layer Responsibilities

### `src/domain/`

The pure business core. No I/O, no framework, no external library (except `dataclasses` and `decimal`).

```
src/domain/
├── entities/
│   ├── transaction.py          # Transaction (canonical internal model)
│   ├── asset_position.py       # AssetPosition (accumulated holding per asset)
│   ├── processing_job.py       # ProcessingJob (one import session)
│   └── processing_result.py    # ProcessingResult (output of FIFO calculation)
├── value_objects/
│   ├── money.py                # Money(amount: Decimal, currency: str) — immutable
│   ├── quantity.py             # Quantity(amount: Decimal) — non-negative
│   ├── asset_symbol.py         # AssetSymbol(symbol: str) — e.g. "BTC"
│   ├── transaction_type.py     # Enum: buy, sell, fee, deposit, withdrawal, transfer
│   └── cost_basis_method.py    # Enum: fifo, weighted_average
├── services/
│   ├── transaction_normalizer.py   # Maps raw dict → Transaction
│   ├── transaction_validator.py    # Validates field integrity + business rules
│   ├── cost_basis_calculator.py    # FIFO engine: consumes buy queue on sell events
│   └── profit_loss_calculator.py   # Calculates realized P&L from FIFO output
└── ports/
    ├── i_transaction_repository.py  # Abstract: save/find transactions
    ├── i_job_repository.py          # Abstract: save/update/find jobs
    ├── i_result_repository.py       # Abstract: save/find results
    └── i_validation_error_repository.py
```

**Key design decisions:**

- Entities use Python `dataclasses` (not Pydantic). Pydantic is only at the API boundary.
- Value objects are **frozen dataclasses** — immutable and hashable.
- `CostBasisCalculator` receives a sorted list of `Transaction` objects and returns `ProcessingResult`. Pure function, no side effects.
- Repository ports are **abstract base classes** with typed method signatures.

---

### `src/application/`

Orchestrates domain services + ports to implement system operations.

```
src/application/
└── use_cases/
    ├── import_transactions.py    # Parse → Normalize → Validate → Persist
    ├── process_transactions.py   # Load → FIFO calc → Persist result → Update job
    ├── get_job_status.py         # Load job → return status DTO
    └── get_portfolio_summary.py  # Aggregate results → return summary DTO
```

**Key design decisions:**

- Use cases receive their dependencies (repositories, services) via constructor injection.
- Use cases return **plain dataclass DTOs**, not ORM models or Pydantic models.
- Use cases do not raise HTTP exceptions — they raise domain exceptions or return error DTOs.
- Application layer is fully testable without HTTP or database (using fakes).

---

### `src/infra/`

Concrete implementations of all ports. External world lives here.

```
src/infra/
├── db/
│   ├── models.py               # SQLAlchemy ORM table definitions
│   ├── session.py              # Engine + session factory
│   └── migrations/             # Alembic migration files
├── repositories/
│   ├── pg_transaction_repository.py
│   ├── pg_job_repository.py
│   ├── pg_result_repository.py
│   └── pg_validation_error_repository.py
└── parsers/
    └── binance_csv_parser.py   # Reads Binance CSV → list[dict] + list[ParseError]
```

**Key design decisions:**

- ORM models in `models.py` are separate from domain entities. Mapping is explicit.
- Repositories translate between ORM rows and domain entities — no ORM leaks into the domain.
- `BinanceCsvParser` does not raise on malformed rows; it collects errors and continues parsing.

---

### `src/api/`

FastAPI application. Thin adapter layer — translates HTTP ↔ application use cases.

```
src/api/
├── main.py                     # FastAPI app factory
├── dependencies.py             # DI wiring: sessions, repos, use cases
├── routers/
│   ├── imports.py              # POST /api/v1/imports/csv
│   ├── jobs.py                 # GET /api/v1/jobs, GET /api/v1/jobs/{job_id}
│   ├── results.py              # GET /api/v1/results/{job_id}
│   ├── portfolio.py            # GET /api/v1/portfolio/summary
│   └── health.py               # GET /health, GET /ready
└── schemas/
    ├── import_schemas.py
    ├── job_schemas.py
    ├── result_schemas.py
    └── portfolio_schemas.py
```

**Key design decisions:**

- Routers are thin: validate input → call use case → map output to schema → return.
- All request/response types are Pydantic models defined in `schemas/`.
- Domain exceptions are caught at the router level and mapped to appropriate HTTP status codes.
- Dependencies (DB session, repositories, use cases) are injected via FastAPI `Depends`.

---

## Full Project Structure

```
crypto-data-processing-platform/
├── src/
│   ├── domain/
│   ├── application/
│   ├── infra/
│   └── api/
├── tests/
│   ├── unit/
│   │   ├── domain/             # Value objects, entities, domain services
│   │   └── parsers/            # CSV parser unit tests
│   ├── integration/
│   │   ├── repositories/       # Real DB tests
│   │   └── use_cases/          # Use cases with real DB, no HTTP
│   └── api/                    # API tests with TestClient + test DB
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # Lint + test + build on every push
│   │   ├── deploy-staging.yml  # Auto-deploy on merge to main
│   │   └── deploy-prod.yml     # Manual-approval deploy on tag v*
│   └── dependabot.yml          # Weekly pip dependency updates
├── alembic/
├── docker/
│   └── app/Dockerfile
├── docker-compose.yml
├── docker-compose.test.yml
├── Makefile                    # Standardized developer commands
├── pyproject.toml
├── .env.example
├── .pre-commit-config.yaml
└── README.md
```

---

## Data Flow — CSV Import

```
HTTP POST /api/v1/imports/csv
    │
    ▼
[API Router]
    │ extract file bytes
    ▼
[ImportTransactions use case]
    │
    ├──► [BinanceCsvParser]          → list[raw_dict] + list[ParseError]
    │
    ├──► [TransactionNormalizer]     → list[Transaction]
    │
    ├──► [TransactionValidator]      → list[Transaction (valid)] + list[ValidationError]
    │
    ├──► [ITransactionRepository]    → persist valid transactions
    │
    ├──► [IValidationErrorRepository]→ persist validation errors
    │
    └──► [IJobRepository]            → create ProcessingJob (status=imported)
    │
    ▼
Return job_id to client
```

---

## Data Flow — FIFO Processing

```
HTTP POST /api/v1/process/{job_id}
    │
    ▼
[API Router]
    │
    ▼
[ProcessTransactions use case]
    │
    ├──► [IJobRepository]             → load job, validate status
    │
    ├──► [ITransactionRepository]     → load all transactions for job, sort by occurred_at
    │
    ├──► [CostBasisCalculator (FIFO)] → process buy/sell queue → ProcessingResult
    │
    ├──► [ProfitLossCalculator]       → calculate realized P&L per sell event
    │
    ├──► [IResultRepository]          → persist ProcessingResult
    │
    └──► [IJobRepository]             → update job status to processed
    │
    ▼
Return result summary to client
```

---

## CI/CD Pipeline

```
feature/* branch  →  PR  →  CI  →  merge to main  →  CD staging (auto)
                                                            │
                                                     CD prod (tag v* + approval)
```

**CI stages** (run on every push and PR):

1. **Lint** — Ruff + Black + Mypy
2. **Unit tests** — `pytest tests/unit/` with coverage gate ≥ 80%
3. **Integration tests** — PostgreSQL service container, `alembic upgrade head`, `pytest tests/integration/ tests/api/`
4. **Build** — Docker image built on every run; pushed to GHCR only on merge to `main`

**Image tagging:** `ghcr.io/<owner>/app:<git-sha>` on every green build; `latest` = last green `main`; semver on release (`v1.0.0`).

**CD — staging:** Auto-triggers on merge to `main`. Runs `alembic upgrade head` as a pre-deploy job, deploys the new container, then runs a smoke test (`GET /ready` → 200).

**CD — production:** Triggered by a git tag (`v*`). Requires manual approval. Same migration + smoke test flow. Rollback = re-deploy the previous image SHA if the smoke test fails.

---

## Database Schema

### `transactions`

| Column           | Type                      | Notes                                              |
| ---------------- | ------------------------- | -------------------------------------------------- |
| id               | UUID PK                   |                                                    |
| job_id           | UUID FK → processing_jobs |                                                    |
| external_id      | VARCHAR                   | from source (Binance txn ID); unique per source    |
| source           | VARCHAR                   | e.g. `binance_csv`                                 |
| asset            | VARCHAR                   | e.g. `BTC`                                         |
| transaction_type | VARCHAR                   | buy / sell / fee / deposit / withdrawal / transfer |
| quantity         | NUMERIC(28,18)            | always positive                                    |
| unit_price       | NUMERIC(28,18)            | in quote currency                                  |
| total_value      | NUMERIC(28,18)            | quantity × unit_price                              |
| fee_amount       | NUMERIC(28,18)            | nullable                                           |
| fee_asset        | VARCHAR                   | nullable                                           |
| occurred_at      | TIMESTAMPTZ               | original event timestamp                           |
| raw_payload      | JSONB                     | original row for auditability                      |
| created_at       | TIMESTAMPTZ               |                                                    |

### `processing_jobs`

| Column         | Type        | Notes                                                |
| -------------- | ----------- | ---------------------------------------------------- |
| id             | UUID PK     |                                                      |
| source_type    | VARCHAR     | e.g. `binance_csv`                                   |
| status         | VARCHAR     | pending / imported / processing / processed / failed |
| input_filename | VARCHAR     | original uploaded filename                           |
| total_rows     | INT         | rows in the file                                     |
| valid_rows     | INT         | rows that passed validation                          |
| error_rows     | INT         | rows that failed                                     |
| started_at     | TIMESTAMPTZ |                                                      |
| finished_at    | TIMESTAMPTZ | nullable                                             |
| error_message  | TEXT        | nullable                                             |
| created_at     | TIMESTAMPTZ |                                                      |

### `processing_results`

| Column               | Type           | Notes                                |
| -------------------- | -------------- | ------------------------------------ |
| id                   | UUID PK        |                                      |
| job_id               | UUID FK        |                                      |
| asset                | VARCHAR        |                                      |
| realized_profit      | NUMERIC(28,18) | total realized P&L for this asset    |
| total_cost_basis     | NUMERIC(28,18) | total acquisition cost of sold units |
| remaining_quantity   | NUMERIC(28,18) | unsold units still held              |
| remaining_cost_basis | NUMERIC(28,18) | cost of unsold units                 |
| result_payload       | JSONB          | full FIFO breakdown                  |
| created_at           | TIMESTAMPTZ    |                                      |

### `validation_errors`

| Column     | Type        | Notes                                   |
| ---------- | ----------- | --------------------------------------- |
| id         | UUID PK     |                                         |
| job_id     | UUID FK     |                                         |
| row_number | INT         | source file row                         |
| field_name | VARCHAR     | nullable                                |
| error_code | VARCHAR     | e.g. `MISSING_QUANTITY`, `INVALID_DATE` |
| message    | TEXT        | human-readable description              |
| raw_row    | JSONB       | the offending raw row                   |
| created_at | TIMESTAMPTZ |                                         |

---

## Technical Decisions

Each key decision has a dedicated Architecture Decision Record in [`docs/ADR/`](./ADR/).

| Decision                                          | ADR                                        |
| ------------------------------------------------- | ------------------------------------------ |
| Why Clean Architecture + Hexagonal?               | [ADR 005](./ADR/005-clean-architecture.md) |
| Why FastAPI?                                      | [ADR 001](./ADR/001-fastapi.md)            |
| Why PostgreSQL?                                   | [ADR 002](./ADR/002-postgresql.md)         |
| Why Redis + RQ for the queue?                     | [ADR 003](./ADR/003-redis-queue.md)        |
| Why FIFO first?                                   | [ADR 004](./ADR/004-fifo-first.md)         |
| Why Alembic runs in the pipeline, not at startup? | [ADR 006](./ADR/006-alembic-pipeline.md)   |

### Why separate ORM models from domain entities?

Mixing ORM concerns into domain entities creates hidden coupling to SQLAlchemy. Explicit mapping means the domain can evolve independently, and repositories are testable with simple in-memory fakes — no database required for unit tests.

### Why UUID for all primary keys?

Avoids sequential ID leakage, supports distributed ID generation, and is consistent with event-sourcing patterns if the system evolves in that direction.

### Why synchronous processing in the MVP?

For a single-user tool processing files up to ~50K rows, synchronous processing completes in well under a second. Introducing Redis + RQ in Phase 6 adds real operational value only after the API and domain are stable — see [ADR 003](./ADR/003-redis-queue.md) for the queue decision rationale.
