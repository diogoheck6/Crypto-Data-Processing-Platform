import dataclasses
from decimal import Decimal

import pytest

from src.domain.value_objects.money import Money


class TestMoneyCreation:
    def test_valid_money(self):
        m = Money(Decimal("150.00"), "USD")
        assert m.amount == Decimal("150.00")
        assert m.currency == "USD"

    def test_currency_normalised_to_uppercase(self):
        m = Money(Decimal("1"), "usd")
        assert m.currency == "USD"

    def test_currency_whitespace_stripped(self):
        m = Money(Decimal("1"), "  USD  ")
        assert m.currency == "USD"

    def test_zero_amount_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            Money(Decimal("0"), "USD")

    def test_negative_amount_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            Money(Decimal(-0.01), "USD")

    def test_float_amount_raises(self):
        with pytest.raises(TypeError, match="must be a Decimal"):
            Money(1.5, "USD")  # type: ignore

    def test_empty_currency_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            Money(Decimal("1"), "")

    def test_whitespace_currency_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            Money(Decimal("1"), "  ")

    def test_non_string_currency_raises(self):
        with pytest.raises(TypeError, match="must be a str"):
            Money(Decimal("1"), 123)  # type: ignore


class TestMoneyImmutability:
    def test_frozen_cannot_be_mutated(self):
        m = Money(Decimal("1"), "USD")
        with pytest.raises(dataclasses.FrozenInstanceError):
            m.amount = Decimal("2")  # type: ignore

    def test_equal_money_instances(self):
        assert Money(Decimal("1"), "USD") == Money(Decimal("1"), "USD")

    def test_different_amount_not_equal(self):
        assert Money(Decimal("1"), "USD") != Money(Decimal("2"), "USD")

    def test_different_currency_not_equal(self):
        assert Money(Decimal("1"), "USD") != Money(Decimal("1"), "EUR")

    def test_hashable(self):
        s = {Money(Decimal("1"), "USD"), Money(Decimal("1"), "USD")}
        assert len(s) == 1


class TestMoneyArithmetic:
    def test_add_same_currency(self):
        result = Money(Decimal("1"), "USD") + Money(Decimal("2"), "USD")
        assert result == Money(Decimal("3"), "USD")

    def test_add_different_currency_raises(self):
        with pytest.raises(ValueError, match="different currencies"):
            Money(Decimal("1"), "USD") + Money(Decimal("1"), "EUR")

    def test_str_representation(self):
        assert str(Money(Decimal("150.00"), "USD")) == "150.00 USD"
