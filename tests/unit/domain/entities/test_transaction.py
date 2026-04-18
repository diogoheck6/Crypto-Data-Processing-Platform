from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.entities.transaction import Transaction
from src.domain.value_objects.asset_symbol import AssetSymbol
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.transaction_type import TransactionType


def make_transaction(**overrides) -> Transaction:
    """Factory helper — builds a valid Transaction with sensible defaults.

    Any field can be overridden via kwargs. Using a factory keeps tests
    short and makes it obvious what each test actually cares about.
    """
    defaults = dict(
        asset=AssetSymbol("BTC"),
        transaction_type=TransactionType.BUY,
        quantity=Quantity(Decimal("0.5")),
        unit_price=Decimal("30000"),
        total_value=Decimal("15000"),
        source="binance_csv",
        occurred_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
    )
    return Transaction(**{**defaults, **overrides})


class TestTransactionIdentity:
    def test_two_transactions_with_same_id_are_equal(self):
        shared_id = uuid4()
        t1 = make_transaction(id=shared_id)
        t2 = make_transaction(id=shared_id)
        assert t1 == t2

    def test_two_transactions_with_different_ids_are_not_equal(self):
        t1 = make_transaction()
        t2 = make_transaction()
        assert t1 != t2

    def test_transaction_is_not_equal_to_non_transaction(self):
        t = make_transaction()
        assert t != "not a transaction"
        assert t != 42

    def test_transaction_is_hashable(self):
        t1 = make_transaction()
        t2 = make_transaction()
        s = {t1, t2}
        assert len(s) == 2

    def test_same_transaction_in_set_deduplicates(self):
        shared_id = uuid4()
        t1 = make_transaction(id=shared_id)
        t2 = make_transaction(id=shared_id)
        s = {t1, t2}
        assert len(s) == 1


class TestTransactionDefaults:
    def test_id_is_uuid(self):
        t = make_transaction()
        assert isinstance(t.id, UUID)

    def test_job_id_is_uuid(self):
        t = make_transaction()
        assert isinstance(t.job_id, UUID)

    def test_each_instance_gets_unique_id_by_default(self):
        t1 = make_transaction()
        t2 = make_transaction()
        assert t1.id != t2.id

    def test_raw_payload_defaults_to_empty_dict(self):
        t = make_transaction()
        assert t.raw_payload == {}

    def test_fee_fields_default_to_none(self):
        t = make_transaction()
        assert t.fee_amount is None
        assert t.fee_asset is None

    def test_occurred_at_is_timezone_aware(self):
        t = make_transaction()
        assert t.occurred_at.tzinfo is not None

    def test_created_at_is_timezone_aware(self):
        t = make_transaction()
        assert t.created_at.tzinfo is not None

    def test_quantity_default_is_zero_sentinel(self):
        # Zero quantity is the dataclass default — it is NOT valid business data.
        # TransactionValidator will reject it. This test documents that the
        # default exists and is zero, not that zero is an acceptable trade.
        t = Transaction()
        assert t.quantity.is_zero()


class TestTransactionFields:
    def test_asset_is_stored_correctly(self):
        t = make_transaction(asset=AssetSymbol("ETH"))
        assert t.asset == AssetSymbol("ETH")

    def test_transaction_type_is_stored_correctly(self):
        t = make_transaction(transaction_type=TransactionType.SELL)
        assert t.transaction_type == TransactionType.SELL

    def test_quantity_is_stored_correctly(self):
        qty = Quantity(Decimal("1.5"))
        t = make_transaction(quantity=qty)
        assert t.quantity == qty

    def test_fee_fields_can_be_set(self):
        t = make_transaction(
            fee_amount=Decimal("0.001"),
            fee_asset="BNB",
        )
        assert t.fee_amount == Decimal("0.001")
        assert t.fee_asset == "BNB"

    def test_transaction_is_mutable(self):
        # Entities are NOT frozen — they can be updated (e.g. by the normalizer).
        # This is intentional and different from value objects.
        t = make_transaction()
        t.source = "update_source"
        assert t.source == "update_source"
