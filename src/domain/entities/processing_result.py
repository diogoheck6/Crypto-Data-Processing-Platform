"""ProcessingResult — output of the FIFO cost-basis calculation for one asset.

One ProcessingResult is created per asset per job. It holds the realized
profit/loss, the cost basis consumed, and what is still held (unsold).

Design notes:
- Regular (non-frozen) dataclass — the calculator writes fields after creation.
- Identity by UUID id.
- All monetary values are Decimal (always in quote currency; no Money wrapper needed).
- result_payload stores the full FIFO breakdown as a dict for auditability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.value_objects.asset_symbol import AssetSymbol


@dataclass
class ProcessingResult:
    job_id: UUID
    asset: AssetSymbol

    id: UUID = field(default_factory=uuid4)

    realized_profit: Decimal = Decimal("0")
    total_cost_basis: Decimal = Decimal("0")
    remaining_quantity: Decimal = Decimal("0")
    remaining_cost_basis: Decimal = Decimal("0")

    result_payload: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ProcessingResult):
            return self.id == other.id
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.id)
