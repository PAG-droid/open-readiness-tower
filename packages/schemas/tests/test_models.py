from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from open_readiness_schemas.models import CandidateIntervention, ManufacturingCapacitySlot


def candidate_data():
    return dict(
        candidate_id="synthetic-candidate", threat_pathogen_family="synthetic-family",
        platform="MRNA", target_dose_count=100,
        bioreactor_volume_liters_required=10, storage_temp_celsius=-80,
        regulatory_target_regions=["WHO"],
    )


def slot_data():
    return dict(
        slot_id="synthetic-slot", facility_id="synthetic-facility", facility_country="DE",
        supported_platforms=["MRNA"], bioreactor_capacity_liters=20,
        window_start="2026-12-01T00:00:00", window_end="2026-12-02T00:00:00Z",
        evidence_hash="synthetic-placeholder", evidence_expires_at="2026-12-03T00:00:00+00:00",
    )


@pytest.mark.parametrize("field", ["target_dose_count", "bioreactor_volume_liters_required"])
@pytest.mark.parametrize("value", [0, -1])
def test_candidate_rejects_nonpositive_quantities(field, value):
    with pytest.raises(ValidationError) as exc:
        CandidateIntervention(**(candidate_data() | {field: value}))
    assert exc.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan")])
def test_slot_rejects_invalid_capacity(value):
    with pytest.raises(ValidationError):
        ManufacturingCapacitySlot(**(slot_data() | {"bioreactor_capacity_liters": value}))


@pytest.mark.parametrize("value", [float("inf"), float("nan")])
def test_candidate_rejects_nonfinite_volume(value):
    with pytest.raises(ValidationError):
        CandidateIntervention(**(candidate_data() | {"bioreactor_volume_liters_required": value}))


def test_positive_quantities_and_negative_storage_temperature_remain_valid():
    assert CandidateIntervention(**candidate_data()).storage_temp_celsius == -80
    assert ManufacturingCapacitySlot(**slot_data()).bioreactor_capacity_liters == 20


@pytest.mark.parametrize("end", ["2026-12-01T00:00:00Z", "2026-11-30T23:59:59Z", "2026-12-01T01:00:00+01:00"])
def test_window_must_end_after_start_in_utc(end):
    with pytest.raises(ValidationError, match="window_end must be after window_start"):
        ManufacturingCapacitySlot(**(slot_data() | {"window_end": end}))


def test_mixed_naive_and_offset_timestamps_normalize_to_utc():
    slot = ManufacturingCapacitySlot(**(slot_data() | {
        "window_end": "2026-12-01T02:00:00+01:00",
        "evidence_expires_at": "2026-12-02T23:00:00-01:00",
    }))
    assert slot.window_start == datetime(2026, 12, 1, tzinfo=UTC)
    assert slot.window_end == datetime(2026, 12, 1, 1, tzinfo=UTC)
    assert slot.evidence_expires_at == datetime(2026, 12, 3, tzinfo=UTC)
    assert all(value.tzinfo is UTC for value in (slot.window_start, slot.window_end, slot.evidence_expires_at))


@pytest.mark.parametrize("field", ["window_start", "window_end", "evidence_expires_at"])
def test_invalid_timestamp_has_field_validation_error(field):
    with pytest.raises(ValidationError) as exc:
        ManufacturingCapacitySlot(**(slot_data() | {field: "not-a-timestamp"}))
    assert exc.value.errors()[0]["loc"] == (field,)
