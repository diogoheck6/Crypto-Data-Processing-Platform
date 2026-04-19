"""ValidationError — records one failed validation rule for a single row.

Created by TransactionValidator when a row fails a business rule.
Persisted so the user can review which rows were rejected and why,
without having to re-upload the file.

Design notes:
- Regular (non-frozen) dataclass for consistency with other entities.
- Identity by UUID id.
- field_name is None for row-level errors (e.g. duplicate row) vs
  field-level errors (e.g. invalid quantity format).
- raw_row stores the original dict for full auditability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class ValidationError:
    job_id: UUID
    row_number: int
    error_code: str
    message: str

    id: UUID = field(default_factory=uuid4)
    field_name: str | None = None
    raw_row: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ValidationError):
            return self.id == other.id
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.id)
