"""BinanceCsvParser — converts raw Binance spot-trade CSV bytes into
normalizer-ready row dicts plus a list of parse errors.

Sits in `src/infra/parsers/` because it depends on an external data format
(Binance CSV) and uses the stdlib `csv` module. The domain layer never sees
this class — it only ever receives the plain dicts this parser produces.

Output contract:
    Each successful row dict contains exactly these keys, ready for
    TransactionNormalizer.normalize():

        occurred_at     (str)  — e.g. "2024-01-10 10:00:00"
        asset           (str)  — e.g. "BTC"
        quote_asset     (str)  — e.g. "USDT"
        transaction_type (str) — "BUY" or "SELL"
        unit_price      (str)  — numeric string
        quantity        (str)  — numeric string (executed amount, no unit)
        total_value     (str)  — numeric string (quote amount, no unit)
        fee_amount      (str)  — numeric string
        fee_asset       (str)  — e.g. "USDT"
        source          (str)  — always "binance_csv"

Fatal vs non-fatal errors:
    - Missing required column: FATAL  → ParseResult(rows=[], errors=[one error])
    - Empty file (no data rows): OK   → ParseResult(rows=[], errors=[])
    - Malformed row (bad number, unparseable field): NON-FATAL → row skipped, error appended
    - Completely blank row: silently skipped, no error
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Data transfer objects
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = frozenset(
    {"Date(UTC)", "Pair", "Side", "Price", "Executed", "Amount", "Fee"}
)

# Known quote-asset suffixes in order of length (longest first) so that
# USDT is tried before USD when a pair ends with both.
_KNOWN_QUOTES = [
    "USDT",
    "BUSD",
    "USDC",
    "TUSD",
    "BTC",
    "ETH",
    "BNB",
    "USD",
    "EUR",
    "GBP",
    "AUD",
    "TRY",
]


@dataclass
class ParseError:
    """A single parse failure, tied to an optional source row."""

    row_number: int  # 1-based; 0 = file-level error
    error_code: str
    message: str
    raw_row: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParseResult:
    """Return type of BinanceCsvParser.parse()."""

    rows: list[dict[str, Any]] = field(default_factory=list)
    errors: list[ParseError] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


class BinanceCsvParser:
    """Parse Binance spot-trade CSV exports into normalizer-ready dicts.

    Usage:
        parser = BinanceCsvParser()
        result = parser.parse(csv_bytes)
    """

    def parse(self, content: bytes) -> ParseResult:
        """Convert raw CSV bytes into a ParseResult.

        Args:
            content: Raw bytes of a Binance spot-trade CSV export. BOM
                     encoding (`utf-8-sig`) is handled transparently.

        Returns:
            ParseResult with `rows` for successfully parsed records and
            `errors` for any issues encountered.
        """
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        # ── fatal check: required columns must all be present ─────────────
        # DictReader.fieldnames is None before first iteration if the file is
        # completely empty; treat that the same as missing columns.
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            return ParseResult(
                rows=[],
                errors=[
                    ParseError(
                        row_number=0,
                        error_code="MISSING_REQUIRED_COLUMNS",
                        message=(
                            f"CSV is missing required columns: " f"{sorted(missing)}"
                        ),
                    )
                ],
            )

        rows: list[dict[str, Any]] = []
        errors: list[ParseError] = []

        for csv_row_number, raw in enumerate(reader, start=2):  # row 1 = header
            # Skip entirely blank rows.
            if not any(v and v.strip() for v in raw.values()):
                continue

            try:
                row = self._parse_row(raw)
            except ValueError as exc:
                errors.append(
                    ParseError(
                        row_number=csv_row_number,
                        error_code="ROW_PARSE_ERROR",
                        message=str(exc),
                        raw_row=dict(raw),
                    )
                )
                continue

            rows.append(row)

        return ParseResult(rows=rows, errors=errors)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_row(self, raw: dict) -> dict:
        """Convert one CSV row dict into a normalizer-ready dict.

        Raises:
            ValueError: if any field value cannot be parsed.
        """
        asset, quote_asset = self._split_pair(raw["Pair"].strip())
        quantity_str, _qty_unit = self._split_amount(
            raw["Executed"].strip(), "Executed"
        )
        total_value_str, _total_unit = self._split_amount(
            raw["Amount"].strip(), "Amount"
        )
        fee_str, fee_asset = self._split_amount(raw["Fee"].strip(), "Fee")
        unit_price_str = self._parse_number(raw["Price"].strip(), "Price")

        return {
            "occurred_at": raw["Date(UTC)"].strip(),
            "asset": asset,
            "quote_asset": quote_asset,
            "transaction_type": raw["Side"].strip().upper(),
            "unit_price": unit_price_str,
            "quantity": quantity_str,
            "total_value": total_value_str,
            "fee_amount": fee_str,
            "fee_asset": fee_asset,
            "source": "binance_csv",
        }

    @staticmethod
    def _split_pair(pair: str) -> tuple[str, str]:
        """Split 'BTCUSDT' into ('BTC', 'USDT').

        Tries known quote suffixes in order (longest first).

        Raises:
            ValueError: if no known quote suffix matches.
        """
        pair_upper = pair.upper()
        for quote in _KNOWN_QUOTES:
            if pair_upper.endswith(quote):
                asset = pair_upper[: -len(quote)]
                if asset:
                    return asset, quote
        raise ValueError(
            f"Cannot split pair {pair!r}: no known quote asset suffix found."
        )

    @staticmethod
    def _split_amount(value: str, field_name: str) -> tuple[str, str]:
        """Split '1.00000000 BTC' into ('1.00000000', 'BTC').

        Also handles plain numeric strings (no unit), returning ('number', '').

        Raises:
            ValueError: if the numeric part cannot be parsed.
        """
        parts = value.split()
        if len(parts) == 2:
            numeric, unit = parts
        elif len(parts) == 1:
            numeric, unit = parts[0], ""
        else:
            raise ValueError(
                f"Cannot parse {field_name} value {value!r}: "
                f"expected 'number' or 'number UNIT'."
            )
        # Validate numeric part.
        try:
            float(numeric)
        except ValueError:
            raise ValueError(
                f"Non-numeric value in {field_name}: {numeric!r}."
            ) from None
        return numeric, unit

    @staticmethod
    def _parse_number(value: str, field_name: str) -> str:
        """Validate that `value` is a numeric string and return it as-is.

        Raises:
            ValueError: if the value is not numeric.
        """
        try:
            float(value)
        except ValueError:
            raise ValueError(f"Non-numeric value in {field_name}: {value!r}.") from None
        return value
