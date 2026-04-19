import pytest

from src.domain.ports.i_validation_error_repository import IValidationErrorRepository


class TestValidationErrorRepositoryIsAbstract:
    """IValidationErrorRepository cannot be instantiated — it is a pure interface."""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            IValidationErrorRepository()  # type: ignore[abstract]

    def test_concrete_class_missing_all_methods_cannot_instantiate(self):
        class Incomplete(IValidationErrorRepository):
            pass

        with pytest.raises(TypeError):
            Incomplete()

    def test_concrete_class_missing_one_method_cannot_instantiate(self):
        class PartialImpl(IValidationErrorRepository):
            def save_batch(self, errors):
                pass

            # find_by_job_id intentionally missing

        with pytest.raises(TypeError):
            PartialImpl()

    def test_full_implementation_can_be_instantiate(self):
        class FakeValidationErrorRepository(IValidationErrorRepository):
            def save_batch(self, errors):
                pass

            def find_by_job_id(self, job_id):
                return []

        repo = FakeValidationErrorRepository()
        assert isinstance(repo, IValidationErrorRepository)

    def test_abstract_method_names_are_correct(self):
        expected = {"save_batch", "find_by_job_id"}
        assert IValidationErrorRepository.__abstractmethods__ == expected
