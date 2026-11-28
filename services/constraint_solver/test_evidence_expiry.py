from datetime import UTC, datetime, timedelta, timezone

import pytest

from open_readiness_schemas.models import CandidateIntervention, ManufacturingCapacitySlot, SlotStatus
from services.constraint_solver import solver as solver_module
from services.constraint_solver.solver import BioreactorAllocationSolver


NOW = datetime(2026, 11, 27, tzinfo=UTC)


def candidate(candidate_id="candidate"):
    return CandidateIntervention(
        candidate_id=candidate_id, threat_pathogen_family="synthetic-family",
        platform="MRNA", target_dose_count=100,
        bioreactor_volume_liters_required=10, storage_temp_celsius=-80,
        regulatory_target_regions=["WHO"],
    )


def slot(expiry, **overrides):
    values = dict(
        slot_id="slot", facility_id="synthetic-facility", facility_country="DE",
        supported_platforms=["MRNA"], bioreactor_capacity_liters=20,
        window_start=NOW, window_end=NOW + timedelta(days=1),
        evidence_hash="synthetic-placeholder", evidence_expires_at=expiry,
    )
    return ManufacturingCapacitySlot(**(values | overrides))


@pytest.mark.parametrize("delta,expected", [(-1, False), (0, False), (1, True)])
def test_expiry_boundary_is_exclusive(delta, expected):
    result = BioreactorAllocationSolver.solve(
        [candidate()], [slot(NOW + timedelta(microseconds=delta))], as_of=NOW,
    )
    assert result.is_feasible is expected
    assert result.allocations == ({"candidate": "slot"} if expected else {})
    assert result.unallocated_candidates == ([] if expected else ["candidate"])
    assert len(result.conflicts) == (0 if expected else 1)


@pytest.mark.parametrize("status", [s for s in SlotStatus if s != SlotStatus.AVAILABLE])
def test_fresh_evidence_does_not_override_unavailable_status(status):
    result = BioreactorAllocationSolver.solve(
        [candidate()], [slot(NOW + timedelta(days=1), status=status)], as_of=NOW,
    )
    assert not result.is_feasible
    assert result.allocations == {}


@pytest.mark.parametrize("as_of", [NOW.replace(tzinfo=None), NOW.astimezone(timezone(timedelta(hours=-5)))])
def test_equivalent_evaluation_times_have_identical_boundary(as_of):
    assert not BioreactorAllocationSolver.solve([candidate()], [slot(NOW)], as_of=as_of).is_feasible


def test_legacy_naive_evidence_is_treated_as_utc():
    result = BioreactorAllocationSolver.solve(
        [candidate()], [slot((NOW + timedelta(seconds=1)).replace(tzinfo=None))], as_of=NOW,
    )
    assert result.is_feasible


def test_default_evaluation_time_uses_current_utc(monkeypatch):
    class FixedClock(datetime):
        @classmethod
        def now(cls, tz=None):
            assert tz is UTC
            return NOW

    monkeypatch.setattr(solver_module, "datetime", FixedClock)
    assert not BioreactorAllocationSolver.solve([candidate()], [slot(NOW)]).is_feasible
    assert BioreactorAllocationSolver.solve([candidate()], [slot(NOW + timedelta(seconds=1))]).is_feasible


@pytest.mark.parametrize("overrides", [{"supported_platforms": ["VIRAL_VECTOR"]}, {"bioreactor_capacity_liters": 5}])
def test_freshness_does_not_bypass_platform_or_volume_constraints(overrides):
    result = BioreactorAllocationSolver.solve(
        [candidate()], [slot(NOW + timedelta(days=1), **overrides)], as_of=NOW,
    )
    assert not result.is_feasible


def test_stale_slot_cannot_resolve_contention_over_one_fresh_slot():
    result = BioreactorAllocationSolver.solve(
        [candidate("a"), candidate("b")],
        [slot(NOW, slot_id="stale"), slot(NOW + timedelta(days=1), slot_id="fresh")],
        as_of=NOW,
    )
    assert len(result.allocations) == 1
    assert set(result.allocations.values()) == {"fresh"}
    assert len(result.unallocated_candidates) == 1
    assert not result.is_feasible
