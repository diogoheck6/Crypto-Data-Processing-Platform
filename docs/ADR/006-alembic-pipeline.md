# ADR 006 — Run Alembic Migrations as a Pipeline Step, Not at App Startup

**Status:** Accepted (relevant from Phase 8)  
**Date:** 2026-04-15

---

## Context

Database migrations must run before the new version of the application starts serving traffic. There are two common approaches:

**Option A — Run migrations at container startup:** The app container's entrypoint runs `alembic upgrade head` before starting `uvicorn`. Simple to implement, works in single-container setups.

**Option B — Run migrations as a dedicated pipeline step:** A separate CI/CD job runs `alembic upgrade head` against the target database before the new container is deployed.

For local development, Option A is perfectly acceptable. For production deployments in Phase 8, the choice matters.

---

## Decision

**Use Option A (migrations at startup) for local development and Docker Compose.**  
**Use Option B (migrations as a pipeline step) for staging and production deployments.**

The CD pipeline (`deploy-staging.yml`, `deploy-prod.yml`) will include a pre-deploy migration job that runs `alembic upgrade head` before the new container version is swapped in.

---

## Consequences

**Positive:**

- Eliminates the startup race condition: in a deployment with multiple replicas, every container trying to run migrations simultaneously can cause conflicts. A single pipeline job with a schema lock runs exactly once.
- Migrations can fail fast and stop the deployment before any traffic is affected — the old version keeps running
- Rollback is clean: if migration fails, the old container is still running on the old schema
- The separation makes the migration history visible in the CI/CD audit log, not buried in container startup logs

**Negative:**

- Slightly more complex CD pipeline setup
- The application container must not assume the schema is migrated on startup — it will fail with a database error if deployed without running the pipeline migration step first

**Neutral:**

- For local development (`docker compose up`), the `api` entrypoint will still run `alembic upgrade head` automatically for convenience — this is acceptable because there is only one container and no race condition
- This is the standard pattern used in production financial and SaaS systems
