from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities.processing_result import ProcessingResult
from src.domain.services.profit_loss_calculator import ProfitLossCalculator
from src.domain.value_objects.asset_symbol import AssetSymbol

JOB_ID = uuid4()
BTC = AssetSymbol("BTC")
ETH = AssetSymbol("ETH")
SOL = AssetSymbol("SOL")


def make_result(
    asset: AssetSymbol,
    realized_profit: str = "0",
    total_cost_basis: str = "0",
    remaining_cost_basis: str = "0",
) -> ProcessingResult:
    return ProcessingResult(
        job_id=JOB_ID,
        asset=asset,
        realized_profit=Decimal(realized_profit),
        total_cost_basis=Decimal(total_cost_basis),
        remaining_cost_basis=Decimal(remaining_cost_basis),
    )


class TestProfitLossCalculatorReturnType:

    def setup_method(self):
        self.calc = ProfitLossCalculator()

    def test_returns_dict(self):
        result = self.calc.calculate([make_result(BTC)])
        assert isinstance(result, dict)

    def test_empty_results_raises_value_error(self):
        with pytest.raises(ValueError):
            self.calc.calculate([])

    def test_result_has_all_expected_keys(self):
        summary = self.calc.calculate([make_result(BTC)])
        expected_keys = {
            "total_realized_profit",
            "total_cost_basis",
            "total_remaining_cost_basis",
            "assets_in_profit",
            "assets_at_loss",
            "assets_breakeven",
        }
        assert set(summary.keys()) == expected_keys


class TestProfitLossCalculatorTotals:

    def setup_method(self):
        self.calc = ProfitLossCalculator()

    def test_total_realized_profit_single_asset(self):
        result = make_result(BTC, realized_profit="5000")
        summary = self.calc.calculate([result])
        assert summary["total_realized_profit"] == Decimal("5000")

    def test_total_realized_profit_summed_across_assets(self):
        btc = make_result(BTC, realized_profit="3000")
        eth = make_result(ETH, realized_profit="2000")
        summary = self.calc.calculate([btc, eth])
        assert summary["total_realized_profit"] == Decimal("5000")

    def test_total_realized_profit_includes_losses(self):
        # BTC made 5000 profit, ETH lost 2000 — net is 3000.
        btc = make_result(BTC, realized_profit="5000")
        eth = make_result(ETH, realized_profit="-2000")
        summary = self.calc.calculate([btc, eth])
        assert summary["total_realized_profit"] == Decimal("3000")

    def test_total_cost_basis_summed_across_assets(self):
        btc = make_result(BTC, total_cost_basis="30000")
        eth = make_result(ETH, total_cost_basis="10000")
        summary = self.calc.calculate([btc, eth])
        assert summary["total_cost_basis"] == Decimal("40000")

    def test_total_remaining_cost_basis_summed_across_assets(self):
        btc = make_result(BTC, remaining_cost_basis="15000")
        eth = make_result(ETH, remaining_cost_basis="5000")
        summary = self.calc.calculate([btc, eth])
        assert summary["total_remaining_cost_basis"] == Decimal("20000")

    def test_buy_only_asset_has_zero_realized_profit(self):
        # No sells have happened — realized profit must be zero.
        buy_only = make_result(BTC, realized_profit="0", remaining_cost_basis="30000")
        summary = self.calc.calculate([buy_only])
        assert summary["total_realized_profit"] == Decimal("0")


class TestProfitLossCalculatorClassification:

    def setup_method(self):
        self.calc = ProfitLossCalculator()

    def test_profitable_asset_is_in_assets_in_profit(self):
        result = make_result(BTC, realized_profit="1000")
        summary = self.calc.calculate([result])
        assert "BTC" in summary["assets_in_profit"]

    def test_losing_asset_is_in_assets_at_loss(self):
        result = make_result(ETH, realized_profit="-500")
        summary = self.calc.calculate([result])
        assert "ETH" in summary["assets_at_loss"]

    def test_zero_profit_asset_is_in_assets_breakeven(self):
        result = make_result(SOL, realized_profit="0")
        summary = self.calc.calculate([result])
        assert "SOL" in summary["assets_breakeven"]

    def test_buy_only_asset_is_breakeven_not_profitable(self):
        # A position with no sells has realized_profit == 0 → breakeven.
        buy_only = make_result(BTC, realized_profit="0", remaining_cost_basis="30000")
        summary = self.calc.calculate([buy_only])
        assert "BTC" in summary["assets_breakeven"]
        assert "BTC" not in summary["assets_in_profit"]

    def test_mixed_portfolio_classifies_each_asset_correctly(self):
        btc = make_result(BTC, realized_profit="5000")  # profit
        eth = make_result(ETH, realized_profit="-1000")  # loss
        sol = make_result(SOL, realized_profit="0")  # breakeven
        summary = self.calc.calculate([btc, eth, sol])
        assert summary["assets_in_profit"] == ["BTC"]
        assert summary["assets_at_loss"] == ["ETH"]
        assert summary["assets_breakeven"] == ["SOL"]

    def test_no_asset_appears_in_more_than_one_category(self):
        btc = make_result(BTC, realized_profit="5000")
        summary = self.calc.calculate([btc])
        all_assets = (
            summary["assets_in_profit"]
            + summary["assets_at_loss"]
            + summary["assets_breakeven"]
        )
        assert all_assets.count("BTC") == 1
