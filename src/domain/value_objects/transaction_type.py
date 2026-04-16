from enum import Enum


class TransactionType(str, Enum):
    """Canonical set of transaction types recognised by the domain.

    Inherits from str so values can be compared directly to strings
    (e.g. from a CSV column) without an explicit .value lookup.
    """

    BUY = "BUY"
    SELL = "SELL"
    FEE = "FEE"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
