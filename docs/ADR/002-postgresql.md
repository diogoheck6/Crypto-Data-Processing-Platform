# ADR 002 — Use PostgreSQL as the Primary Database

**Status:** Accepted  
**Date:** 2026-04-15

---

## Context

The system processes financial transaction data where correctness is non-negotiable. The database must:

- Provide ACID guarantees for all writes
- Store financial amounts with high decimal precision
- Support auditability (store raw payloads alongside normalized data)
- Have strong tooling for migrations and schema management
- Be available as a managed service on major cloud providers

---

## Decision

Use **PostgreSQL 16** as the primary database.

---

## Consequences

**Positive:**

- Full ACID compliance ensures no partial writes — critical for financial data where a failed processing job must not leave orphaned records
- `NUMERIC(28, 18)` columns support the precision required for crypto amounts without floating-point rounding errors
- `JSONB` columns for `raw_payload` and `result_payload` allow auditability and future schema evolution without requiring migrations for every field addition
- Alembic + SQLAlchemy have first-class PostgreSQL support
- Available as a managed service on Azure (Azure Database for PostgreSQL), which is the target cloud for Phase 8

**Negative:**

- Heavier than SQLite for local development — mitigated entirely by Docker Compose
- Requires migration management — handled by Alembic

**Neutral:**

- NoSQL alternatives (MongoDB, DynamoDB) were not considered — the relational model with foreign keys between `processing_jobs → transactions → processing_results` is the natural fit for this domain
