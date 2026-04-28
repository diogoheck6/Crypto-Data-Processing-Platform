# ADR 003 — Use Redis + RQ for Async Job Queue

**Status:** Accepted (deferred to Phase 6)  
**Date:** 2026-04-15

---

## Context

Processing large CSV files synchronously within an HTTP request creates two problems:

1. The request can time out for large files (tens of thousands of rows)
2. The client has no way to track progress

A task queue decouples the upload (fast) from the processing (slow), allowing the API to return a `job_id` immediately and letting the client poll for results.

The main queue options evaluated: Celery + Redis, RQ + Redis, Dramatiq + Redis.

---

## Decision

Use **Redis as the broker** and **RQ (Redis Queue) as the task queue library**.

Celery is planned as a future upgrade path if the complexity warrants it.

---

## Consequences

**Positive:**

- RQ has a minimal API — a background job is just a Python function call; no task class, no serialization decorator required
- Redis is already planned in the stack for caching, so adding RQ has no new infrastructure cost
- RQ worker is a single process, trivial to containerize and add to `docker-compose.yml`
- The `rq-dashboard` web UI provides job visibility with no extra work
- Easy to test: jobs can be executed synchronously in tests by calling the underlying function directly

**Negative:**

- RQ does not support complex routing, chained workflows, or periodic tasks (cron) as natively as Celery
- If the system later needs scheduled tasks or multi-step pipelines, a migration to Celery would be required

**Neutral:**

- Dramatiq was considered — similar simplicity to RQ but less community adoption in the Python ecosystem
- Celery would be the right choice if the system needs: advanced retry strategies, task chaining, beat scheduler, or Flower monitoring — none of which are in scope for the current roadmap
- **Synchronous processing is used in Phase 1–5 (MVP)**. RQ is only introduced in Phase 6, after the API and domain are stable. This is a deliberate sequencing decision to avoid premature operational complexity.
