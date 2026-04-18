from src.domain.value_objects.job_status import JobStatus


class TestJobStatusMembers:
    """All five lifecycle states must be present with the correct string values."""

    def test_pending_value(self):
        assert JobStatus.PENDING == "pending"

    def test_imported_value(self):
        assert JobStatus.IMPORTED == "imported"

    def test_processing_value(self):
        assert JobStatus.PROCESSING == "processing"

    def test_processed_value(self):
        assert JobStatus.PROCESSED == "processed"

    def test_failed_value(self):
        assert JobStatus.FAILED == "failed"

    def test_all_five_members_exist(self):
        names = {s.name for s in JobStatus}
        assert names == {"PENDING", "IMPORTED", "PROCESSING", "PROCESSED", "FAILED"}
