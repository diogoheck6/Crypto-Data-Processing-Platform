"""IJobRepository — abstract port for ProcessingJob persistence.

Any class that stores or retrieves ProcessingJob objects must implement this
interface. The domain depends only on this ABC; infrastructure provides the
concrete PostgreSQL implementation in Phase 3.

Why these four methods?
- save             : called once when a CSV upload creates a new job.
- update_status    : called multiple times as the pipeline advances the job
                     through its lifecycle (imported → processing → processed/failed).
                     Updating only the status avoids loading and re-saving the full
                     job object on every state transition.
- find_by_id       : used by the API to return a single job's status to the caller.
- find_all         : used by the API to list all jobs (GET /api/v1/jobs).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.processing_job import ProcessingJob
from src.domain.value_objects.job_status import JobStatus


class IJobRepository(ABC):

    @abstractmethod
    def save(self, job: ProcessingJob) -> None:
        """Persist a new ProcessingJob."""

    @abstractmethod
    def update_status(self, job_id: UUID, status: JobStatus) -> None:
        """Update the status of an existing job.

        Raises:
            ValueError: if no job with the given id exists.
        """

    @abstractmethod
    def find_by_id(self, job_id: UUID) -> ProcessingJob | None:
        """Return the job with the given id, or None if it does not exist."""

    @abstractmethod
    def find_all(self) -> list[ProcessingJob]:
        """Return all jobs, ordered by created_at descending."""
