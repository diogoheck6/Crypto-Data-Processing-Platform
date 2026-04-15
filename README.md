# Crypto Data Processing Platform

> A financial data processing engine for cryptocurrency transactions.
> Ingests Binance CSV exports, applies FIFO cost basis rules, calculates realized P&L, and exposes results through a typed REST API.

---

## What It Does

Cryptocurrency traders and accountants need to answer a precise question from a messy dataset:

> _"Given all my trades, what is my realized profit/loss and current position per asset?"_

This platform solves that by:

1. **Ingesting** Binance CSV exports (and later, other sources)
2. **Normalizing** raw rows into a canonical internal transaction model
3. **Validating** each transaction against financial business rules
4. **Calculating** cost basis using FIFO per asset
5. **Persisting** results with full auditability
6. **Exposing** everything through a documented REST API

This is not a simple CRUD app. It is a financial data processing engine built with production-grade architecture.

---

## Architecture

Clean Architecture with hexagonal (ports & adapters) inspiration.

```
┌─────────────────────────────────────────┐
│              API Layer (FastAPI)         │  ← HTTP adapters
├─────────────────────────────────────────┤
│         Application Layer (Use Cases)   │  ← orchestration
├─────────────────────────────────────────┤
│            Domain Layer                 │  ← pure business logic
│   Entities · Value Objects · Services  │  ← no framework, no I/O
├─────────────────────────────────────────┤
│       Infrastructure Layer              │  ← PostgreSQL · Redis · CSV parser
└─────────────────────────────────────────┘
```

The domain layer has **zero external dependencies**. All I/O is in adapters.

→ Full architecture details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)  
→ Architecture decisions: [docs/ADR/](docs/ADR/)

---

## Tech Stack

| Layer              | Technology                              |
| ------------------ | --------------------------------------- |
| Language           | Python 3.12                             |
| API framework      | FastAPI + Pydantic                      |
| ORM + migrations   | SQLAlchemy + Alembic                    |
| Database           | PostgreSQL 16                           |
| Cache + queue      | Redis + RQ                              |
| Testing            | pytest + pytest-cov                     |
| Linting            | Ruff + Black + Mypy + Bandit            |
| Containers         | Docker + Docker Compose                 |
| CI/CD              | GitHub Actions                          |
| Cloud (Phase 8)    | Azure Container Apps + Azure PostgreSQL |
| Frontend (Phase 7) | Next.js + TypeScript                    |

---

## Quick Start

**Requirements:** Docker and Docker Compose.

```bash
# 1. Clone the repository
git clone https://github.com/diogoheck6/Crypto-Data-Processing-Platform.git
cd Crypto-Data-Processing-Platform

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env if needed — defaults work for local dev

# 3. Start the full stack
make up
# or: docker compose up --build

# 4. Verify the API is running
curl http://localhost:8000/health
# → {"status": "ok"}

# 5. Open the interactive API docs
open http://localhost:8000/docs
```

→ Full setup and troubleshooting: [docs/RUNBOOK.md](docs/RUNBOOK.md)

---

## Running Tests

```bash
# All tests (unit + integration + API)
make test

# Unit tests only (no database required)
make test-unit

# Integration and API tests (requires Docker DB)
make test-integration

# With coverage report
pytest --cov=src --cov-report=term-missing
```

Tests require the test database to be running for integration and API tests:

```bash
docker compose -f docker-compose.test.yml up -d db_test
```

---

## Main API Endpoints

| Method | Endpoint                    | Description                                |
| ------ | --------------------------- | ------------------------------------------ |
| `POST` | `/api/v1/imports/csv`       | Upload a Binance CSV file                  |
| `POST` | `/api/v1/process/{job_id}`  | Run FIFO processing on an import job       |
| `GET`  | `/api/v1/jobs`              | List all import jobs                       |
| `GET`  | `/api/v1/jobs/{job_id}`     | Get job status and row counts              |
| `GET`  | `/api/v1/results/{job_id}`  | Get FIFO results for a processed job       |
| `GET`  | `/api/v1/portfolio/summary` | Aggregated P&L and positions per asset     |
| `GET`  | `/health`                   | Liveness check                             |
| `GET`  | `/ready`                    | Readiness check (verifies DB connectivity) |

Full interactive documentation available at `http://localhost:8000/docs` when the app is running.

---

## Project Documentation

| Document                                     | Purpose                                                  |
| -------------------------------------------- | -------------------------------------------------------- |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layer design, data flows, DB schema, technical decisions |
| [docs/ROADMAP.md](docs/ROADMAP.md)           | Phased delivery plan with exit criteria per phase        |
| [docs/MVP_SCOPE.md](docs/MVP_SCOPE.md)       | Exact MVP scope — what's in, what's out, and why         |
| [docs/CHECKLIST.md](docs/CHECKLIST.md)       | Granular task checklist to track progress phase by phase |
| [docs/BACKLOG.md](docs/BACKLOG.md)           | Epics, stories, and acceptance criteria                  |
| [docs/STATUS.md](docs/STATUS.md)             | Current project state — updated after every session      |
| [docs/NEXT_STEP.md](docs/NEXT_STEP.md)       | The single next task to execute                          |
| [docs/RUNBOOK.md](docs/RUNBOOK.md)           | How to run, test, migrate, and debug locally             |
| [docs/ADR/](docs/ADR/)                       | Architecture Decision Records for key technical choices  |

---

## Demo Data

Sample CSV files are available in [`data/sample/`](data/sample/) for testing and demonstration purposes.

| File                                 | Description                                    |
| ------------------------------------ | ---------------------------------------------- |
| `binance_spot_trades_valid.csv`      | 10 clean transactions across BTC, ETH, and BNB |
| `binance_spot_trades_edge_cases.csv` | 9 rows covering validation edge cases          |

```bash
# Upload the sample file after starting the API
curl -X POST http://localhost:8000/api/v1/imports/csv \
  -F "file=@data/sample/binance_spot_trades_valid.csv"
```

→ See [data/sample/README.md](data/sample/README.md) for details.

---

## Security Notice

> This project is designed for portfolio demonstration. All sample data is **entirely fictional** — no real transaction history, wallet addresses, or personal financial data is included in this repository.
>
> Credentials and secrets are managed via environment variables and are never committed to the repository. See `.env.example` for the full list of required variables.
