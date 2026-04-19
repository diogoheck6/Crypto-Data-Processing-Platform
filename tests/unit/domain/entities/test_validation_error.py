from uuid import UUID, uuid4

from src.domain.entities.validation_error import ValidationError


# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------
def make_error(**overrides) -> ValidationError:
    defaults = dict(
        job_id=uuid4(),
        row_number=1,
        error_code="INVALID_QUANTITY",
        message="Quantity must be greater than zero.",
    )
    return ValidationError(**{**defaults, **overrides})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestValidationErrorCreation:
    """Default values are sensible; required fields must be supplied."""

    def test_id_is_uuid(self):
        error = make_error()
        assert isinstance(error.id, UUID)

    def test_each_instance_gets_unique_id(self):
        e1 = make_error()
        e2 = make_error()
        assert e1.id != e2.id

    def test_field_name_defaults_to_none(self):
        error = make_error()
        assert error.field_name is None

    def test_raw_row_defaults_to_empty_dict(self):
        error = make_error()
        assert error.raw_row == {}

    def test_created_at_is_timezone_aware(self):
        error = make_error()
        assert error.created_at.tzinfo is not None

    def test_required_fields_are_stored_correctly(self):
        jid = uuid4()
        error = make_error(
            job_id=jid,
            row_number=42,
            error_code="MISSING_ASSET",
            message="Asset field is required.",
        )
        assert error.job_id == jid
        assert error.row_number == 42
        assert error.error_code == "MISSING_ASSET"
        assert error.message == "Asset field is required."

    def test_field_name_can_be_set(self):
        error = make_error(field_name="quantity")
        assert error.field_name == "quantity"

    def test_raw_row_can_be_set(self):
        raw = {"qty": "-1", "symbol": "BTCUSDT"}
        error = make_error(raw_row=raw)
        assert error.raw_row == raw


class TestValidationErrorIdentity:
    """Identity is by id only."""

    def test_two_errors_with_same_id_are_equal(self):
        shared_id = uuid4()
        e1 = make_error(id=shared_id)
        e2 = make_error(id=shared_id)
        assert e1 == e2

    def test_two_errors_with_different_ids_are_not_equal(self):
        e1 = make_error()
        e2 = make_error()
        assert e1 != e2

    def test_error_is_not_equal_to_non_error(self):
        error = make_error()
        assert error.__eq__("not an error") is NotImplemented

    def test_error_is_hashable(self):
        error = make_error()
        assert isinstance(hash(error), int)

    def test_same_error_deduplicates_in_set(self):
        shared_id = uuid4()
        e1 = make_error(id=shared_id)
        e2 = make_error(id=shared_id)
        assert len({e1, e2}) == 1
