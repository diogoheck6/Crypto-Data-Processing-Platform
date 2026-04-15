# ADR 001 — Use FastAPI as the API Framework

**Status:** Accepted  
**Date:** 2026-04-15

---

## Context

The project needs an HTTP API framework for Python. The main candidates were Flask, Django REST Framework, and FastAPI.

The system has specific requirements:

- Strong request/response type safety
- Automatic API documentation (OpenAPI)
- Integration with Pydantic for schema validation
- Good ergonomics for async operations (queue, future streaming)
- Relevant in the current job market for Python backend roles

---

## Decision

Use **FastAPI**.

---

## Consequences

**Positive:**

- Pydantic models at the API boundary give us typed, validated schemas with zero boilerplate
- OpenAPI docs are generated automatically from the code — no separate spec to maintain
- FastAPI's `Depends` system maps cleanly to our dependency injection approach for use cases and repositories
- Strong typing throughout means Mypy can catch schema mismatches at the API layer
- Industry-standard choice for modern Python APIs — directly relevant for the target job market

**Negative:**

- More opinionated than Flask — but that is a deliberate benefit here, not a drawback
- Async error handling requires care when mixing with synchronous SQLAlchemy (managed by using sync sessions in Phase 1–5)

**Neutral:**

- Django was not suitable — it brings ORM coupling, admin panel, and conventions that conflict with Clean Architecture
- Flask was not suitable — no built-in typing or validation; would require significant boilerplate to reach the same quality bar
