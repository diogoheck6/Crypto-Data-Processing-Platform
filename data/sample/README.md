# Sample Data — Crypto Data Processing Platform

> All data in this directory is **entirely fictional**. It exists solely for testing, development, and demo purposes. No real transaction history is included.

---

## Files

| File                                 | Rows | Purpose                                                         |
| ------------------------------------ | ---- | --------------------------------------------------------------- |
| `binance_spot_trades_valid.csv`      | 10   | Clean happy-path transactions across BTC, ETH, and BNB          |
| `binance_spot_trades_edge_cases.csv` | 9    | Transactions designed to trigger specific validation edge cases |

---

## CSV Format

Both files use the Binance spot trade history export format:

```
Date(UTC),Pair,Side,Price,Executed,Amount,Fee
```

| Column      | Example               | Description                           |
| ----------- | --------------------- | ------------------------------------- |
| `Date(UTC)` | `2024-01-10 10:00:00` | Transaction timestamp in UTC          |
| `Pair`      | `BTCUSDT`             | Trading pair (base + quote asset)     |
| `Side`      | `BUY` or `SELL`       | Trade direction                       |
| `Price`     | `40000.00000000`      | Unit price in quote asset             |
| `Executed`  | `1.00000000 BTC`      | Quantity traded (with asset symbol)   |
| `Amount`    | `40000.00000000 USDT` | Total value (with quote asset symbol) |
| `Fee`       | `40.00000000 USDT`    | Fee charged (with fee asset symbol)   |

---

## binance_spot_trades_valid.csv

A realistic scenario with three assets across multiple buy and sell events.

**Expected FIFO results after processing:**

| Asset | Transactions     | Expected Realized P&L                      |
| ----- | ---------------- | ------------------------------------------ |
| BTC   | 3 buys + 2 sells | Profit (price increased over time)         |
| ETH   | 1 buy + 2 sells  | Mixed (one profitable sell, one at a loss) |
| BNB   | 1 buy + 1 sell   | Loss (sold below cost)                     |

This file is safe to use as the primary demo dataset. Upload it, process it, and the portfolio summary should reflect consistent results.

---

## binance_spot_trades_edge_cases.csv

Designed to verify that the system handles invalid or unusual input gracefully — processing should not crash; it should collect errors and continue.

| Row | Scenario                                          | Expected Behavior                                   |
| --- | ------------------------------------------------- | --------------------------------------------------- |
| 1   | Valid BUY (context for rows below)                | Imported successfully                               |
| 2   | Duplicate of row 1 (same date/pair/side/quantity) | Rejected with `DUPLICATE_TRANSACTION`               |
| 3   | Valid SELL — partially consumes lot from row 1    | Imported and processed correctly                    |
| 4   | SELL exceeds available quantity                   | Partial match + `INSUFFICIENT_QUANTITY` error       |
| 5   | SELL on XRP with no prior BUY                     | Rejected with `NO_PRIOR_COST_BASIS` error           |
| 6   | BUY with quantity = 0                             | Rejected with `ZERO_QUANTITY` error                 |
| 7   | Valid BUY (provides context for row 8)            | Imported successfully                               |
| 8   | SELL with fee in BNB (different from trade asset) | Fee recorded separately; does not affect cost basis |
| 9   | Transactions appear out of chronological order    | System sorts by `Date(UTC)` before processing       |

---

## How to Use

### Upload via API

```bash
# Start the stack first
make up

# Upload the valid sample file
curl -X POST http://localhost:8000/api/v1/imports/csv \
  -F "file=@data/sample/binance_spot_trades_valid.csv"

# Note the job_id returned in the response, then process it
curl -X POST http://localhost:8000/api/v1/process/{job_id}

# View the portfolio summary
curl http://localhost:8000/api/v1/portfolio/summary
```

### Use in Tests

The sample files can be loaded directly in pytest fixtures:

```python
from pathlib import Path

SAMPLE_DIR = Path(__file__).parent.parent.parent / "data" / "sample"

def valid_csv_bytes() -> bytes:
    return (SAMPLE_DIR / "binance_spot_trades_valid.csv").read_bytes()

def edge_case_csv_bytes() -> bytes:
    return (SAMPLE_DIR / "binance_spot_trades_edge_cases.csv").read_bytes()
```
