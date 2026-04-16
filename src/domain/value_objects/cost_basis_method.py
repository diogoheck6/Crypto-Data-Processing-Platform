from enum import Enum


class CostBasisMethod(str, Enum):
    """Supported cost basis accounting methods.

    Only FIFO is implemented in the MVP.
    WEIGHTED_AVERAGE is reserved for Phase 9.
    """

    FIFO = "FIFO"
    WEIGHTED_AVERAGE = "WEIGHTED_AVERAGE"
