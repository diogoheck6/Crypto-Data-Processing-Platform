"""TransactionNormalizer — maps a raw dict to a Transaction domain entity.

Sits at the boundary between untyped data (from any source: CSV, JSON, API)
and the domain model. Once normalization succeeds, all downstream services
work exclusively with typed domain objects.

Raw dict key contract:
    Required: asset, transaction_type, quantity, unit_price, total_value, occurred_at
    Optional: external_id, source, fee_amount, fee_asset
    Unknown keys are silently ignored.

All normalization failures raise ValueError with a descriptive message.
The use case layer is responsible for catching these and recording them
as ValidationError objects — the normalizer itself does not persist anything.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from src.domain.entities.transaction import Transaction
from src.domain.value_objects.asset_symbol import AssetSymbol
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.transaction_type import TransactionType

_REQUIRED_FIELDS = frozenset(
    {
        "asset",
        "transaction_type",
        "quantity",
        "unit_price",
        "total_value",
        "occurred_at",
    }
)


class TransactionNormalizer:

    def normalize(self, raw: dict) -> Transaction:
        """Convert a raw dict into a typed Transaction.

        Raises:
            ValueError: if any required field is missing or any value cannot
                        be converted to the expected domain type.
        """
        missing = _REQUIRED_FIELDS - raw.keys()
        if missing:
            raise ValueError(f"Missing required fields: {sorted(missing)}")

        asset = self._parse_asset(raw["asset"])
        transaction_type = self._parse_transaction_type(raw["transaction_type"])
        quantity = self._parse_quantity(raw["quantity"])
        unit_price = self._parse_decimal(raw["unit_price"], "unit_price")
        total_value = self._parse_decimal(raw["total_value"], "total_value")
        occurred_at = self._parse_datetime(raw["occurred_at"])

        fee_amount: Decimal | None = None
        if raw.get("fee_amount") is not None:
            fee_amount = self._parse_decimal(raw["fee_amount"], "fee_amount")

        return Transaction(
            external_id=str(raw.get("external_id", "")),
            source=str(raw.get("source", "")),
            asset=asset,
            transaction_type=transaction_type,
            quantity=quantity,
            unit_price=unit_price,
            total_value=total_value,
            fee_amount=fee_amount,
            fee_asset=raw.get("fee_asset"),
            occurred_at=occurred_at,
            raw_payload=dict(raw),
        )

    # ------------------------------------------------------------------
    # Private parsing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_asset(value: object) -> AssetSymbol:
        try:
            return AssetSymbol(str(value))
        except ValueError as exc:
            raise ValueError(f"Invalid asset {value!r}: {exc}") from exc

    @staticmethod
    def _parse_transaction_type(value: object) -> TransactionType:
        try:
            return TransactionType(str(value).strip().upper())
        except ValueError:
            raise ValueError(
                f"Invalid transaction_type {value!r}. "
                f"Allowed values: {[t.value for t in TransactionType]}"
            ) from None

    @staticmethod
    def _parse_quantity(value: object) -> Quantity:
        try:
            return Quantity(Decimal(str(value)))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Invalid quantity {value!r}: {exc}") from exc

    @staticmethod
    def _parse_decimal(value: object, field_name: str) -> Decimal:
        try:
            return Decimal(str(value))
        except InvalidOperation as exc:
            raise ValueError(f"Invalid {field_name} {value!r}: {exc}") from exc

    @staticmethod
    def _parse_datetime(value: object) -> datetime:
        try:
            dt = datetime.fromisoformat(str(value))
        except ValueError as exc:
            raise ValueError(f"Invalid occurred_at {value!r}: {exc}") from exc
        # If the source provides a naive datetime, assume UTC.
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt
