from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.transaction import Transaction
from src.domain.entities.validation_error import ValidationError
from src.domain.services.transaction_validator import TransactionValidator
from src.domain.value_objects.asset_symbol import AssetSymbol
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.transaction_type import TransactionType


def make_transaction(**overrides) -> Transaction:
    defaults = dict(
        job_id=uuid4(),
        asset=AssetSymbol("BTC"),
        transaction_type=TransactionType.BUY,
        quantity=Quantity(Decimal("0.5")),
        unit_price=Decimal("30000"),
        total_value=Decimal("15000"),
        occurred_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
    )
    return Transaction(**{**defaults, **overrides})


class TestTransactionValidatorHappyPath:
    def setup_method(self):
        self.validator = TransactionValidator()

    def test_valid_buy_returns_empty_list(self):
        errors = self.validator.validate(make_transaction(), row_number=1)
        assert errors == []

    def test_valid_sell_returns_empty_list(self):
        t = make_transaction(transaction_type=TransactionType.SELL)
        errors = self.validator.validate(t, row_number=1)
        assert errors == []

    def test_valid_fee_returns_empty_list(self):
        t = make_transaction(
            transaction_type=TransactionType.FEE,
            unit_price=Decimal("0"),
            total_value=Decimal("0"),
        )
        errors = self.validator.validate(t, row_number=1)
        assert errors == []

    def test_valid_deposit_returns_empty_list(self):
        t = make_transaction(
            transaction_type=TransactionType.DEPOSIT,
            unit_price=Decimal("0"),
            total_value=Decimal("0"),
        )
        errors = self.validator.validate(t, row_number=1)
        assert errors == []

    def test_returns_list_of_validation_error_objects(self):
        t = make_transaction(quantity=Quantity(Decimal("0")))
        errors = self.validator.validate(t, row_number=1)
        assert all(isinstance(e, ValidationError) for e in errors)

    def test_error_carries_correct_job_id(self):
        job_id = uuid4()
        t = make_transaction(job_id=job_id, quantity=Quantity(Decimal("0")))
        errors = self.validator.validate(t, row_number=1)
        assert errors[0].job_id == job_id

    def test_error_carries_correct_row_number(self):
        t = make_transaction(quantity=Quantity(Decimal("0")))
        errors = self.validator.validate(t, row_number=7)
        assert errors[0].row_number == 7


class TestTransactionValidatorQuantityRules:
    def setup_method(self):
        self.validator = TransactionValidator()

    def test_zero_quantity_buy_fails(self):
        t = make_transaction(quantity=Quantity(Decimal("0")))
        errors = self.validator.validate(t, row_number=1)
        codes = [e.error_code for e in errors]
        assert "ZERO_QUANTITY" in codes

    def test_zero_quantity_sell_fails(self):
        t = make_transaction(
            transaction_type=TransactionType.SELL,
            quantity=Quantity(Decimal("0")),
        )
        errors = self.validator.validate(t, row_number=1)
        codes = [e.error_code for e in errors]
        assert "ZERO_QUANTITY" in codes

    def test_zero_quantity_error_has_field_name_quantity(self):
        t = make_transaction(quantity=Quantity(Decimal("0")))
        errors = self.validator.validate(t, row_number=1)
        zero_qty_error = next(e for e in errors if e.error_code == "ZERO_QUANTITY")
        assert zero_qty_error.field_name == "quantity"

    def test_zero_quantity_fee_passes(self):
        t = make_transaction(
            transaction_type=TransactionType.FEE,
            quantity=Quantity(Decimal("0")),
            unit_price=Decimal("0"),
            total_value=Decimal("0"),
        )
        errors = self.validator.validate(t, row_number=1)
        assert errors == []

    def test_zero_quantity_deposit_passes(self):
        t = make_transaction(
            transaction_type=TransactionType.DEPOSIT,
            quantity=Quantity(Decimal("0")),
            unit_price=Decimal("0"),
            total_value=Decimal("0"),
        )
        errors = self.validator.validate(t, row_number=1)
        assert errors == []

    def test_zero_quantity_withdrawal_passes(self):
        t = make_transaction(
            transaction_type=TransactionType.WITHDRAWAL,
            quantity=Quantity(Decimal("0")),
            unit_price=Decimal("0"),
            total_value=Decimal("0"),
        )
        errors = self.validator.validate(t, row_number=1)
        assert errors == []


class TestTransactionValidatorPriceRules:
    def setup_method(self):
        self.validator = TransactionValidator()

    def test_zero_unit_price_buy_fails(self):
        t = make_transaction(unit_price=Decimal("0"))
        errors = self.validator.validate(t, row_number=1)
        codes = [e.error_code for e in errors]
        assert "INVALID_UNIT_PRICE" in codes

    def test_negative_unit_price_buy_fails(self):
        t = make_transaction(unit_price=Decimal("-1"))
        errors = self.validator.validate(t, row_number=1)
        codes = [e.error_code for e in errors]
        assert "INVALID_UNIT_PRICE" in codes

    def test_unit_price_error_has_correct_field_name(self):
        t = make_transaction(unit_price=Decimal("0"))
        errors = self.validator.validate(t, row_number=1)
        price_error = next(e for e in errors if e.error_code == "INVALID_UNIT_PRICE")
        assert price_error.field_name == "unit_price"

    def test_zero_total_value_sell_fails(self):
        t = make_transaction(
            transaction_type=TransactionType.SELL,
            total_value=Decimal("0"),
        )
        errors = self.validator.validate(t, row_number=1)
        codes = [e.error_code for e in errors]
        assert "INVALID_TOTAL_VALUE" in codes

    def test_total_value_error_has_correct_field_name(self):
        t = make_transaction(total_value=Decimal("0"))
        errors = self.validator.validate(t, row_number=1)
        tv_error = next(e for e in errors if e.error_code == "INVALID_TOTAL_VALUE")
        assert tv_error.field_name == "total_value"

    def test_zero_unit_price_fee_passes(self):
        t = make_transaction(
            transaction_type=TransactionType.FEE,
            unit_price=Decimal("0"),
            total_value=Decimal("0"),
        )
        errors = self.validator.validate(t, row_number=1)
        assert errors == []

    def test_multiple_price_errors_accumulated(self):
        t = make_transaction(unit_price=Decimal("0"), total_value=Decimal("0"))
        errors = self.validator.validate(t, row_number=1)
        codes = [e.error_code for e in errors]
        assert "INVALID_UNIT_PRICE" in codes
        assert "INVALID_TOTAL_VALUE" in codes


class TestTransactionValidatorDateRules:
    def setup_method(self):
        self.validator = TransactionValidator()

    def test_future_occurred_at_fails(self):
        t = make_transaction(occurred_at=datetime(2099, 1, 1, tzinfo=UTC))
        errors = self.validator.validate(t, row_number=1)
        codes = [e.error_code for e in errors]
        assert "FUTURE_DATE" in codes

    def test_future_date_error_has_correct_field_name(self):
        t = make_transaction(occurred_at=datetime(2099, 1, 1, tzinfo=UTC))
        errors = self.validator.validate(t, row_number=1)
        date_error = next(e for e in errors if e.error_code == "FUTURE_DATE")
        assert date_error.field_name == "occurred_at"

    def test_past_occurred_at_passes(self):
        t = make_transaction(occurred_at=datetime(2020, 6, 15, tzinfo=UTC))
        errors = self.validator.validate(t, row_number=1)
        assert errors == []


class TestTransactionValidatorDuplicateDetection:
    def setup_method(self):
        self.validator = TransactionValidator()

    def test_first_occurrence_of_external_id_passes(self):
        t = make_transaction(external_id="TX-001", source="binance_csv")
        errors = self.validator.validate(t, row_number=1)
        assert not any(e.error_code == "DUPLICATE_EXTERNAL_ID" for e in errors)

    def test_second_occurrence_of_same_external_id_fails(self):
        t1 = make_transaction(external_id="TX-001", source="binance_csv")
        t2 = make_transaction(external_id="TX-001", source="binance_csv")
        self.validator.validate(t1, row_number=1)
        errors = self.validator.validate(t2, row_number=2)
        codes = [e.error_code for e in errors]
        assert "DUPLICATE_EXTERNAL_ID" in codes

    def test_same_external_id_different_source_passes(self):
        t1 = make_transaction(external_id="TX-001", source="binance_csv")
        t2 = make_transaction(external_id="TX-001", source="kraken_csv")
        self.validator.validate(t1, row_number=1)
        errors = self.validator.validate(t2, row_number=2)
        assert not any(e.error_code == "DUPLICATE_EXTERNAL_ID" for e in errors)

    def test_empty_external_id_not_checked_for_duplicates(self):
        t1 = make_transaction(external_id="")
        t2 = make_transaction(external_id="")
        self.validator.validate(t1, row_number=1)
        errors = self.validator.validate(t2, row_number=2)
        assert not any(e.error_code == "DUPLICATE_EXTERNAL_ID" for e in errors)

    def test_duplicate_error_is_row_level_no_field_name(self):
        t1 = make_transaction(external_id="TX-001", source="binance_csv")
        t2 = make_transaction(external_id="TX-001", source="binance_csv")
        self.validator.validate(t1, row_number=1)
        errors = self.validator.validate(t2, row_number=2)
        dup_error = next(e for e in errors if e.error_code == "DUPLICATE_EXTERNAL_ID")
        assert dup_error.field_name is None
