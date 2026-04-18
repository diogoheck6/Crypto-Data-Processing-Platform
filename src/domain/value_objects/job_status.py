"""JobStatus — lifecycle states for a ProcessingJob.

Transitions (enforced by use cases, not by this enum):
    PENDING → IMPORTED → PROCESSING → PROCESSED
                                    ↘ FAILED
"""

from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    IMPORTED = "imported"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
