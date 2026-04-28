# Status — Crypto Data Processing Platform

> This file is the single source of truth for the current project state.
> Update this file at the end of every work session.
> Never assume something is done if it is not recorded here.

---

## Current Phase

**Phase 1 — Domain Layer**

---

## Summary

| Area                                           | Status         |
| ---------------------------------------------- | -------------- |
| Repository structure                           | ✅ Done        |
| Python tooling (Ruff, Black, Mypy, pre-commit) | ✅ Done        |
| Docker (app + PostgreSQL)                      | ✅ Done        |
| Domain layer                                   | 🟡 In Progress |
| CSV parser                                     | 🔴 Not started |
| Persistence (PostgreSQL + repositories)        | 🔴 Not started |
| Use cases                                      | 🔴 Not started |
| API (FastAPI)                                  | 🔴 Not started |
| Async queue                                    | 🔴 Not started |
| Frontend                                       | 🔴 Not started |
| Cloud deploy                                   | 🔴 Not started |

---

## Done

- [x] Project documentation created: `MVP_SCOPE.md`, `ROADMAP.md`, `CHECKLIST.md`, `BACKLOG.md`, `STATUS.md`, `NEXT_STEP.md`, `ARCHITECTURE.md`
- [x] Architecture defined: Clean Architecture with hexagonal inspiration
- [x] Stack decided: Python 3.12 + FastAPI + PostgreSQL + Redis + Docker + Next.js
- [x] Domain model defined: entities, value objects, ports, services
- [x] MVP scope frozen: FIFO + CSV import + REST API + tests
- [x] **Phase 0 complete (2026-04-15)**
  - [x] Full `src/` + `tests/` package tree created
  - [x] `pyproject.toml` with all pinned dependencies
  - [x] `src/config.py` via pydantic-settings
  - [x] `src/api/main.py` — factory pattern, `GET /health` → `{"status": "ok"}`
  - [x] `Dockerfile` (python:3.12-slim, non-root user)
  - [x] `docker-compose.yml` + `docker-compose.test.yml`
  - [x] `.pre-commit-config.yaml` — ruff, black, mypy, bandit
  - [x] `Makefile`, `.gitignore`, `.env.example`, `README.md`
  - [x] `pip install -e ".[dev]"` passes
  - [x] `pre-commit run --all-files` passes clean
  - [x] `pytest` runs (0 collected, no errors)
  - [x] `docker compose up --build` starts cleanly
  - [x] `GET /health` returns `{"status": "ok"}`

---

## In Progress

- **Phase 1 — Domain Layer**: value objects ✅ + all 4 entities ✅ (122 tests, 100% domain coverage). Now on `feature/phase-1-ports`. Next: repository ports (4 ABCs).

---

## Next Step

→ See [NEXT_STEP.md](./NEXT_STEP.md) for the detailed task for the next session.

**Upcoming:** Implement repository ports — `ITransactionRepository`, `IJobRepository`, `IResultRepository`, `IValidationErrorRepository` (Phase 1, sub-step 1.6).

---

## Blockers

None.

---

## Recent Decisions

| Date       | Decision                                 | Reason                                                              |
| ---------- | ---------------------------------------- | ------------------------------------------------------------------- |
| 2026-04-15 | FIFO only for MVP cost basis             | Simplest correct method; weighted average added in Phase 9          |
| 2026-04-15 | Synchronous processing in MVP            | No need for async queue until API is stable (Phase 5 gate)          |
| 2026-04-15 | No authentication in MVP                 | Single-user local use; auth added before cloud deploy               |
| 2026-04-15 | PostgreSQL as primary DB                 | ACID guarantees for financial data; JSONB for raw payloads          |
| 2026-04-15 | Separate ORM models from domain entities | No SQLAlchemy leakage into domain; enables full unit testing        |
| 2026-04-15 | UUID for all primary keys                | Avoids sequential ID leakage; consistent with future event-sourcing |

---

## Phase Progress

| Phase | Description        | Status         |
| ----- | ------------------ | -------------- |
| 0     | Project Foundation | ✅ Done        |
| 1     | Domain Layer       | 🟡 In Progress |
| 2     | CSV Parser         | 🔴 Not Started |
| 3     | Persistence        | 🔴 Not Started |
| 4     | Use Cases          | 🔴 Not Started |
| 5     | API Layer          | 🔴 Not Started |
| 6     | Async Queue        | 🔴 Not Started |
| 7     | Frontend           | 🔴 Not Started |
| 8     | Production & Cloud | 🔴 Not Started |
| 9     | Premium Features   | 🔴 Not Started |
