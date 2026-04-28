"""CostBasisCalculator — FIFO cost basis and realized P&L for a single asset.

Processes a batch of transactions for one asset and returns:
  - A ProcessingResult with realized profit, cost basis consumed, and remaining position.
  - A list of ValidationError for any rule violations encountered during calculation.

Responsibility boundary:
    - TransactionNormalizer : parse raw strings into domain types
    - TransactionValidator  : check business rules per transaction
    - CostBasisCalculator   : apply FIFO cost basis across a batch of transactions
    - Use cases             : orchestrate the pipeline above

Design notes:
    - Pure domain logic — no I/O, no external dependencies.
    - Call once per asset per processing job.
    - All monetary values are Decimal; no rounding is applied at this layer.
    - Errors do not abort processing — all issues are recorded and returned.
    - Inline fees paid in the SAME asset reduce the net quantity added to the queue.
    - Inline fees paid in a DIFFERENT asset do not affect this asset's position.
    - FEE transaction type consumes from the FIFO queue at zero proceeds.
    - DEPOSIT, WITHDRAWAL, TRANSFER generate no P&L and are skipped.
    - row_number is set to 0 on all errors produced by this service because
      FIFO errors are calculation-level issues, not tied to a specific source row.
"""

from __future__ import annotations

from collections import deque
from decimal import Decimal
from uuid import UUID

from src.domain.entities.processing_result import ProcessingResult
from src.domain.entities.transaction import Transaction
from src.domain.entities.validation_error import ValidationError
from src.domain.value_objects.transaction_type import TransactionType


def _consume_from_queue(
    queue: deque[list[Decimal]],
    qty_to_consume: Decimal,
) -> tuple[Decimal, Decimal]:
    """Consume qty_to_consume from the head of the FIFO queue.

    Each queue entry is a mutable two-element list: [remaining_qty, unit_cost].

    Returns:
        (unmatched_qty, total_cost_consumed)
        unmatched_qty > 0 means the queue was exhausted before the full
        quantity was matched.
    """
    remaining = qty_to_consume
    cost_consumed = Decimal("0")

    while remaining > Decimal("0") and queue:
        head = queue[0]
        head_qty, head_unit_cost = head[0], head[1]
        if head_qty <= remaining:
            cost_consumed += head_qty * head_unit_cost
            remaining -= head_qty
            queue.popleft()
        else:
            cost_consumed += remaining * head_unit_cost
            head[0] -= remaining
            remaining = Decimal("0")

    return remaining, cost_consumed


class CostBasisCalculator:
    """FIFO cost basis calculator for a single asset.

    Usage (per asset, per job):
        calc = CostBasisCalculator()
        result, errors = calc.calculate(btc_transactions, job_id)
    """

    def calculate(
        self,
        transactions: list[Transaction],
        job_id: UUID,
    ) -> tuple[ProcessingResult, list[ValidationError]]:
        """Apply FIFO cost basis rules to a list of transactions.

        All transactions must belong to the same asset — the asset is inferred
        from the first element. Transactions are sorted by occurred_at before
        processing so the caller does not need to pre-sort them.

        Args:
            transactions: Non-empty list of Transaction objects for ONE asset.
            job_id:       UUID of the enclosing processing job.

        Returns:
            A (ProcessingResult, list[ValidationError]) tuple.
            The error list is empty when all transactions are valid.

        Raises:
            ValueError: if transactions is empty.
        """
        if not transactions:
            raise ValueError("transactions list cannot be empty")

        asset = transactions[0].asset
        errors: list[ValidationError] = []

        # ── 1. Reject duplicate transaction IDs ───────────────────────────
        seen_ids: set = set()
        deduped: list[Transaction] = []
        for tx in transactions:
            if tx.id in seen_ids:
                errors.append(
                    self._make_error(
                        job_id=job_id,
                        tx=tx,
                        error_code="DUPLICATE_TRANSACTION_ID",
                        message=(
                            f"Transaction id {tx.id} appears more than once "
                            f"in this batch."
                        ),
                    )
                )
            else:
                seen_ids.add(tx.id)
                deduped.append(tx)

        # ── 2. Sort by event time ──────────────────────────────────────────
        sorted_txs = sorted(deduped, key=lambda t: t.occurred_at)

        # ── 3. FIFO queue: each entry is [remaining_qty, unit_cost] ───────
        queue: deque[list[Decimal]] = deque()
        result = ProcessingResult(job_id=job_id, asset=asset)

        for tx in sorted_txs:
            # Defensive: skip zero-quantity transactions that slipped through.
            if tx.quantity.is_zero() and tx.transaction_type in (
                TransactionType.BUY,
                TransactionType.SELL,
                TransactionType.FEE,
            ):
                errors.append(
                    self._make_error(
                        job_id=job_id,
                        tx=tx,
                        error_code="ZERO_QUANTITY",
                        message=(
                            f"Zero quantity {tx.transaction_type.value} transaction "
                            f"cannot be processed."
                        ),
                        field_name="quantity",
                    )
                )
                continue

            if tx.transaction_type == TransactionType.BUY:
                buy_qty = tx.quantity.amount

                # Inline fee in the SAME asset reduces net quantity received.
                # Inline fee in a DIFFERENT asset (e.g. USDT) does not affect
                # this asset's position.
                if (
                    tx.fee_amount is not None
                    and tx.fee_asset is not None
                    and tx.fee_asset == str(asset)
                ):
                    buy_qty = buy_qty - tx.fee_amount
                    if buy_qty < Decimal("0"):
                        buy_qty = Decimal("0")

                if buy_qty > Decimal("0"):
                    unit_cost = tx.total_value / buy_qty
                    queue.append([buy_qty, unit_cost])

            elif tx.transaction_type == TransactionType.SELL:
                sell_qty = tx.quantity.amount
                unmatched, cost_consumed = _consume_from_queue(queue, sell_qty)
                matched_qty = sell_qty - unmatched

                if unmatched > Decimal("0"):
                    errors.append(
                        self._make_error(
                            job_id=job_id,
                            tx=tx,
                            error_code="SELL_EXCEEDS_POSITION",
                            message=(
                                f"Sell of {sell_qty} {asset} exceeds available "
                                f"position; {unmatched} units could not be matched."
                            ),
                            field_name="quantity",
                        )
                    )

                if matched_qty > Decimal("0"):
                    proceeds = matched_qty * tx.unit_price
                    result.realized_profit += proceeds - cost_consumed
                    result.total_cost_basis += cost_consumed

            elif tx.transaction_type == TransactionType.FEE:
                # A FEE transaction for this asset consumes units from the FIFO
                # queue at zero proceeds — it reduces the remaining position.
                _consume_from_queue(queue, tx.quantity.amount)

            # DEPOSIT, WITHDRAWAL, TRANSFER → skipped (no P&L, no queue change).

        # ── 4. Remaining position ──────────────────────────────────────────
        result.remaining_quantity = sum((entry[0] for entry in queue), Decimal("0"))
        result.remaining_cost_basis = sum(
            (entry[0] * entry[1] for entry in queue), Decimal("0")
        )

        return result, errors

    @staticmethod
    def _make_error(
        job_id: UUID,
        tx: Transaction,
        error_code: str,
        message: str,
        field_name: str | None = None,
    ) -> ValidationError:
        return ValidationError(
            job_id=job_id,
            row_number=0,
            error_code=error_code,
            message=message,
            field_name=field_name,
            raw_row=tx.raw_payload,
        )
