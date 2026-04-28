"""ProfitLossCalculator — aggregates per-asset FIFO results into a job-level
profit/loss summary.

CostBasisCalculator works per asset. This service combines all per-asset
ProcessingResult objects produced for a single job and returns the final
summary metrics consumed by the use case layer (e.g. process_transactions,
get_portfolio_summary).

Responsibility boundary:
    - CostBasisCalculator : FIFO queue logic per asset → ProcessingResult
    - ProfitLossCalculator: aggregate N per-asset results → job-level summary
    - Use cases           : orchestrate the pipeline above

Design notes:
    - Pure domain logic — no I/O, no external dependencies.
    - Stateless: a single instance can be reused across multiple jobs.
    - Input list must be non-empty; raise ValueError otherwise.
    - All monetary values are Decimal; no rounding is applied at this layer.
    - An asset is classified as:
        - "in_profit"  when realized_profit > 0
        - "at_loss"    when realized_profit < 0
        - "breakeven"  when realized_profit == 0  (including buy-only positions)
"""

from __future__ import annotations

from decimal import Decimal

from src.domain.entities.processing_result import ProcessingResult


class ProfitLossCalculator:
    """Aggregate per-asset FIFO results into a job-level P&L summary.

    Usage (once per job, after CostBasisCalculator has run for every asset):
        calc = ProfitLossCalculator()
        summary = calc.calculate(per_asset_results)
    """

    def calculate(self, results: list[ProcessingResult]) -> dict:
        """Aggregate per-asset results into a job-level profit/loss summary.

        Args:
            results: Non-empty list of ProcessingResult, one per asset,
                     as returned by CostBasisCalculator.

        Returns:
            A dict with the following keys:

            total_realized_profit   (Decimal) — net P&L across all assets
            total_cost_basis        (Decimal) — total cost of sold positions
            total_remaining_cost_basis (Decimal) — cost basis of unsold positions
            assets_in_profit        (list[str]) — assets with positive P&L
            assets_at_loss          (list[str]) — assets with negative P&L
            assets_breakeven        (list[str]) — assets with zero P&L

        Raises:
            ValueError: if results is empty.
        """
        if not results:
            raise ValueError("results list cannot be empty")

        total_realized_profit = Decimal("0")
        total_cost_basis = Decimal("0")
        total_remaining_cost_basis = Decimal("0")

        assets_in_profit: list[str] = []
        assets_at_loss: list[str] = []
        assets_breakeven: list[str] = []

        for result in results:
            total_realized_profit += result.realized_profit
            total_cost_basis += result.total_cost_basis
            total_remaining_cost_basis += result.remaining_cost_basis

            symbol = str(result.asset)
            if result.realized_profit > Decimal("0"):
                assets_in_profit.append(symbol)
            elif result.realized_profit < Decimal("0"):
                assets_at_loss.append(symbol)
            else:
                assets_breakeven.append(symbol)

        return {
            "total_realized_profit": total_realized_profit,
            "total_cost_basis": total_cost_basis,
            "total_remaining_cost_basis": total_remaining_cost_basis,
            "assets_in_profit": assets_in_profit,
            "assets_at_loss": assets_at_loss,
            "assets_breakeven": assets_breakeven,
        }
