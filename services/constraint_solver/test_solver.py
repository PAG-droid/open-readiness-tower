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


if __name__ == "__main__":
    unittest.main()
