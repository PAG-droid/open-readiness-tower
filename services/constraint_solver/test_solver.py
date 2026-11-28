import unittest
from datetime import datetime, timedelta
from open_readiness_schemas.models import CandidateIntervention, ManufacturingCapacitySlot, ProductionPlatform, SlotStatus
from services.constraint_solver.solver import BioreactorAllocationSolver


class TestBioreactorAllocationSolver(unittest.TestCase):
    def test_slot_collision_resolution(self):
        cand_1 = CandidateIntervention(
            candidate_id="cand_vax_alpha",
            threat_pathogen_family="Henipavirus",
            platform=ProductionPlatform.MRNA,
            target_dose_count=1_000_000,
            bioreactor_volume_liters_required=2000.0,
            storage_temp_celsius=-80.0,
            regulatory_target_regions=["WHO"]
        )
        cand_2 = CandidateIntervention(
            candidate_id="cand_vax_beta",
            threat_pathogen_family="Arenaviridae",
            platform=ProductionPlatform.MRNA,
            target_dose_count=2_000_000,
            bioreactor_volume_liters_required=2000.0,
            storage_temp_celsius=-80.0,
            regulatory_target_regions=["EMA"]
        )

        now = datetime.utcnow()
        slot_single = ManufacturingCapacitySlot(
            slot_id="slot_bioreactor_01",
            facility_id="facility_north_01",
            facility_country="DE",
            supported_platforms=[ProductionPlatform.MRNA],
            bioreactor_capacity_liters=2000.0,
            window_start=now + timedelta(days=10),
            window_end=now + timedelta(days=40),
            status=SlotStatus.AVAILABLE,
            evidence_hash="sha256_mock_proof_slot1",
            evidence_expires_at=now + timedelta(days=90)
        )

        result = BioreactorAllocationSolver.solve([cand_1, cand_2], [slot_single])

        self.assertEqual(len(result.allocations), 1)
        self.assertEqual(len(result.unallocated_candidates), 1)
        self.assertFalse(result.is_feasible)
        self.assertEqual(len(result.conflicts), 1)

    def test_empty_candidates_and_empty_slots(self):
        result = BioreactorAllocationSolver.solve([], [])

        self.assertTrue(result.is_feasible)
        self.assertEqual(result.allocations, {})
        self.assertEqual(result.unallocated_candidates, [])
        self.assertEqual(result.conflicts, [])

    def test_empty_candidates_with_available_slots(self):
        now = datetime.utcnow()
        slot = ManufacturingCapacitySlot(
            slot_id="slot_empty_test_01",
            facility_id="facility_north_01",
            facility_country="DE",
            supported_platforms=[ProductionPlatform.MRNA],
            bioreactor_capacity_liters=2000.0,
            window_start=now + timedelta(days=10),
            window_end=now + timedelta(days=40),
            status=SlotStatus.AVAILABLE,
            evidence_hash="sha256_mock_proof_slot_empty",
            evidence_expires_at=now + timedelta(days=90),
        )

        result = BioreactorAllocationSolver.solve([], [slot])

        self.assertTrue(result.is_feasible)
        self.assertEqual(result.allocations, {})
        self.assertEqual(result.unallocated_candidates, [])
        self.assertEqual(result.conflicts, [])

    def test_candidates_with_no_slots(self):
        cand_1 = CandidateIntervention(
            candidate_id="cand_no_slot_alpha",
            threat_pathogen_family="Henipavirus",
            platform=ProductionPlatform.MRNA,
            target_dose_count=1_000_000,
            bioreactor_volume_liters_required=2000.0,
            storage_temp_celsius=-80.0,
            regulatory_target_regions=["WHO"],
        )
        cand_2 = CandidateIntervention(
            candidate_id="cand_no_slot_beta",
            threat_pathogen_family="Arenaviridae",
            platform=ProductionPlatform.VIRAL_VECTOR,
            target_dose_count=500_000,
            bioreactor_volume_liters_required=1000.0,
            storage_temp_celsius=-20.0,
            regulatory_target_regions=["EMA"],
        )

        result = BioreactorAllocationSolver.solve([cand_1, cand_2], [])

        self.assertFalse(result.is_feasible)
        self.assertEqual(result.allocations, {})
        self.assertEqual(
            set(result.unallocated_candidates),
            {"cand_no_slot_alpha", "cand_no_slot_beta"},
        )
        self.assertEqual(len(result.conflicts), 2)
        for cid in ("cand_no_slot_alpha", "cand_no_slot_beta"):
            self.assertEqual(sum(1 for conflict in result.conflicts if cid in conflict), 1)


if __name__ == "__main__":
    unittest.main()
