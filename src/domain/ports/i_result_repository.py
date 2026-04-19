"""IResultRepository — abstract port for ProcessingResult persistence.

Any class that stores or retrieves ProcessingResult objects must implement
this interface. Infrastructure provides the concrete implementation in Phase 3.

Why only two methods?
- save_batch      : the FIFO calculator produces one result per asset per job;
                    they are all written in a single unit of work after processing
                    completes.
- find_by_job_id  : the API uses this to return the full result set for a job
                    (GET /api/v1/results/{job_id}).

There is no update method — results are write-once. If a job is re-processed,
the use case deletes the old results and writes a fresh batch (handled at the
use-case level, not here).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.processing_result import ProcessingResult


class IResultRepository(ABC):

    @abstractmethod
    def save_batch(self, results: list[ProcessingResult]) -> None:
        """Persist a list of ProcessingResult objects for a single job."""

    @abstractmethod
    def find_by_job_id(self, job_id: UUID) -> list[ProcessingResult]:
        """Return all results for the given job, ordered by asset symbol."""
