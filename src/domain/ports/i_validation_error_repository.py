"""IValidationErrorRepository — abstract port for ValidationError persistence.

Any class that stores or retrieves ValidationError objects must implement
this interface. Infrastructure provides the concrete implementation in Phase 3.

Why only two methods?
- save_batch      : the validator produces many errors in one pass; they are
                    all written together after validation completes.
- find_by_job_id  : the API uses this to return the error report for a job
                    (GET /api/v1/jobs/{job_id}/errors).

ValidationErrors are write-once — there is no update or delete at this level.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.validation_error import ValidationError


class IValidationErrorRepository(ABC):

    @abstractmethod
    def save_batch(self, errors: list[ValidationError]) -> None:
        """Persist a list of ValidationError objects for a single job."""

    @abstractmethod
    def find_by_job_id(self, job_id: UUID) -> list[ValidationError]:
        """Return all validation errors for the given job, ordered by row_number."""
