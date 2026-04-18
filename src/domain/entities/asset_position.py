"""AssetPosition — FIFO buy queue for a single asset.

Holds the ordered list of buy-side Transactions waiting to be consumed
by the CostBasisCalculator when sell events arrive.

Design notes:
- Mutable by design: the calculator pushes buys and pops from the front.
- One AssetPosition per asset symbol; adding a transaction for the wrong
  asset raises ValueError — this guards the FIFO invariant.
- Identity is by asset symbol, not by object identity.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from src.domain.entities.transaction import Transaction
from src.domain.value_objects.asset_symbol import AssetSymbol


@dataclass
class AssetPosition:
    asset: AssetSymbol
    queue: deque[Transaction] = field(default_factory=deque)

    # ------------------------------------------------------------------
    # Invariant enforcement
    # ------------------------------------------------------------------

    def add_transaction(self, transaction: Transaction) -> None:
        """Append a buy transaction to the back of the FIFO queue.

        Raises:
            ValueError: if the transaction's asset does not match this position.
        """
        if transaction.asset != self.asset:
            raise ValueError(
                f"Cannot add transaction for {transaction.asset!r} "
                f"to AssetPosition for {self.asset!r}."
            )
        self.queue.append(transaction)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def is_empty(self) -> bool:
        """Return True when there are no buy transactions remaining."""
        return len(self.queue) == 0

    # ------------------------------------------------------------------
    # Identity — one position per asset symbol
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AssetPosition):
            return self.asset == other.asset
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.asset)
