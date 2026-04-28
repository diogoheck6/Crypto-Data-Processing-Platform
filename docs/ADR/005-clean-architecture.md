# ADR 005 — Adopt Clean Architecture with Hexagonal Inspiration

**Status:** Accepted  
**Date:** 2026-04-15

---

## Context

The core challenge of this system is not HTTP or database — it is the business logic: FIFO calculation, transaction validation, normalization, and P&L computation. These rules are complex enough to require exhaustive testing and will evolve as the product matures.

The question is: how do we structure the code so that:

1. Business logic can be tested without a database or HTTP server?
2. Infrastructure (PostgreSQL, Redis, CSV files) can be swapped without touching business rules?
3. The codebase remains navigable as it grows?

Two common patterns were considered: a layered "MVC-style" approach and Clean Architecture / Hexagonal Architecture.

---

## Decision

Adopt **Clean Architecture** for layer separation, with **hexagonal (ports & adapters)** inspiration for defining the boundary between the domain and external systems.

The practical interpretation:

- `src/domain/` — pure Python business logic, no external imports
- `src/application/` — use cases that orchestrate domain services and call repository ports
- `src/infra/` — concrete implementations of ports (PostgreSQL repos, CSV parser)
- `src/api/` — FastAPI adapter that translates HTTP ↔ use cases

The one-way dependency rule: `domain ← application ← infrastructure ← api`. Never reversed.

---

## Consequences

**Positive:**

- The entire domain layer can be unit-tested with zero infrastructure setup — no Docker, no database, no HTTP — tests run in milliseconds
- Repository ports (abstract interfaces) allow integration tests to use real implementations while unit tests use simple in-memory fakes
- The domain never breaks because of a database schema change or a FastAPI version upgrade
- The architecture is immediately recognizable to senior engineers and makes a strong impression in portfolio and interview contexts
- Adding a new data source (e.g., Kraken CSV, Binance API) means writing a new adapter in `src/infra/parsers/` — no domain changes required

**Negative:**

- More files and more indirection than a simple layered structure
- The explicit ORM ↔ domain entity mapping in repositories is boilerplate, but it is the correct trade-off: it prevents SQLAlchemy from leaking into the domain

**Neutral:**

- This is not a strict academic implementation of either pattern. Pragmatism takes precedence over theoretical purity.
- The frontend (Next.js) in Phase 7 is a separate application and does not follow these layers — it consumes the API as an external client
