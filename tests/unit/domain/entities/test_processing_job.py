from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.domain.entities.processing_job import ProcessingJob
from src.domain.value_objects.job_status import JobStatus

# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------


def make_job(**overrides) -> ProcessingJob:
    defaults = dict(
        source_type="binance_csv",
        input_filename="trades_2024.csv",
    )
    return ProcessingJob(**{**defaults, **overrides})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestProcessingJobCreation:
    """Default values are sensible; required fields must be supplied."""

    def test_id_is_uuid(self):
        job = make_job()
        assert isinstance(job.id, UUID)

    def test_each_instance_gets_unique_id(self):
        j1 = make_job()
        j2 = make_job()
        assert j1.id != j2.id

    def test_default_status_is_peding(self):
        job = make_job()
        assert job.status == JobStatus.PENDING

    def test_row_counts_default_to_zero(self):
        job = make_job()
        assert job.total_rows == 0
        assert job.valid_rows == 0
        assert job.error_rows == 0

    def test_finished_at_defaults_to_none(self):
        job = make_job()
        assert job.finished_at is None

    def test_error_message_defaults_to_none(self):
        job = make_job()
        assert job.error_message is None

    def test_started_at_is_timezone_aware(self):
        job = make_job()
        assert job.started_at.tzinfo is not None

    def test_created_at_is_timezone_aware(self):
        job = make_job()
        assert job.created_at.tzinfo is not None

    def test_source_type_is_stored_correctly(self):
        job = make_job(source_type="kraken_csv")
        assert job.source_type == "kraken_csv"

    def test_input_filename_is_stored_correctly(self):
        job = make_job(input_filename="my_file.csv")
        assert job.input_filename == "my_file.csv"


class TestProcessingJobIdentity:
    """Identity is by id — two jobs with the same id are equal."""

    def test_two_jobs_with_same_id_are_equal(self):
        shared_id = uuid4()
        j1 = make_job(id=shared_id)
        j2 = make_job(id=shared_id)
        assert j1 == j2

    def test_two_jobs_with_different_ids_are_not_equal(self):
        j1 = make_job()
        j2 = make_job()
        assert j1 != j2

    def test_job_is_not_equal_non_job(self):
        job = make_job()
        assert job.__eq__("not a job") is NotImplemented

    def test_job_is_hashable(self):
        job = make_job()
        assert isinstance(hash(job), int)

    def test_same_job_deduplicates_in_set(self):
        shared_id = uuid4()
        j1 = make_job(id=shared_id)
        j2 = make_job(id=shared_id)
        assert len({j1, j2}) == 1


class TestProcessingJobMutability:
    """Status and row counts are mutated in place as the job progresses."""

    def test_status_can_be_updated(self):
        job = make_job()
        job.status = JobStatus.IMPORTED
        assert job.status == JobStatus.IMPORTED

    def test_row_counts_can_be_updated(self):
        job = make_job()
        job.total_rows = 100
        job.valid_rows = 95
        job.error_rows = 5
        assert job.total_rows == 100
        assert job.valid_rows == 95
        assert job.error_rows == 5

    def test_finished_at_can_be_set(self):
        job = make_job()
        now = datetime.now(tz=UTC)
        job.finished_at = now
        assert job.finished_at == now

    def test_error_message_can_be_set(self):
        job = make_job()
        job.error_message = "Something went wrong"
        assert job.error_message == "Something went wrong"
