import dataclasses
from decimal import Decimal

import pytest

from src.domain.value_objects.quantity import Quantity


class TestQuantityCreation:
    def test_valid_positive_amount(self):
        q = Quantity(Decimal("1.5"))
        assert q.amount == Decimal("1.5")

    def test_zero_is_valid(self):
        # Zero represents an empty position — must not raise
        q = Quantity(Decimal("0"))
        assert q.is_zero()

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="must be >= 0"):
            Quantity(Decimal("-0.001"))

    def test_wrong_type_raises(self):
        with pytest.raises(TypeError, match="must be a Decimal"):
            Quantity(1.5)  # float, not Decimal


class TestQuantityImmutability:
    def test_frozen_cannot_be_mutated(self):
        q = Quantity(Decimal("1"))
        with pytest.raises(dataclasses.FrozenInstanceError):
            q.amount = Decimal("2")  # type: ignore

    def test_equal_quantities_are_equal(self):
        assert Quantity(Decimal("1")) == Quantity(Decimal("1"))

    def test_different_quantities_are_not_equal(self):
        assert Quantity(Decimal("1")) != Quantity(Decimal("2"))

    def test_hashable(self):
        # frozen dataclasses must be usable in sets and as dict keys
        s = {Quantity(Decimal("1")), Quantity(Decimal("1"))}
        assert len(s) == 1


class TestQuantityArithmetic:
    def test_add_two_quantities(self):
        result = Quantity(Decimal("1")) + Quantity(Decimal("2"))
        assert result == Quantity(Decimal("3"))

    def test_subtract_gives_correct_result(self):
        result = Quantity(Decimal("3")) - Quantity(Decimal("1"))
        assert result == Quantity(Decimal("2"))

    def test_subtract_to_zero_is_valid(self):
        result = Quantity(Decimal("1")) - Quantity(Decimal("1"))
        assert result.is_zero()

    def test_subtract_below_zero_raises(self):
        with pytest.raises(ValueError):
            Quantity(Decimal("1")) - Quantity(Decimal("2"))
