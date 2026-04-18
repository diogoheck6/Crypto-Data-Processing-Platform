"""ProcessingJob — tracks one import/processing session end-to-end.

A job is created when a CSV file is uploaded. Its status advances as the
pipeline runs. The entity only holds state; transitions are driven by use cases.

Status lifecycle:
    PENDING → IMPORTED → PROCESSING → PROCESSED
                                    ↘ FAILED

Design notes:
- Regular (non-frozen) dataclass — status and row counts are mutated in place.
- Identity by UUID id — same pattern as Transaction.
- finished_at and error_message are None until the job concludes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.domain.value_objects.job_status import JobStatus


@dataclass
class ProcessingJob:
    source_type: str
    input_filename: str

    id: UUID = field(default_factory=uuid4)
    status: JobStatus = JobStatus.PENDING

    total_rows: int = 0
    valid_rows: int = 0
    error_rows: int = 0

    started_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    finished_at: datetime | None = None
    error_message: str | None = None

    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ProcessingJob):
            return self.id == other.id
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.id)
