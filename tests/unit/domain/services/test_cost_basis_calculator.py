from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities.processing_result import ProcessingResult
from src.domain.entities.transaction import Transaction
from src.domain.services.cost_basis_calculator import CostBasisCalculator
from src.domain.value_objects.asset_symbol import AssetSymbol
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.transaction_type import TransactionType

JOB_ID = uuid4()
BTC = AssetSymbol("BTC")

T1 = datetime(2024, 1, 1, tzinfo=UTC)
T2 = datetime(2024, 1, 2, tzinfo=UTC)
T3 = datetime(2024, 1, 3, tzinfo=UTC)


def make_buy(qty: str, unit_price: str, at: datetime = T1, **overrides) -> Transaction:
    q = Decimal(qty)
    up = Decimal(unit_price)
    return Transaction(
        job_id=JOB_ID,
        asset=BTC,
        transaction_type=TransactionType.BUY,
        quantity=Quantity(q),
        unit_price=up,
        total_value=q * up,
        occurred_at=at,
        **overrides,
    )


def make_sell(qty: str, unit_price: str, at: datetime = T2, **overrides) -> Transaction:
    q = Decimal(qty)
    up = Decimal(unit_price)
    return Transaction(
        job_id=JOB_ID,
        asset=BTC,
        transaction_type=TransactionType.SELL,
        quantity=Quantity(q),
        unit_price=up,
        total_value=q * up,
        occurred_at=at,
        **overrides,
    )


def make_fee(qty: str, at: datetime = T2, **overrides) -> Transaction:
    q = Decimal(qty)
    return Transaction(
        job_id=JOB_ID,
        asset=BTC,
        transaction_type=TransactionType.FEE,
        quantity=Quantity(q),
        unit_price=Decimal("0"),
        total_value=Decimal("0"),
        occurred_at=at,
        **overrides,
    )


def make_deposit(qty: str, at: datetime = T1, **overrides) -> Transaction:
    q = Decimal(qty)
    return Transaction(
        job_id=JOB_ID,
        asset=BTC,
        transaction_type=TransactionType.DEPOSIT,
        quantity=Quantity(q),
        unit_price=Decimal("0"),
        total_value=Decimal("0"),
        occurred_at=at,
        **overrides,
    )


def make_transfer(qty: str, at: datetime = T1, **overrides) -> Transaction:
    q = Decimal(qty)
    return Transaction(
        job_id=JOB_ID,
        asset=BTC,
        transaction_type=TransactionType.TRANSFER,
        quantity=Quantity(q),
        unit_price=Decimal("0"),
        total_value=Decimal("0"),
        occurred_at=at,
        **overrides,
    )


class TestCostBasisCalculatorReturnTypes:
    def setup_method(self):
        self.calc = CostBasisCalculator()

    def test_returns_processing_result_and_list(self):
        result, errors = self.calc.calculate([make_buy("1", "30000")], JOB_ID)
        assert isinstance(result, ProcessingResult)
        assert isinstance(errors, list)

    def test_result_has_correct_job_id(self):
        result, _ = self.calc.calculate([make_buy("1", "30000")], JOB_ID)
        assert result.job_id == JOB_ID

    def test_result_has_correct_asset(self):
        result, _ = self.calc.calculate([make_buy("1", "30000")], JOB_ID)
        assert result.asset == BTC

    def test_empty_transactions_raises_value_error(self):
        with pytest.raises(ValueError):
            self.calc.calculate([], JOB_ID)


class TestCostBasisCalculatorSingleBuySell:
    """Edge case 1: single buy + single sell."""

    def setup_method(self):
        self.calc = CostBasisCalculator()

    def test_buy_then_sell_correct_realized_profit(self):
        buy = make_buy("1", "30000", at=T1)
        sell = make_sell("1", "35000", at=T2)
        result, errors = self.calc.calculate([buy, sell], JOB_ID)
        assert result.realized_profit == Decimal("5000")
        assert errors == []

    def test_buy_then_sell_at_loss(self):
        buy = make_buy("1", "30000", at=T1)
        sell = make_sell("1", "25000", at=T2)
        result, _ = self.calc.calculate([buy, sell], JOB_ID)
        assert result.realized_profit == Decimal("-5000")

    def test_full_sell_leaves_zero_remaining_quantity(self):
        buy = make_buy("1", "30000", at=T1)
        sell = make_sell("1", "35000", at=T2)
        result, _ = self.calc.calculate([buy, sell], JOB_ID)
        assert result.remaining_quantity == Decimal("0")


class TestCostBasisCalculatorFIFOOrder:
    """Edge case 2: multiple buys at different prices use FIFO on sell."""

    def setup_method(self):
        self.calc = CostBasisCalculator()

    def test_two_buys_one_sell_uses_fifo_not_lifo(self):
        # FIFO: sell consumes first buy (cost 30000), profit = 50000 - 30000 = 20000.
        # LIFO would give 50000 - 40000 = 10000 — use this to confirm FIFO.
        buy1 = make_buy("1", "30000", at=T1)
        buy2 = make_buy("1", "40000", at=T2)
        sell = make_sell("1", "50000", at=T3)

        result, _ = self.calc.calculate([buy1, buy2, sell], JOB_ID)
        assert result.realized_profit == Decimal("20000")

    def test_partial_sell_leaves_correct_remaining_quantity(self):
        buy = make_buy("2", "30000", at=T1)  # 2 BTC at 30000 each
        sell = make_sell("1", "35000", at=T2)
        result, _ = self.calc.calculate([buy, sell], JOB_ID)
        assert result.remaining_quantity == Decimal("1")

    def test_partial_sell_leaves_correct_remaining_cost_basis(self):
        buy = make_buy("2", "30000", at=T1)  # 2 BTC, each costs 30000
        sell = make_sell("1", "35000", at=T2)
        result, _ = self.calc.calculate([buy, sell], JOB_ID)
        assert result.remaining_cost_basis == Decimal("30000")


class TestCostBasisCalculatorOutOfOrder:
    """Edge case 7: out-of-order timestamps are sorted before processing."""

    def setup_method(self):
        self.calc = CostBasisCalculator()

    def test_sell_listed_first_but_has_later_timestamp(self):
        # sell is listed FIRST in the input list but has a LATER timestamp.
        # After sorting by occurred_at the buy is processed first.
        sell = make_sell("1", "35000", at=T2)
        buy = make_buy("1", "30000", at=T1)
        result, errors = self.calc.calculate([sell, buy], JOB_ID)
        assert result.realized_profit == Decimal("5000")
        assert errors == []


class TestCostBasisCalculatorSellErrors:
    """Edge cases 3 and 4: sell with no prior buy, or sell exceeds position."""

    def setup_method(self):
        self.calc = CostBasisCalculator()

    def test_sell_exceeds_position_records_error(self):
        # Buy 1 BTC, try to sell 2 — 1 unit cannot be matched.
        buy = make_buy("1", "30000", at=T1)
        sell = make_sell("2", "35000", at=T2)
        _, errors = self.calc.calculate([buy, sell], JOB_ID)
        assert len(errors) == 1
        assert errors[0].error_code == "SELL_EXCEEDS_POSITION"

    def test_sell_exceeds_position_partial_profit_recorded(self):
        # Only the matched unit generates P&L: 1 * 35000 - 1 * 30000 = 5000.
        buy = make_buy("1", "30000", at=T1)
        sell = make_sell("2", "35000", at=T2)
        result, _ = self.calc.calculate([buy, sell], JOB_ID)
        assert result.realized_profit == Decimal("5000")

    def test_sell_with_no_prior_buy_records_error(self):
        sell = make_sell("1", "35000", at=T1)
        _, errors = self.calc.calculate([sell], JOB_ID)
        assert len(errors) == 1
        assert errors[0].error_code == "SELL_EXCEEDS_POSITION"

    def test_sell_no_prior_buy_zero_realized_profit(self):
        sell = make_sell("1", "35000", at=T1)
        result, _ = self.calc.calculate([sell], JOB_ID)
        assert result.realized_profit == Decimal("0")


class TestCostBasisCalculatorFees:
    """Edge cases 5 and 6: fee handling."""

    def setup_method(self):
        self.calc = CostBasisCalculator()

    def test_inline_fee_exceeds_buy_qty_nothing_added_to_queue(self):
        # Buy 1 BTC but fee is 1.5 BTC — net qty goes negative, clamped to 0.
        # Nothing is added to the queue, so a sell afterwards triggers an error.
        buy = make_buy(
            "1",
            "30000",
            at=T1,
            fee_amount=Decimal("1.5"),
            fee_asset="BTC",
        )
        sell = make_sell("1", "35000", at=T2)
        _, errors = self.calc.calculate([buy, sell], JOB_ID)
        assert len(errors) == 1
        assert errors[0].error_code == "SELL_EXCEEDS_POSITION"

    def test_fee_transaction_type_consumes_from_queue(self):
        # A standalone FEE transaction removes units from the buy queue.
        # Buy 1 BTC, then a 0.5 BTC fee event → 0.5 BTC should remain.
        buy = make_buy("1", "30000", at=T1)
        fee = make_fee("0.5", at=T2)
        result, errors = self.calc.calculate([buy, fee], JOB_ID)
        assert result.remaining_quantity == Decimal("0.5")
        assert errors == []

    def test_inline_fee_same_asset_reduces_net_quantity(self):
        # Buy 1 BTC at 30000 with a 0.1 BTC fee paid in BTC.
        # Net BTC received = 1 - 0.1 = 0.9.
        # Remaining quantity must be 0.9 (nothing sold yet).
        buy = make_buy("1", "30000", at=T1, fee_amount=Decimal("0.1"), fee_asset="BTC")
        result, errors = self.calc.calculate([buy], JOB_ID)
        assert result.remaining_quantity == Decimal("0.9")
        assert errors == []

    def test_inline_fee_different_asset_does_not_reduce_quantity(self):
        # Buy 1 BTC at 30000 with a 10 USDT fee paid in USDT (not BTC).
        # Net BTC received = 1.0 (fee in a different asset is not deducted).
        buy = make_buy(
            "1",
            "30000",
            at=T1,
            fee_amount=Decimal("10"),
            fee_asset="USDT",
        )
        result, errors = self.calc.calculate([buy], JOB_ID)
        assert result.remaining_quantity == Decimal("1")
        assert errors == []


class TestCostBasisCalculatorSkippedTypes:
    """Edge case 8: DEPOSIT and TRANSFER generate no P&L and do not change queue."""

    def setup_method(self):
        self.calc = CostBasisCalculator()

    def test_deposit_alone_generates_no_realized_profit(self):
        deposit = make_deposit("1", at=T1)
        result, errors = self.calc.calculate([deposit], JOB_ID)
        assert result.realized_profit == Decimal("0")
        assert errors == []

    def test_transfer_alone_generates_no_realized_profit(self):
        transfer = make_transfer("1", at=T1)
        result, errors = self.calc.calculate([transfer], JOB_ID)
        assert result.realized_profit == Decimal("0")
        assert errors == []

    def test_deposit_does_not_add_to_fifo_queue(self):
        # A deposit followed by a sell should produce an error (queue is empty).
        deposit = make_deposit("1", at=T1)
        sell = make_sell("1", "35000", at=T2)
        _, errors = self.calc.calculate([deposit, sell], JOB_ID)
        assert len(errors) == 1
        assert errors[0].error_code == "SELL_EXCEEDS_POSITION"


class TestCostBasisCalculatorDuplicates:
    """Edge case 9: duplicate transaction IDs are rejected."""

    def setup_method(self):
        self.calc = CostBasisCalculator()

    def test_duplicate_transaction_id_records_error(self):
        buy = make_buy("1", "30000", at=T1)
        # Create a second transaction sharing the same UUID.
        duplicate = make_buy("1", "40000", at=T2, id=buy.id)
        _, errors = self.calc.calculate([buy, duplicate], JOB_ID)
        assert len(errors) == 1
        assert errors[0].error_code == "DUPLICATE_TRANSACTION_ID"

    def test_duplicate_transaction_id_only_first_is_processed(self):
        # Only the first buy should be in the queue; the duplicate is skipped.
        # After selling 1 unit, remaining = 0 (no second buy was queued).
        buy = make_buy("1", "30000", at=T1)
        duplicate = make_buy("1", "40000", at=T2, id=buy.id)
        sell = make_sell("1", "35000", at=T3)
        result, _ = self.calc.calculate([buy, duplicate, sell], JOB_ID)
        assert result.remaining_quantity == Decimal("0")


class TestCostBasisCalculatorZeroQuantity:
    """Edge case 10: zero-quantity BUY/SELL/FEE transactions are rejected."""

    def setup_method(self):
        self.calc = CostBasisCalculator()

    def test_zero_quantity_buy_records_error(self):
        zero_buy = Transaction(
            job_id=JOB_ID,
            asset=BTC,
            transaction_type=TransactionType.BUY,
            quantity=Quantity(Decimal("0")),
            unit_price=Decimal("30000"),
            total_value=Decimal("0"),
            occurred_at=T1,
        )
        _, errors = self.calc.calculate([zero_buy], JOB_ID)
        assert len(errors) == 1
        assert errors[0].error_code == "ZERO_QUANTITY"

    def test_zero_quantity_sell_records_error(self):
        buy = make_buy("1", "30000", at=T1)
        zero_sell = Transaction(
            job_id=JOB_ID,
            asset=BTC,
            transaction_type=TransactionType.SELL,
            quantity=Quantity(Decimal("0")),
            unit_price=Decimal("35000"),
            total_value=Decimal("0"),
            occurred_at=T2,
        )
        _, errors = self.calc.calculate([buy, zero_sell], JOB_ID)
        assert len(errors) == 1
        assert errors[0].error_code == "ZERO_QUANTITY"
