from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """An immutable monetary value with a currency denomination.

    Rules:
    - amount must be a Decimal and strictly greater than zero.
    - currency must be a non-empty string; stored normalised to uppercase.
    - Two Money instances can only be added if they share the same currency.

    Examples:
        Money(Decimal("150.00"), "USD")   # valid
        Money(Decimal("0"), "USD")        # raises ValueError — zero not allowed
        Money(Decimal("-1"), "USD")       # raises ValueError — negative not allowed
        Money(Decimal("1"), "")           # raises ValueError — empty currency
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError(
                f"Money.amount must be a Decimal, got {type(self.amount).__name__}"
            )
        if self.amount <= Decimal("0"):
            raise ValueError(f"Money.amount must be > 0, got {self.amount}")
        if not isinstance(self.currency, str):
            raise TypeError(
                f"Money.currency must be a str, got {type(self.currency).__name__}"
            )
        if not self.currency.strip():
            raise ValueError("Money.currency must not be empty")
        object.__setattr__(self, "currency", self.currency.strip().upper())

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add Money with different currencies: "
                f"{self.currency} and {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
