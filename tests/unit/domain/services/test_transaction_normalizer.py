from datetime import UTC
from decimal import Decimal

import pytest

from src.domain.entities.transaction import Transaction
from src.domain.services.transaction_normalizer import TransactionNormalizer
from src.domain.value_objects.asset_symbol import AssetSymbol
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.transaction_type import TransactionType

# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def make_raw(**overrides) -> dict:
    """Build a valid minimal raw dict. Override any field via kwargs."""
    defaults = {
        "asset": "BTC",
        "transaction_type": "buy",
        "quantity": "0.5",
        "unit_price": "30000",
        "total_value": "15000",
        "occurred_at": "2024-01-01T12:00:00+00:00",
    }
    return {**defaults, **overrides}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestTransactionNormalizerHappyPath:
    """A valid raw dict produces a correctly typed Transaction."""

    def setup_method(self):
        self.normalizer = TransactionNormalizer()

    def test_returns_transaction_instance(self):
        result = self.normalizer.normalize(make_raw())
        assert isinstance(result, Transaction)

    def test_asset_is_correct_type(self):
        result = self.normalizer.normalize(make_raw(asset="eth"))
        assert result.asset == AssetSymbol("ETH")

    def test_asset_is_normalized_to_uppercase(self):
        result = self.normalizer.normalize(make_raw(asset="btc"))
        assert result.asset.symbol == "BTC"

    def test_transaction_type_is_correct(self):
        result = self.normalizer.normalize(make_raw(transaction_type="sell"))
        assert result.transaction_type == TransactionType.SELL

    def test_transaction_type_is_case_insensitive(self):
        result = self.normalizer.normalize(make_raw(transaction_type="BUY"))
        assert result.transaction_type == TransactionType.BUY

    def test_quantity_is_correct_type(self):
        result = self.normalizer.normalize(make_raw(quantity="1.25"))
        assert result.quantity == Quantity(Decimal("1.25"))

    def test_unit_price_is_decimal(self):
        result = self.normalizer.normalize(make_raw(unit_price="29999.99"))
        assert result.unit_price == Decimal("29999.99")

    def test_total_value_is_decimal(self):
        result = self.normalizer.normalize(make_raw(total_value="14999.995"))
        assert result.total_value == Decimal("14999.995")

    def test_occurred_at_is_timezone_aware(self):
        result = self.normalizer.normalize(make_raw())
        assert result.occurred_at.tzinfo is not None

    def test_naive_occurred_at_gets_utc_timezone(self):
        # A naive datetime string (no offset) must be treated as UTC.
        result = self.normalizer.normalize(make_raw(occurred_at="2024-01-01T12:00:00"))
        assert result.occurred_at.tzinfo == UTC

    def test_fee_fields_are_none_when_absent(self):
        result = self.normalizer.normalize(make_raw())
        assert result.fee_amount is None
        assert result.fee_asset is None

    def test_fee_amount_is_decimal_when_present(self):
        result = self.normalizer.normalize(
            make_raw(fee_amount="1.50", fee_asset="USDT")
        )
        assert result.fee_amount == Decimal("1.50")
        assert result.fee_asset == "USDT"

    def test_unknown_keys_in_raw_dict_are_ignored(self):
        raw = make_raw(unknown_column="ignored", another_extra="also_ignored")
        result = self.normalizer.normalize(raw)
        assert isinstance(result, Transaction)

    def test_raw_payload_is_stored_on_transacion(self):
        raw = make_raw()
        result = self.normalizer.normalize(raw)
        assert result.raw_payload == raw

    def test_optional_source_and_external_id_are_stored(self):
        result = self.normalizer.normalize(
            make_raw(source="binance_csv", external_id="TX99")
        )
        assert result.source == "binance_csv"
        assert result.external_id == "TX99"

    def test_missing_optional_source_defaults_to_empty_string(self):
        result = self.normalizer.normalize(make_raw())
        assert result.source == ""
        assert result.external_id == ""


class TestTransactionNormalizerMissingFields:
    """Each missing required field must raise ValueError."""

    def setup_method(self):
        self.normalizer = TransactionNormalizer()

    def test_missing_asset_raises(self):
        raw = make_raw()
        del raw["asset"]
        with pytest.raises(ValueError, match="asset"):
            self.normalizer.normalize(raw)

    def test_missing_transaction_type_raises(self):
        raw = make_raw()
        del raw["transaction_type"]
        with pytest.raises(ValueError, match="transaction_type"):
            self.normalizer.normalize(raw)

    def test_missing_quantity_raises(self):
        raw = make_raw()
        del raw["quantity"]
        with pytest.raises(ValueError, match="quantity"):
            self.normalizer.normalize(raw)

    def test_missing_unit_price_raises(self):
        raw = make_raw()
        del raw["unit_price"]
        with pytest.raises(ValueError, match="unit_price"):
            self.normalizer.normalize(raw)

    def test_missing_total_value_raises(self):
        raw = make_raw()
        del raw["total_value"]
        with pytest.raises(ValueError, match="total_value"):
            self.normalizer.normalize(raw)

    def test_missing_occurred_at_raises(self):
        raw = make_raw()
        del raw["occurred_at"]
        with pytest.raises(ValueError, match="occurred_at"):
            self.normalizer.normalize(raw)


class TestTransactionNormalizerInvalidValues:
    """Invalid field values must raise ValueError with a clear message."""

    def setup_method(self):
        self.normalizer = TransactionNormalizer()

    def test_invalid_transaction_type_raises(self):
        with pytest.raises(ValueError, match="transaction_type"):
            self.normalizer.normalize(make_raw(transaction_type="swap"))

    def test_invalid_quantity_format_raises(self):
        with pytest.raises(ValueError, match="quantity"):
            self.normalizer.normalize(make_raw(quantity="not_a_number"))

    def test_negative_quantity_raises(self):
        # Quantity value object rejects negative amounts.
        with pytest.raises(ValueError):
            self.normalizer.normalize(make_raw(quantity="-0.5"))

    def test_invalid_occurred_at_format_raises(self):
        with pytest.raises(ValueError, match="occurred_at"):
            self.normalizer.normalize(make_raw(occurred_at="not-a-date"))

    def test_empty_asset_raises(self):
        with pytest.raises(ValueError):
            self.normalizer.normalize(make_raw(asset=""))

    def test_invalid_unit_price_format_raises(self):
        with pytest.raises(ValueError, match="unit_price"):
            self.normalizer.normalize(make_raw(unit_price="not_a_number"))
