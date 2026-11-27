import os
import json
import sys
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../packages/schemas")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../packages/fsm_engine")))

from open_readiness_schemas.models import CandidateIntervention, ManufacturingCapacitySlot, ActionRecord, ActionState
from open_readiness_fsm.engine import ActionStateMachine
from services.constraint_solver.solver import BioreactorAllocationSolver


def main():
    print("==========================================================")
    print("  OPEN READINESS CONTROL TOWER - REPLAY SIMULATION ENGINE ")
    print("==========================================================")

    fixture_path = os.path.join(os.path.dirname(__file__), "../fixtures/mock_data.json")
    with open(fixture_path, "r") as f:
        data = json.load(f)

    candidates = [CandidateIntervention(**c) for c in data["candidates"]]
    slots = [ManufacturingCapacitySlot(**s) for s in data["slots"]]

    print(f"[T+00 Days] Ingested {len(candidates)} candidate interventions from upstream R&D.")
    print(f"[T+00 Days] Audited {len(slots)} verified manufacturing slots from federated partner network.\n")

    print("[T+05 Days] Executing OR-Tools Mixed-Integer Linear Constraint Solver...")
    result = BioreactorAllocationSolver.solve(candidates, slots)

    if result.is_feasible:
        print("[T+06 Days] STATUS: OPTIMAL ALLOCATION FOUND (No capacity collisions detected).")
        for cand_id, slot_id in result.allocations.items():
            print(f"  -> Candidate '{cand_id}' successfully mapped to Slot '{slot_id}'")
    else:
        print("[T+06 Days] STATUS: CONFLICT DETECTED - Insufficient capacity or platform mismatch.")
        for conflict in result.conflicts:
            print(f"  [!] {conflict}")

    print("\n[T+10 Days] Initializing 6-Stage Action Engine for allocated slots...")
    for cand_id, slot_id in result.allocations.items():
        action = ActionRecord(
            action_id=f"act_alloc_{cand_id}",
            domain="MANUFACTURING",
            title=f"Activate Reservation for {cand_id}",
            description=f"Formally lock Slot {slot_id} with participating CMO.",
            assigned_human_owner="lead_ops_duty_officer@preparedness.org",
            executing_partner_id=slot_id
        )
        fsm = ActionStateMachine(action)
        print(f"  Action [{action.action_id}]: {fsm.current_state}")
        fsm.transition_to(ActionState.APPROVED, actor_id="ops_board", reason="Simulation activation protocol")
        print(f"  Action [{action.action_id}]: -> {fsm.current_state}")
        fsm.transition_to(ActionState.ACCEPTED, actor_id=slot_id, reason="CMO automated API response")
        print(f"  Action [{action.action_id}]: -> {fsm.current_state}")

    print("\nReplay simulation run completed successfully.")
    print("==========================================================")


if __name__ == "__main__":
    main()
