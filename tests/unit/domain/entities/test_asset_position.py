from collections import deque
from datetime import UTC
from decimal import Decimal

import pytest

from src.domain.entities.asset_position import AssetPosition
from src.domain.entities.transaction import Transaction
from src.domain.value_objects.asset_symbol import AssetSymbol
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.transaction_type import TransactionType


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------
def make_btc_transaction(**overrides) -> Transaction:
    """Build a minimal BTC BUY transaction. Override any field via kwargs."""
    from datetime import datetime

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


def make_eth_transaction(**overrides) -> Transaction:
    """Build a minimal ETH BUY transaction."""
    from datetime import datetime

    defaults = dict(
        asset=AssetSymbol("ETH"),
        transaction_type=TransactionType.BUY,
        quantity=Quantity(Decimal("1.0")),
        unit_price=Decimal("2000"),
        total_value=Decimal("2000"),
        source="binance_csv",
        occurred_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
    )
    return Transaction(**{**defaults, **overrides})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestAssetPositionCreation:
    """A brand-new AssetPosition starts empty and stores its asset."""

    def test_position_starts_with_empty_queue(self):
        position = AssetPosition(asset=AssetSymbol("BTC"))
        assert len(position.queue) == 0

    def test_is_empty_returns_true_for_new_position(self):
        position = AssetPosition(asset=AssetSymbol("BTC"))
        assert position.is_empty() is True

    def test_asset_is_stored_correctly(self):
        position = AssetPosition(asset=AssetSymbol("ETH"))
        assert position.asset == AssetSymbol("ETH")


class TestAssetPositionAddTransaction:
    """add_transaction() appends to the queue and enforces the same-asset invariant."""

    def test_add_transaction_appends_to_queue(self):
        position = AssetPosition(asset=AssetSymbol("BTC"))
        t = make_btc_transaction()
        position.add_transaction(t)
        assert len(position.queue) == 1

    def test_add_multiple_transactions_preserves_order(self):
        position = AssetPosition(asset=AssetSymbol("BTC"))
        t1 = make_btc_transaction()
        t2 = make_btc_transaction()
        t3 = make_btc_transaction()
        position.add_transaction(t1)
        position.add_transaction(t2)
        position.add_transaction(t3)
        assert position.queue[0] is t1
        assert position.queue[-1] is t3

    def test_add_transaction_wrong_asset_raises(self):
        position = AssetPosition(asset=AssetSymbol("BTC"))
        eth_transaction = make_eth_transaction()
        with pytest.raises(ValueError, match="ETH"):
            position.add_transaction(eth_transaction)

    def test_is_empty_returns_false_after_add(self):
        position = AssetPosition(asset=AssetSymbol("BTC"))
        position.add_transaction(make_btc_transaction())
        assert position.is_empty() is False

    def test_queue_pops_in_fifo_order(self):
        # deque.popleft() removes from the front — oldest transaction first.
        position = AssetPosition(asset=AssetSymbol("BTC"))
        t1 = make_btc_transaction()
        t2 = make_btc_transaction()
        position.add_transaction(t1)
        position.add_transaction(t2)
        first_out = position.queue.popleft()
        assert first_out is t1


class TestAssetPositionIdentity:
    """Identity is by asset symbol only — queue contents are irrelevant."""

    def test_two_positions_same_asset_are_equal(self):
        p1 = AssetPosition(asset=AssetSymbol("BTC"))
        p2 = AssetPosition(asset=AssetSymbol("BTC"))
        assert p1 == p2

    def test_two_positions_different_asset_are_not_equal(self):
        p1 = AssetPosition(asset=AssetSymbol("BTC"))
        p2 = AssetPosition(asset=AssetSymbol("ETH"))
        assert p1 != p2

    def test_position_is_not_equal_to_non_position(self):
        position = AssetPosition(asset=AssetSymbol("BTC"))
        assert position.__eq__("BTC") is NotImplemented

    def test_position_is_hashable(self):
        position = AssetPosition(asset=AssetSymbol("BTC"))
        assert isinstance(hash(position), int)

    def test_same_asset_position_deduplicates_in_set(self):
        p1 = AssetPosition(asset=AssetSymbol("BTC"))
        p2 = AssetPosition(asset=AssetSymbol("BTC"))
        result = {p1, p2}
        assert len(result) == 1


class TestAssetPositionMutability:
    """AssetPosition is a mutable entity — fields and queue can change in place."""

    def test_queue_grows_as_transactions_are_added(self):
        position = AssetPosition(asset=AssetSymbol("BTC"))
        for _ in range(3):
            position.add_transaction(make_btc_transaction())
        assert len(position.queue) == 3

    def test_queue_shrinks_when_popped(self):
        position = AssetPosition(asset=AssetSymbol("BTC"))
        position.add_transaction(make_btc_transaction())
        position.add_transaction(make_btc_transaction())
        position.queue.popleft()
        assert len(position.queue) == 1

    def test_position_with_different_queues_same_asset_are_equal(self):
        # Equality is by asset only — a full queue and an empty one are "equal".
        p1 = AssetPosition(asset=AssetSymbol("BTC"))
        p2 = AssetPosition(asset=AssetSymbol("BTC"))
        p1.add_transaction(make_btc_transaction())
        assert p1 == p2

    def test_asset_field_is_mutable(self):
        position = AssetPosition(asset=AssetSymbol("BTC"))
        position.asset = AssetSymbol("ETH")
        assert position.asset == AssetSymbol("ETH")

    def test_queue_field_is_mutable(self):
        position = AssetPosition(asset=AssetSymbol("BTC"))
        position.queue = deque()
        assert len(position.queue) == 0
