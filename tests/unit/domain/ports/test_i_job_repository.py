import pytest

from src.domain.ports.i_job_repository import IJobRepository


class TestIJobRepositoryIsAbstract:
    """IJobRepository cannot be instantiated — it is a pure interface."""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            IJobRepository()  # type: ignore[abstract]

    def test_concrete_class_missing_all_methods_cannot_instantiate(self):
        class Incomplete(IJobRepository):
            pass

        with pytest.raises(TypeError):
            Incomplete()

    def test_concrete_class_missing_one_method_cannot_instantiate(self):
        class PartialImpl(IJobRepository):
            def save(self, job):
                pass

            def update_status(self, job_id, status):
                pass

            def find_by_id(self, job_id):
                return None

            # find_all intentionally missing

        with pytest.raises(TypeError):
            PartialImpl()

    def test_full_implementation_can_be_instantiated(self):
        class FakeJobRepository(IJobRepository):
            def save(self, job):
                pass

            def update_status(self, job_id, status):
                pass

            def find_by_id(self, job_id):
                return None

            def find_all(self):
                return []

        repo = FakeJobRepository()
        assert isinstance(repo, IJobRepository)

    def test_abstract_method_names_are_correct(self):
        expected = {"save", "update_status", "find_by_id", "find_all"}
        assert IJobRepository.__abstractmethods__ == expected
