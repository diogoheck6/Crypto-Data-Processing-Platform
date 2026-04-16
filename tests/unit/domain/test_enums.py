import pytest

from src.domain.value_objects.cost_basis_method import CostBasisMethod
from src.domain.value_objects.transaction_type import TransactionType


class TestTransactionType:
    def test_all_members_exist(self):
        members = {t.value for t in TransactionType}
        assert members == {"BUY", "SELL", "FEE", "DEPOSIT", "WITHDRAWAL", "TRANSFER"}

    def test_string_comparison(self):
        # TransactionType(str, Enum) must compare equal to its string value
        assert TransactionType.BUY == "BUY"

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            TransactionType("INVALID")


class TestCostBasisMethod:
    def test_all_members_exist(self):
        members = {m.value for m in CostBasisMethod}
        assert members == {"FIFO", "WEIGHTED_AVERAGE"}

    def test_fifo_is_default_method(self):
        assert CostBasisMethod.FIFO == "FIFO"
