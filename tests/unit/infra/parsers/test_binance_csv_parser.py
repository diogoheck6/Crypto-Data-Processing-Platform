from typing import Any, cast

from src.infra.parsers.binance_csv_parser import (
    BinanceCsvParser,
    ParseResult,
)

# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

HEADER = "Date(UTC),Pair,Side,Price,Executed,Amount,Fee\n"


def make_csv(*rows: str, header: str = HEADER) -> bytes:
    """Build CSV bytes from a header and zero or more data row strings."""
    return (header + "".join(rows)).encode("utf-8")


def make_bom_csv(*rows: str) -> bytes:
    """Build a BOM-prefixed CSV (utf-8-sig)."""
    return (HEADER + "".join(rows)).encode("utf-8-sig")


VALID_BUY = (
    "2024-01-10 10:00:00,BTCUSDT,BUY,40000.00000000,"
    "1.00000000 BTC,40000.00000000 USDT,40.00000000 USDT\n"
)
VALID_SELL = (
    "2024-02-10 14:00:00,BTCUSDT,SELL,50000.00000000,"
    "0.80000000 BTC,40000.00000000 USDT,40.00000000 USDT\n"
)
VALID_ETH_BUY = (
    "2024-01-25 09:00:00,ETHUSD,BUY,2500.00000000,"
    "2.00000000 ETH,5000.00000000 USDT,5.00000000 USDT\n"
)


# ---------------------------------------------------------------------------
# Return types
# ---------------------------------------------------------------------------


class TestBinanceCsvParserReturnTypes:
    def setup_method(self):
        self.parser = BinanceCsvParser()

    def test_returns_parse_result(self):
        result = self.parser.parse(make_csv(VALID_BUY))
        assert isinstance(result, ParseResult)

    def test_parse_result_has_rows_and_errors(self):
        result = self.parser.parse(make_csv(VALID_BUY))
        assert isinstance(result.rows, list)
        assert isinstance(result.errors, list)

    def test_valid_row_produces_no_errors(self):
        result = self.parser.parse(make_csv(VALID_BUY))
        assert result.errors == []

    def test_valid_row_produces_one_dict(self):
        result = self.parser.parse(make_csv(VALID_BUY))
        assert len(result.rows) == 1


# ---------------------------------------------------------------------------
# Happy path — field mapping
# ---------------------------------------------------------------------------


class TestBinanceCsvParserFieldMapping:
    def setup_method(self):
        self.parser = BinanceCsvParser()

    def _row(self) -> dict[str, Any]:
        return cast(dict[str, Any], self.parser.parse(make_csv(VALID_BUY)).rows[0])

    def test_occurred_at_mapped(self):
        assert self._row()["occurred_at"] == "2024-01-10 10:00:00"

    def test_asset_extracted_from_pair(self):
        assert self._row()["asset"] == "BTC"

    def test_quote_asset_extracted_from_pair(self):
        assert self._row()["quote_asset"] == "USDT"

    def test_transaction_type_is_uppercased(self):
        assert self._row()["transaction_type"] == "BUY"

    def test_unit_price_mapped(self):
        assert self._row()["unit_price"] == "40000.00000000"

    def test_quantity_is_numeric_only(self):
        # "1.00000000 BTC" → "1.00000000"
        assert self._row()["quantity"] == "1.00000000"

    def test_total_value_is_numeric_only(self):
        # "40000.00000000 USDT" → "40000.00000000"
        assert self._row()["total_value"] == "40000.00000000"

    def test_fee_amount_is_numeric_only(self):
        assert self._row()["fee_amount"] == "40.00000000"

    def test_fee_asset_extracted(self):
        assert self._row()["fee_asset"] == "USDT"

    def test_source_is_binance_csv(self):
        assert self._row()["source"] == "binance_csv"

    def test_sell_transaction_type(self):
        row = self.parser.parse(make_csv(VALID_SELL)).rows[0]
        assert row["transaction_type"] == "SELL"

    def test_eth_pair_splits_correctly(self):
        row = self.parser.parse(make_csv(VALID_ETH_BUY)).rows[0]
        assert row["asset"] == "ETH"
        assert row["quote_asset"] == "USD"

    def test_multiple_rows_all_parsed(self):
        result = self.parser.parse(make_csv(VALID_BUY, VALID_SELL))
        assert len(result.rows) == 2

    def test_fee_in_different_asset(self):
        # Fee paid in BNB instead of USDT
        row_csv = (
            "2024-02-05 10:00:00,ETHUSD,BUY,2600.00000000,"
            "1.00000000 ETH,2600.00000000 USDT,0.05000000 BNB\n"
        )
        row = self.parser.parse(make_csv(row_csv)).rows[0]
        assert row["fee_asset"] == "BNB"
        assert row["fee_amount"] == "0.05000000"


# ---------------------------------------------------------------------------
# Fatal errors
# ---------------------------------------------------------------------------


class TestBinanceCsvParserFatalErrors:
    def setup_method(self):
        self.parser = BinanceCsvParser()

    def test_missing_required_column_returns_empty_rows(self):
        bad_header = "Date(UTC),Pair,Side,Price,Executed,Amount\n"  # no Fee
        result = self.parser.parse(make_csv(VALID_BUY, header=bad_header))
        assert result.rows == []

    def test_missing_required_column_returns_one_error(self):
        bad_header = "Date(UTC),Pair,Side,Price,Executed,Amount\n"
        result = self.parser.parse(make_csv(VALID_BUY, header=bad_header))
        assert len(result.errors) == 1

    def test_missing_required_column_error_code(self):
        bad_header = "Date(UTC),Pair,Side,Price,Executed,Amount\n"
        result = self.parser.parse(make_csv(VALID_BUY, header=bad_header))
        assert result.errors[0].error_code == "MISSING_REQUIRED_COLUMNS"

    def test_missing_required_column_error_is_file_level(self):
        bad_header = "Date(UTC),Pair,Side,Price,Executed,Amount\n"
        result = self.parser.parse(make_csv(VALID_BUY, header=bad_header))
        assert result.errors[0].row_number == 0

    def test_empty_file_returns_empty_rows_and_errors(self):
        result = self.parser.parse(b"")
        assert result.rows == []
        assert len(result.errors) == 1
        assert result.errors[0].error_code == "MISSING_REQUIRED_COLUMNS"


# ---------------------------------------------------------------------------
# Non-fatal per-row errors
# ---------------------------------------------------------------------------


class TestBinanceCsvParserRowErrors:
    def setup_method(self):
        self.parser = BinanceCsvParser()

    def test_malformed_price_skips_row_and_records_error(self):
        bad_row = (
            "2024-01-10 10:00:00,BTCUSDT,BUY,NOT_A_NUMBER,"
            "1.00000000 BTC,40000.00000000 USDT,40.00000000 USDT\n"
        )
        result = self.parser.parse(make_csv(bad_row))
        assert result.rows == []
        assert len(result.errors) == 1
        assert result.errors[0].error_code == "ROW_PARSE_ERROR"

    def test_malformed_quantity_skips_row_and_records_error(self):
        bad_row = (
            "2024-01-10 10:00:00,BTCUSDT,BUY,40000.00000000,"
            "BROKEN BTC,40000.00000000 USDT,40.00000000 USDT\n"
        )
        result = self.parser.parse(make_csv(bad_row))
        assert result.rows == []
        assert len(result.errors) == 1

    def test_bad_row_does_not_stop_parsing_other_rows(self):
        bad_row = (
            "2024-01-10 10:00:00,BTCUSDT,BUY,NOT_A_NUMBER,"
            "1.00000000 BTC,40000.00000000 USDT,40.00000000 USDT\n"
        )
        result = self.parser.parse(make_csv(bad_row, VALID_SELL))
        # bad_row is skipped, VALID_SELL is parsed
        assert len(result.rows) == 1
        assert len(result.errors) == 1

    def test_row_error_contains_raw_row(self):
        bad_row = (
            "2024-01-10 10:00:00,BTCUSDT,BUY,NOT_A_NUMBER,"
            "1.00000000 BTC,40000.00000000 USDT,40.00000000 USDT\n"
        )
        result = self.parser.parse(make_csv(bad_row))
        assert result.errors[0].raw_row != {}

    def test_row_error_has_correct_row_number(self):
        # Header is row 1, first data row is row 2.
        bad_row = (
            "2024-01-10 10:00:00,BTCUSDT,BUY,NOT_A_NUMBER,"
            "1.00000000 BTC,40000.00000000 USDT,40.00000000 USDT\n"
        )
        result = self.parser.parse(make_csv(bad_row))
        assert result.errors[0].row_number == 2

    def test_unknown_pair_skips_row_and_records_error(self):
        bad_row = (
            "2024-01-10 10:00:00,UNKNOWNPAIR,BUY,100.00,"
            "1.00 XYZ,100.00 XYZ,0.10 XYZ\n"
        )
        result = self.parser.parse(make_csv(bad_row))
        assert result.rows == []
        assert result.errors[0].error_code == "ROW_PARSE_ERROR"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestBinanceCsvParserEdgeCases:
    def setup_method(self):
        self.parser = BinanceCsvParser()

    def test_bom_encoded_file_parsed_correctly(self):
        result = self.parser.parse(make_bom_csv(VALID_BUY))
        assert len(result.rows) == 1
        assert result.errors == []

    def test_header_only_file_returns_empty_rows_no_errors(self):
        result = self.parser.parse(make_csv())  # no data rows
        assert result.rows == []
        assert result.errors == []

    def test_blank_row_with_newline_is_silently_skipped(self):
        result = self.parser.parse(make_csv(VALID_BUY, "\n", VALID_SELL))
        assert len(result.rows) == 2
        assert result.errors == []

    def test_blank_row_with_only_commas_is_silently_skipped(self):
        # A row of only commas (all fields empty) must be skipped silently.
        # DictReader returns it as a row with empty string values — our
        # blank-row guard on line 132 catches this case.
        comma_row = ",,,,,,\n"
        result = self.parser.parse(make_csv(VALID_BUY, comma_row, VALID_SELL))
        assert len(result.rows) == 2
        assert result.errors == []

    def test_extra_unknown_columns_are_ignored(self):
        extra_header = "Date(UTC),Pair,Side,Price,Executed,Amount,Fee,ExtraCol\n"
        extra_row = (
            "2024-01-10 10:00:00,BTCUSDT,BUY,40000.00000000,"
            "1.00000000 BTC,40000.00000000 USDT,40.00000000 USDT,ignored\n"
        )
        result = self.parser.parse(make_csv(extra_row, header=extra_header))
        assert len(result.rows) == 1
        assert result.errors == []

    def test_amount_with_too_many_tokens_records_error(self):
        # "1.00000000 BTC extra" has 3 tokens — triggers the else branch
        # in _split_amount (lines 215-218).
        bad_row = (
            "2024-01-10 10:00:00,BTCUSDT,BUY,40000.00000000,"
            "1.00000000 BTC extra,40000.00000000 USDT,40.00000000 USDT\n"
        )
        result = self.parser.parse(make_csv(bad_row))
        assert result.rows == []
        assert result.errors[0].error_code == "ROW_PARSE_ERROR"

    def test_amount_with_no_unit_suffix_is_accepted(self):
        # Fee field contains a bare number with no unit (e.g. "40.00000000").
        # _split_amount must handle this via the elif len(parts)==1 branch.
        row_csv = (
            "2024-01-10 10:00:00,BTCUSDT,BUY,40000.00000000,"
            "1.00000000 BTC,40000.00000000 USDT,40.00000000\n"
        )
        result = self.parser.parse(make_csv(row_csv))
        assert len(result.rows) == 1
        assert result.rows[0]["fee_amount"] == "40.00000000"
        assert result.rows[0]["fee_asset"] == ""
