from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.entities.processing_result import ProcessingResult
from src.domain.value_objects.asset_symbol import AssetSymbol

# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------


def make_result(**overrides) -> ProcessingResult:
    defaults = dict(
        job_id=uuid4(),
        asset=AssetSymbol("BTC"),
    )
    return ProcessingResult(**{**defaults, **overrides})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestProcessingResultCreation:
    """Default values are zero; required fields must be supplied."""

    def test_id_is_uuid(self):
        result = make_result()
        assert isinstance(result.id, UUID)

    def test_each_instance_gets_unique_id(self):
        r1 = make_result()
        r2 = make_result()
        assert r1.id != r2.id

    def test_decimal_fields_default_to_zero(self):
        result = make_result()
        assert result.realized_profit == Decimal("0")
        assert result.total_cost_basis == Decimal("0")
        assert result.remaining_quantity == Decimal("0")
        assert result.remaining_cost_basis == Decimal("0")

    def test_result_payload_defaults_to_empty_dict(self):
        result = make_result()
        assert result.result_payload == {}

    def test_created_at_is_timezone_aware(self):
        result = make_result()
        assert result.created_at.tzinfo is not None

    def test_job_id_is_stored_correctly(self):
        jid = uuid4()
        result = make_result(job_id=jid)
        assert result.job_id == jid

    def test_asset_is_stored_correctly(self):
        result = make_result(asset=AssetSymbol("ETH"))
        assert result.asset == AssetSymbol("ETH")


class TestProcessingResultIdentity:
    """Identity is by id only."""

    def test_two_results_with_same_id_are_equal(self):
        shared_id = uuid4()
        r1 = make_result(id=shared_id)
        r2 = make_result(id=shared_id)
        assert r1 == r2

    def test_two_results_with_different_ids_are_not_equal(self):
        r1 = make_result()
        r2 = make_result()
        assert r1 != r2

    def test_result_is_not_equal_to_non_result(self):
        result = make_result()
        assert result.__eq__("not a result") is NotImplemented

    def test_result_is_hashable(self):
        result = make_result()
        assert isinstance(hash(result), int)

    def test_same_result_deduplicates_in_set(self):
        shared_id = uuid4()
        r1 = make_result(id=shared_id)
        r2 = make_result(id=shared_id)
        assert len({r1, r2}) == 1


class TestProcessingResultMutability:
    """The calculator writes fields after creation — entity must be mutable."""

    def test_realized_profit_can_be_updated(self):
        result = make_result()
        result.realized_profit = Decimal("500.00")
        assert result.realized_profit == Decimal("500.00")

    def test_remaining_quantity_can_be_updated(self):
        result = make_result()
        result.remaining_quantity = Decimal("0.25")
        assert result.remaining_quantity == Decimal("0.25")

    def test_result_payload_can_be_updated(self):
        result = make_result()
        result.result_payload = {"lots": [{"qty": "0.5", "cost": "15000"}]}
        assert "lots" in result.result_payload
