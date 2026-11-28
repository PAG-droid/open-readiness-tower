import argparse
import sys
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, field_validator

# Resolve source paths independently of the caller's working directory.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "packages/schemas"))
sys.path.insert(0, str(ROOT / "packages/fsm_engine"))

from open_readiness_schemas.models import CandidateIntervention, ManufacturingCapacitySlot, ActionRecord, ActionState
from open_readiness_fsm.engine import ActionStateMachine
from open_readiness_schemas.timestamps import as_utc
from services.constraint_solver.solver import BioreactorAllocationSolver


DEFAULT_FIXTURE = ROOT / "simulation/fixtures/mock_data.json"


class ReplayFixture(BaseModel):
    candidates: list[CandidateIntervention]
    slots: list[ManufacturingCapacitySlot]
    evaluation_time: datetime | None = None

    @field_validator("evaluation_time")
    @classmethod
    def normalize_evaluation_time(cls, value: datetime | None) -> datetime | None:
        return as_utc(value) if value is not None else None


def parse_timestamp(value: str) -> datetime:
    try:
        return as_utc(datetime.fromisoformat(value))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("use an ISO 8601 timestamp, e.g. 2026-11-27T00:00:00Z") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a synthetic allocation and action replay.")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE, help="path to a synthetic JSON fixture")
    parser.add_argument("--as-of", type=parse_timestamp, help="override fixture evaluation_time (ISO 8601; naive means UTC)")
    args = parser.parse_args(argv)
    try:
        data = ReplayFixture.model_validate_json(args.fixture.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        parser.error(f"cannot load fixture '{args.fixture}': {exc}")

    evaluation_time = args.as_of if args.as_of is not None else data.evaluation_time
    print("==========================================================")
    print("  OPEN READINESS CONTROL TOWER - REPLAY SIMULATION ENGINE ")
    print("==========================================================")
    print("SYNTHETIC SIMULATION: evidence strings are placeholders, not verified proofs.")
    print(f"Evaluation time: {evaluation_time.isoformat() if evaluation_time else 'current UTC time'}")
    print(f"[T+00 Days] Ingested {len(data.candidates)} synthetic candidate interventions.")
    print(f"[T+00 Days] Loaded {len(data.slots)} synthetic manufacturing slots.\n")

    print("[T+05 Days] Executing OR-Tools Mixed-Integer Linear Constraint Solver...")
    result = BioreactorAllocationSolver.solve(data.candidates, data.slots, as_of=evaluation_time)
    print(f"Allocation summary: {len(result.allocations)} allocated, {len(result.unallocated_candidates)} unallocated.")

    if result.is_feasible:
        print("[T+06 Days] STATUS: ALL CANDIDATES ALLOCATED within the modeled constraints.")
        for cand_id, slot_id in result.allocations.items():
            print(f"  -> Candidate '{cand_id}' successfully mapped to Slot '{slot_id}'")
    else:
        print("[T+06 Days] STATUS: CONFLICT DETECTED - Some candidates have no eligible allocation.")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
