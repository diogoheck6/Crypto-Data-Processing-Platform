# Contributing — Commit Strategy

> Simple, consistent, practical. One commit per checklist step (or logical group of steps).

---

## Commit Message Format

```
<type>(<scope>): <short summary>
```

- **type** — what kind of change (see table below)
- **scope** — what part of the project was touched (optional but helpful)
- **summary** — imperative mood, lowercase, no period, ≤72 chars

### Types

| Type       | When to use                                                            |
| ---------- | ---------------------------------------------------------------------- |
| `feat`     | New working capability (new endpoint, new domain rule, new parser)     |
| `fix`      | Bug fix or correction to broken behavior                               |
| `test`     | Adding or updating tests — no production code change                   |
| `refactor` | Internal restructuring with no behavior change                         |
| `chore`    | Tooling, config, dependencies, CI, Docker, Makefile, `.gitignore`      |
| `docs`     | Documentation only — README, ADR, RUNBOOK, CHECKLIST, inline docstring |

> **No `feat` without a test.** If you can't add at least one test, it's `chore` or `refactor`.

---

## When to Commit

**Rule: one commit per completed checklist step** (or one coherent group of steps from the same category).

Do not accumulate work across multiple checklist sections before committing. Small commits mean:

- Easy to revert a single step
- Clear history that mirrors the CHECKLIST.md
- Each commit on `main` is a verified, passing state

```
Complete checklist step
    → run lint + tests
        → commit
            → move to next step
```

---

## Phase 0 Examples

```bash
# Repository structure created
git commit -m "chore(scaffold): create src/ and tests/ package tree"

# pyproject.toml + dependencies
git commit -m "chore(deps): add pyproject.toml with pinned dependencies"

# Docker setup
git commit -m "chore(docker): add Dockerfile, docker-compose.yml and .test.yml"

# Tooling
git commit -m "chore(tooling): add pre-commit hooks — ruff, black, mypy, bandit"

# Config module
git commit -m "feat(config): add Settings class via pydantic-settings"

# Health endpoint
git commit -m "feat(api): add /health endpoint and app factory in main.py"

# Makefile + .gitignore
git commit -m "chore(devops): add Makefile and .gitignore"

# README
git commit -m "docs(readme): add project overview, stack and run instructions"

# Phase 0 complete
git commit -m "chore(phase-0): verify scaffold — pip install, pre-commit, pytest all pass"
```

---

## Phase 1 Examples

```bash
# Value objects
git commit -m "feat(domain): add Money value object with Decimal validation"
git commit -m "test(domain): add unit tests for Money — valid, negative, zero"

git commit -m "feat(domain): add Quantity, AssetSymbol value objects"
git commit -m "test(domain): add unit tests for Quantity and AssetSymbol"

git commit -m "feat(domain): add TransactionType and CostBasisMethod enums"
git commit -m "test(domain): add unit tests for TransactionType enum members"

# Entities
git commit -m "feat(domain): add Transaction and AssetPosition entities"
git commit -m "feat(domain): add ProcessingJob and ProcessingResult entities"

# Ports
git commit -m "feat(domain): add repository port interfaces (ABC)"

# Domain services
git commit -m "feat(domain): add TransactionNormalizer and TransactionValidator"
git commit -m "test(domain): add unit tests for TransactionNormalizer"

git commit -m "feat(domain): add CostBasisCalculator — FIFO engine"
git commit -m "test(domain): add FIFO tests — basic, duplicate, insufficient qty"

git commit -m "feat(domain): add ProfitLossCalculator"
git commit -m "test(domain): add P&L calculation tests"

# Phase 1 complete
git commit -m "feat(phase-1): domain layer complete — all unit tests passing at 100% coverage"
```

---

## Later Phases — Pattern

```bash
# Phase 2 — CSV Parser
git commit -m "feat(infra): add BinanceCsvParser — valid rows and parse errors"
git commit -m "test(parsers): add unit tests for BinanceCsvParser edge cases"

# Phase 3 — Persistence
git commit -m "feat(infra): add SQLAlchemy ORM models for all 4 tables"
git commit -m "chore(db): init Alembic and add first migration"
git commit -m "feat(infra): add PostgreSQL repository implementations"
git commit -m "test(integration): add repository integration tests with real DB"

# Phase 4 — Use Cases
git commit -m "feat(app): add ImportTransactions use case"
git commit -m "test(integration): add ImportTransactions integration test"
git commit -m "feat(app): add ProcessTransactions use case — FIFO end-to-end"

# Phase 5 — API
git commit -m "feat(api): add POST /api/v1/imports/csv endpoint"
git commit -m "feat(api): add GET /api/v1/jobs and GET /api/v1/jobs/{id}"
git commit -m "test(api): add API tests for import and job endpoints"

# Phase 5.5 — CI
git commit -m "chore(ci): add GitHub Actions — lint, unit, integration, build stages"
git commit -m "chore(ci): add dependabot.yml for weekly pip updates"

# Phase 8 — Deploy
git commit -m "chore(cd): add deploy-staging workflow with alembic pre-deploy step"
git commit -m "chore(cd): add deploy-prod workflow with manual approval gate"

# Hotfix example
git commit -m "fix(domain): correct FIFO sell quantity when partial lot is consumed"
git commit -m "test(domain): add regression test for partial FIFO lot edge case"
```

---

## Branch Strategy

```
main          — protected; always deployable; direct push blocked
feature/*     — all work happens here; PR required to merge
fix/*         — hotfixes; PR required
```

```bash
# Start a new phase or feature
git checkout -b feature/phase-1-domain

# Work → commit → work → commit (one per checklist step)
# When phase is done:
git push origin feature/phase-1-domain
# Open PR → CI must pass → merge to main
```

> Keep `feature/*` branches short-lived. One branch per phase or per epic is enough.
