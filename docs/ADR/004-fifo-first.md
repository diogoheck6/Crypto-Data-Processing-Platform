# ADR 004 — Implement FIFO as the First Cost Basis Method

**Status:** Accepted  
**Date:** 2026-04-15

---

## Context

Cost basis calculation is the core business problem of the platform. Multiple methods exist:

- **FIFO (First In, First Out):** The oldest purchased lots are consumed first on a sell event
- **LIFO (Last In, First Out):** The most recently purchased lots are consumed first
- **Weighted Average Cost:** All lots are averaged; each sell uses the current average cost

The system must choose one method to implement first. It must be extensible to support others later.

---

## Decision

Implement **FIFO** as the first and only cost basis method in the MVP. Other methods are deferred to Phase 9.

The `CostBasisCalculator` domain service will receive a `CostBasisMethod` value object as a parameter, but only FIFO logic will be implemented initially.

---

## Consequences

**Positive:**

- FIFO is the most widely used cost basis method globally and is required or preferred by tax authorities in many jurisdictions
- It has a clear, deterministic algorithm: maintain a FIFO queue per asset; consume from the front on each sell event. There is no ambiguity in the calculation.
- It is the simplest correct method to implement and test — test cases can be written with exact expected values and verified by hand
- The `CostBasisMethod` enum in the domain model makes the interface extensible: adding `WEIGHTED_AVERAGE` in Phase 9 requires only a new implementation of the same interface, no structural changes

**Negative:**

- FIFO may not be the preferred method for all users (some prefer weighted average for tax purposes)
- Users cannot choose their method until Phase 9

**Neutral:**

- LIFO is not planned — it is less common internationally and adds complexity without proportional value for this portfolio project
- Weighted average will be implemented in Phase 9 as an alternative strategy using the same `CostBasisCalculator` interface
