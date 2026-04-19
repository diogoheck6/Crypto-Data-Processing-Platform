import pytest

from src.domain.ports.i_result_repository import IResultRepository


class TestIResultRepositoryIsAbstract:
    """IResultRepository cannot be instantiated — it is a pure interface."""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            IResultRepository()  # type: ignore[abstract]

    def test_concrete_class_missing_all_methods_cannot_instantiate(self):
        class Incomplete(IResultRepository):
            pass

        with pytest.raises(TypeError):
            Incomplete()

    def test_concrete_class_missing_one_method_cannot_instantiate(self):
        class PartialImpl(IResultRepository):
            def save_batch(self, results):
                pass

            # find_by_job_id intentionally missing

        with pytest.raises(TypeError):
            PartialImpl()

    def test_full_implementation_can_be_instantiated(self):
        class FakeResultRepository(IResultRepository):
            def save_batch(self, results):
                pass

            def find_by_job_id(self, job_id):
                return []

        repo = FakeResultRepository()
        assert isinstance(repo, IResultRepository)

    def test_abstract_method_names_are_correct(self):
        expected = {"save_batch", "find_by_job_id"}
        assert IResultRepository.__abstractmethods__ == expected
