from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.value_objects.asset_symbol import AssetSymbol
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.transaction_type import TransactionType


@dataclass
class Transaction:
    """Canonical internal representation of a single financial event.

    Created by TransactionNormalizer from raw parsed data.
    Consumed by TransactionValidator, CostBasisCalculator, and repositories.

    Identity is determined by `id` alone — two transactions with the same
    fields but different UUIDs are distinct domain objects.

    Fields map directly to the `transactions` DB table, but use domain types
    instead of raw SQL types (e.g. AssetSymbol instead of VARCHAR).
    """

    # Identity
    id: UUID = field(default_factory=uuid4)
    job_id: UUID = field(default_factory=uuid4)

    # Source tracking
    external_id: str = ""
    source: str = ""  # e.g. "binance_csv"

    # What was traded
    asset: AssetSymbol = field(default_factory=lambda: AssetSymbol("BTC"))
    transaction_type: TransactionType = TransactionType.BUY
    quantity: Quantity = field(default_factory=lambda: Quantity(Decimal("0")))

    # Pricing
    unit_price: Decimal = Decimal("0")  # price per unit in quote currency
    total_value: Decimal = Decimal("0")  # quantity × unit_price

    # Fees (optional — fee may be in a different asset)
    fee_amount: Decimal | None = None
    fee_asset: str | None = None  # raw string — may differ from traded asset

    # Timing — occurred_at is the source event time (historical, not "now").
    # Default is timezone-aware UTC. The normalizer must always override
    # occurred_at with the actual timestamp from the source data.
    # created_at is the system ingestion time — "now" is correct here.
    occurred_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    # Audit
    raw_payload: dict = field(default_factory=dict)  # original CSV row

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transaction):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
