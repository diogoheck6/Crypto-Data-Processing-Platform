# Next Step — Crypto Data Processing Platform

> This file defines exactly what to do in the next work session.
> Read this first. Do not start anything else before completing this task.
> Update this file (and STATUS.md + CHECKLIST.md) when the task is done.

---

## Current Phase

**Phase 1 — Domain Layer**

---

## Context

Phase 0 is complete. The scaffold is in place:

- Full `src/` + `tests/` package tree
- `pyproject.toml`, `.pre-commit-config.yaml`, `Makefile`, `Dockerfile`, `docker-compose.yml`
- `src/api/main.py` with `GET /health` returning `{"status": "ok"}`
- All tooling verified: pip install ✅ pre-commit ✅ pytest ✅ docker compose ✅

The codebase is now ready for business logic. Phase 1 builds the entire domain layer
in pure Python — no database, no HTTP, no external dependencies. It must be complete
and at 100% unit test coverage before Phase 2 begins.

---

## Task for This Session

**Phase 1 entities are fully done (122 tests, 100% domain coverage).
Now on `feature/phase-1-ports`. Next: implement the 4 repository port ABCs in `src/domain/ports/`, then proceed to domain services.**

---

## Why This Task Comes First

The domain is the heart of the system. Every other layer (infra, API, use cases) depends on it.
Building domain-first guarantees:

- Business rules are pure Python — testable without a database or server
- FIFO logic is verified in isolation before any persistence is added
- Ports (abstract interfaces) lock the contract that repositories must satisfy

---

## Step-by-Step Execution

### Step 1 — Value Objects

All are **frozen dataclasses** (`@dataclass(frozen=True)`). No Pydantic, no SQLAlchemy.

| File                                            | Class                                   | Rules                                           |
| ----------------------------------------------- | --------------------------------------- | ----------------------------------------------- |
| `src/domain/value_objects/money.py`             | `Money(amount: Decimal, currency: str)` | `amount > 0`; `currency` non-empty, uppercase   |
| `src/domain/value_objects/quantity.py`          | `Quantity(amount: Decimal)`             | `amount >= 0`                                   |
| `src/domain/value_objects/asset_symbol.py`      | `AssetSymbol(symbol: str)`              | non-empty, store as uppercase                   |
| `src/domain/value_objects/transaction_type.py`  | `TransactionType(Enum)`                 | `BUY, SELL, FEE, DEPOSIT, WITHDRAWAL, TRANSFER` |
| `src/domain/value_objects/cost_basis_method.py` | `CostBasisMethod(Enum)`                 | `FIFO, WEIGHTED_AVERAGE`                        |

### Step 2 — Unit Tests for Value Objects

Files in `tests/unit/domain/`:

- `test_money.py` — valid, negative raises, zero raises, equality, different currencies
- `test_quantity.py` — valid, negative raises, zero is valid
- `test_asset_symbol.py` — uppercase normalization, empty raises
- `test_transaction_type.py` — all 6 members present, invalid string raises

### Step 3 — Entities

Plain dataclasses (not frozen — entities have identity, not just value).

| File                                       | Class              | Notes                                                                                                 |
| ------------------------------------------ | ------------------ | ----------------------------------------------------------------------------------------------------- |
| `src/domain/entities/transaction.py`       | `Transaction`      | All columns from DB schema as fields; `transaction_type: TransactionType`                             |
| `src/domain/entities/asset_position.py`    | `AssetPosition`    | `asset: AssetSymbol`, `queue: deque[Transaction]` — FIFO queue holder                                 |
| `src/domain/entities/processing_job.py`    | `ProcessingJob`    | `id`, `status`, `source_type`, `input_filename`, `total_rows`, `valid_rows`, `error_rows`, timestamps |
| `src/domain/entities/processing_result.py` | `ProcessingResult` | `asset`, `realized_profit`, `total_cost_basis`, `remaining_quantity`, `remaining_cost_basis`          |

### Step 4 — Repository Ports

Abstract base classes in `src/domain/ports/`. Zero implementation — interface only.

| File                               | Interface                    | Methods                                                 |
| ---------------------------------- | ---------------------------- | ------------------------------------------------------- |
| `i_transaction_repository.py`      | `ITransactionRepository`     | `save_batch`, `find_by_job_id`, `exists_by_external_id` |
| `i_job_repository.py`              | `IJobRepository`             | `save`, `update_status`, `find_by_id`, `find_all`       |
| `i_result_repository.py`           | `IResultRepository`          | `save_batch`, `find_by_job_id`                          |
| `i_validation_error_repository.py` | `IValidationErrorRepository` | `save_batch`, `find_by_job_id`                          |

### Step 5 — Domain Services

Pure functions or stateless classes. No I/O.

| File                                            | Class                   | Responsibility                                                                          |
| ----------------------------------------------- | ----------------------- | --------------------------------------------------------------------------------------- |
| `src/domain/services/transaction_normalizer.py` | `TransactionNormalizer` | `normalize(raw: dict) -> Transaction`                                                   |
| `src/domain/services/transaction_validator.py`  | `TransactionValidator`  | `validate(t: Transaction) -> list[ValidationError]`                                     |
| `src/domain/services/cost_basis_calculator.py`  | `CostBasisCalculator`   | `calculate(transactions: list[Transaction]) -> list[ProcessingResult]` — FIFO per asset |
| `src/domain/services/profit_loss_calculator.py` | `ProfitLossCalculator`  | `calculate(fifo_output) -> ProcessingResult` — realized P&L                             |

### Step 6 — Unit Tests for Domain Services

Files in `tests/unit/domain/`:

- `test_transaction_normalizer.py` — valid dict, missing required field, unknown field ignored
- `test_transaction_validator.py` — passes, zero quantity fails, invalid date fails, duplicate detected
- `test_cost_basis_calculator.py` (all edge cases from MVP_SCOPE.md):
  - Single buy + single sell → correct P&L
  - Multiple buys at different prices + sell → FIFO order verified
  - Sell qty > total bought → error recorded, partial match
  - Sell with no prior buy → error recorded
  - Fee in same asset reduces cost basis
  - Fee in different asset does not affect cost basis
  - Out-of-order timestamps → sorted before processing
  - Transfer/deposit → no P&L generated
  - Duplicate transaction ID → rejected
  - Zero quantity → rejected
- `test_profit_loss_calculator.py` — correct P&L from FIFO output

---

## Definition of Done

All of the following must be true before closing Phase 1:

- [ ] All value objects implemented and tested
- [ ] All entities implemented
- [ ] All 4 repository port ABCs defined
- [ ] All 4 domain services implemented
- [ ] All 10 FIFO edge cases tested (see MVP_SCOPE.md)
- [ ] `pytest tests/unit/ --cov=src/domain --cov-report=term-missing` → **100% coverage**
- [ ] `pre-commit run --all-files` → clean
- [ ] No import of `fastapi`, `sqlalchemy`, `pydantic`, or any external library inside `src/domain/`

---

## Files to Create in This Session

```
src/domain/value_objects/
    money.py
    quantity.py
    asset_symbol.py
    transaction_type.py
    cost_basis_method.py

src/domain/entities/
    transaction.py
    asset_position.py
    processing_job.py
    processing_result.py

src/domain/ports/
    i_transaction_repository.py
    i_job_repository.py
    i_result_repository.py
    i_validation_error_repository.py

src/domain/services/
    transaction_normalizer.py
    transaction_validator.py
    cost_basis_calculator.py
    profit_loss_calculator.py

tests/unit/domain/
    test_money.py
    test_quantity.py
    test_asset_symbol.py
    test_transaction_type.py
    test_transaction_normalizer.py
    test_transaction_validator.py
    test_cost_basis_calculator.py
    test_profit_loss_calculator.py
```

---

## After This Task

When done, update:

1. **CHECKLIST.md** — mark all Phase 1 items as `[x]`
2. **STATUS.md** — mark Phase 1 as ✅ Done; set Phase 2 as 🟡 In Progress
3. **NEXT_STEP.md** — replace with Phase 2 task: _Implement BinanceCsvParser_

---

## Important Notes

- `src/domain/` must have **zero external dependencies**. Use only stdlib: `dataclasses`, `decimal`, `enum`, `collections`, `abc`, `uuid`, `datetime`.
- Raise `ValueError` for invalid value objects — not custom exceptions yet.
- `CostBasisCalculator` must sort transactions by `occurred_at` internally before processing.
- Keep each file focused. One class per file.
