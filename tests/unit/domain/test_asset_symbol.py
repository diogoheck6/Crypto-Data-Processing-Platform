import dataclasses

import pytest

from src.domain.value_objects.asset_symbol import AssetSymbol


class TestAssetSymbolCreation:
    def test_uppercase_input_stored_as_is(self):
        s = AssetSymbol("BTC")
        assert s.symbol == "BTC"

    def test_lowercase_input_normalised_to_uppercase(self):
        s = AssetSymbol("eth")
        assert s.symbol == "ETH"

    def test_mixed_case_normalised(self):
        s = AssetSymbol("bNb")
        assert s.symbol == "BNB"

    def test_whitespace_is_stripped(self):
        s = AssetSymbol("  BTC  ")
        assert s.symbol == "BTC"

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            AssetSymbol("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            AssetSymbol("   ")

    def test_wrong_type_raises(self):
        with pytest.raises(TypeError, match="must be a str"):
            AssetSymbol(123)  # type: ignore


class TestAssetSymbolImmutability:
    def test_frozen_cannot_be_mutated(self):
        s = AssetSymbol("BTC")
        with pytest.raises(dataclasses.FrozenInstanceError):
            s.symbol = "ETH"  # type: ignore

    def test_same_symbol_equal_regardless_of_input_case(self):
        assert AssetSymbol("btc") == AssetSymbol("BTC")

    def test_different_symbols_not_equal(self):
        assert AssetSymbol("BTC") != AssetSymbol("ETH")

    def test_hashable_and_usable_in_set(self):
        s = {AssetSymbol("BTC"), AssetSymbol("btc"), AssetSymbol("BTC")}
        assert len(s) == 1

    def test_str_returns_symbol(self):
        assert str(AssetSymbol("eth")) == "ETH"
