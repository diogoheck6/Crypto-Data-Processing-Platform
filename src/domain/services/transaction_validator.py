"""TransactionValidator — applies business rules to a normalised Transaction.

Receives a Transaction that has already been produced by TransactionNormalizer
and checks whether its values satisfy domain business rules.

Returns a list of ValidationError objects — one per failing rule.
An empty list means the transaction is valid.

This service never raises — it accumulates all errors so the caller sees
every problem with a row in a single pass.

Responsibility boundary:
    - TransactionNormalizer : "can these raw strings be parsed into domain types?"
    - TransactionValidator  : "do the domain values satisfy business rules?"
    - Use cases             : "what do I do with invalid transactions?"

The validator is stateful for one reason: duplicate detection within a batch.
Create a fresh TransactionValidator instance per processing job.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from src.domain.entities.transaction import Transaction
from src.domain.entities.validation_error import ValidationError
from src.domain.value_objects.transaction_type import TransactionType

# Types that represent a trade — price and quantity must be non-zero.
_TRADE_TYPES = frozenset({TransactionType.BUY, TransactionType.SELL})


class TransactionValidator:

    def __init__(self) -> None:
        # Tracks (external_id, source) pairs seen so far in this job.
        self._seen_external_ids: set[tuple[str, str]] = set()

    def validate(
        self, transaction: Transaction, row_number: int
    ) -> list[ValidationError]:
        """Check all business rules for a single transaction.

        Args:
            transaction: A fully normalised Transaction domain object.
            row_number:  The 1-based row number from the source file,
                         used to populate ValidationError for traceability.

        Returns:
            A list of ValidationError objects — empty if the transaction is valid.
        """
        errors: list[ValidationError] = []

        if transaction.transaction_type in _TRADE_TYPES:
            self._check_zero_quantity(transaction, row_number, errors)
            self._check_unit_price(transaction, row_number, errors)
            self._check_total_value(transaction, row_number, errors)

        self._check_future_date(transaction, row_number, errors)
        self._check_duplicate(transaction, row_number, errors)

        return errors

    # ------------------------------------------------------------------
    # Rule implementations
    # ------------------------------------------------------------------

    @staticmethod
    def _make_error(
        transaction: Transaction,
        row_number: int,
        error_code: str,
        message: str,
        field_name: str | None = None,
    ) -> ValidationError:
        return ValidationError(
            job_id=transaction.job_id,
            row_number=row_number,
            error_code=error_code,
            message=message,
            field_name=field_name,
            raw_row=transaction.raw_payload,
        )

    def _check_zero_quantity(
        self,
        transaction: Transaction,
        row_number: int,
        errors: list[ValidationError],
    ) -> None:
        if transaction.quantity.is_zero():
            errors.append(
                self._make_error(
                    transaction,
                    row_number,
                    error_code="ZERO_QUANTITY",
                    message=(
                        f"Quantity must be greater than zero for "
                        f"{transaction.transaction_type.value} transactions."
                    ),
                    field_name="quantity",
                )
            )

    def _check_unit_price(
        self,
        transaction: Transaction,
        row_number: int,
        errors: list[ValidationError],
    ) -> None:
        if transaction.unit_price <= Decimal("0"):
            errors.append(
                self._make_error(
                    transaction,
                    row_number,
                    error_code="INVALID_UNIT_PRICE",
                    message=(
                        f"unit_price must be greater than zero for "
                        f"{transaction.transaction_type.value} transactions, "
                        f"got {transaction.unit_price}."
                    ),
                    field_name="unit_price",
                )
            )

    def _check_total_value(
        self,
        transaction: Transaction,
        row_number: int,
        errors: list[ValidationError],
    ) -> None:
        if transaction.total_value <= Decimal("0"):
            errors.append(
                self._make_error(
                    transaction,
                    row_number,
                    error_code="INVALID_TOTAL_VALUE",
                    message=(
                        f"total_value must be greater than zero for "
                        f"{transaction.transaction_type.value} transactions, "
                        f"got {transaction.total_value}."
                    ),
                    field_name="total_value",
                )
            )

    def _check_future_date(
        self,
        transaction: Transaction,
        row_number: int,
        errors: list[ValidationError],
    ) -> None:
        if transaction.occurred_at > datetime.now(tz=UTC):
            errors.append(
                self._make_error(
                    transaction,
                    row_number,
                    error_code="FUTURE_DATE",
                    message=(
                        f"occurred_at {transaction.occurred_at.isoformat()} "
                        f"is in the future."
                    ),
                    field_name="occurred_at",
                )
            )

    def _check_duplicate(
        self,
        transaction: Transaction,
        row_number: int,
        errors: list[ValidationError],
    ) -> None:
        if not transaction.external_id:
            return
        key = (transaction.external_id, transaction.source)
        if key in self._seen_external_ids:
            errors.append(
                self._make_error(
                    transaction,
                    row_number,
                    error_code="DUPLICATE_EXTERNAL_ID",
                    message=(
                        f"Transaction with external_id={transaction.external_id!r} "
                        f"and source={transaction.source!r} has already been seen "
                        f"in this batch."
                    ),
                    field_name=None,
                )
            )
        else:
            self._seen_external_ids.add(key)
