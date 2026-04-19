import pytest

from src.domain.ports.i_transaction_repository import ITransactionRepository


class TestITransactionRepositoryIsAbstract:
    """ITransactionRepository cannot be instantiated — it is a pure interface."""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            ITransactionRepository()  # type: ignore[abstract]

    def test_concrete_class_missing_all_methods_cannot_instantiate(self):
        class Incomplete(ITransactionRepository):
            pass

        with pytest.raises(TypeError):
            Incomplete()

    def test_concrete_class_missing_one_method_cannot_instantiate(self):
        class PartialImpl(ITransactionRepository):
            def save_batch(self, transactions):
                pass

            def find_by_job_id(self, job_id):
                pass

            # exists_by_external_id intentionally missing

        with pytest.raises(TypeError):
            PartialImpl()

    def test_full_implementation_can_be_instantiated(self):
        class FakeTransactionRepository(ITransactionRepository):
            def save_batch(self, transactions):
                pass

            def find_by_job_id(self, job_id):
                return []

            def exists_by_external_id(self, external_id, source):
                return False

        repo = FakeTransactionRepository()
        assert isinstance(repo, ITransactionRepository)

    def test_abstract_method_names_are_correct(self):
        expected = {"save_batch", "find_by_job_id", "exists_by_external_id"}
        assert ITransactionRepository.__abstractmethods__ == expected
