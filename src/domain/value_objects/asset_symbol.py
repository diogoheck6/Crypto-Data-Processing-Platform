from dataclasses import dataclass


@dataclass(frozen=True)
class AssetSymbol:
    """An immutable, normalised asset ticker symbol.

    The symbol is always stored in uppercase regardless of how it was provided.
    This ensures that "btc", "BTC", and "Btc" all resolve to the same identity.

    Examples:
        AssetSymbol("BTC")   # stored as "BTC"
        AssetSymbol("eth")   # stored as "ETH"
        AssetSymbol("")      # raises ValueError
    """

    symbol: str

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str):
            raise TypeError(
                f"AssetSymbol.symbol must be a str, got {type(self.symbol).__name__}"
            )
        if not self.symbol.strip():
            raise ValueError("AssetSymbol.symbol must not be empty")
        # Bypass frozen restriction to normalise to uppercase before the object
        # is handed to the caller. After __post_init__ returns the instance is
        # truly immutable.
        object.__setattr__(self, "symbol", self.symbol.strip().upper())

    def __str__(self) -> str:
        return self.symbol
