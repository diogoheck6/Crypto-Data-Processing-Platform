from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Quantity:
    """An immutable, non-negative amount of an asset.

    Zero is valid — it represents an exhausted or empty position.
    Negative values are a domain error and are rejected at construction time.

    Examples:
        Quantity(Decimal("0.5"))   # 0.5 units
        Quantity(Decimal("0"))     # valid — empty position
        Quantity(Decimal("-1"))    # raises ValueError
    """

    amount: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError(
                f"Quantity.amount must be a Decimal, got {type(self.amount).__name__}"
            )
        if self.amount < Decimal("0"):
            raise ValueError(f"Quantity.amount must be >= 0, got {self.amount}")

    def __add__(self, other: "Quantity") -> "Quantity":
        return Quantity(self.amount + other.amount)

    def __sub__(self, other: "Quantity") -> "Quantity":
        """Subtract two quantities. Raises ValueError if result would be negative."""
        result = self.amount - other.amount
        return Quantity(result)  # delegates negative check to __post_init__

    def is_zero(self) -> bool:
        return self.amount == Decimal("0")
