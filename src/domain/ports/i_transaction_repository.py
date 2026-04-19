"""ITransactionRepository — abstract port for transaction persistence.

Any class that stores or retrieves Transaction objects must implement this
interface. The domain layer depends only on this ABC; the infrastructure layer
provides the concrete PostgreSQL (or in-memory test) implementation.

Why three methods?
- save_batch      : the normalizer produces many transactions at once; batch insert
                    is the natural unit of work for a single CSV file.
- find_by_job_id  : the FIFO calculator loads all transactions for one job to process.
- exists_by_external_id : the validator uses this to detect duplicates across imports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.transaction import Transaction


class ITransactionRepository(ABC):

    @abstractmethod
    def save_batch(self, transactions: list[Transaction]) -> None:
        """Persist a list of Transaction objects.

        Implementations must be idempotent on the external_id field —
        inserting a transaction that already exists should be a no-op or
        raise a domain-level duplicate error, not a raw DB error.
        """

    @abstractmethod
    def find_by_job_id(self, job_id: UUID) -> list[Transaction]:
        """Return all transactions belonging to a given job, ordered by occurred_at."""

    @abstractmethod
    def exists_by_external_id(self, external_id: str, source: str) -> bool:
        """Return True if a transaction with this external_id + source already exists."""
