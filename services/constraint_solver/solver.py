from typing import List, Dict, Tuple
from ortools.linear_solver import pywraplp
from open_readiness_schemas.models import CandidateIntervention, ManufacturingCapacitySlot, SlotStatus


class AllocationResult:
    def __init__(self, is_feasible: bool, allocations: Dict[str, str], unallocated_candidates: List[str], conflicts: List[str]):
        self.is_feasible = is_feasible
        self.allocations = allocations  # candidate_id -> slot_id
        self.unallocated_candidates = unallocated_candidates
        self.conflicts = conflicts


class BioreactorAllocationSolver:
    """
    Deterministic Mixed-Integer Linear Programming (MILP) solver using Google OR-Tools.
    Matches CandidateInterventions to qualified ManufacturingCapacitySlots without resource collisions.
    """

    @staticmethod
    def solve(
        candidates: List[CandidateIntervention],
        slots: List[ManufacturingCapacitySlot]
    ) -> AllocationResult:
        solver = pywraplp.Solver.CreateSolver("SCIP")
        if not solver:
            raise RuntimeError("OR-Tools SCIP solver unavailable.")

        # x[c_id, s_id] = 1 if candidate c is assigned to slot s, else 0
        x: Dict[Tuple[str, str], pywraplp.Variable] = {}
        candidate_map = {c.candidate_id: c for c in candidates}
        slot_map = {s.slot_id: s for s in slots}

        # Filter available slots with non-expired evidence
        active_slots = [s for s in slots if s.status == SlotStatus.AVAILABLE]

        for c in candidates:
            for s in active_slots:
                # Platform compatibility and capacity constraints
                if c.platform in s.supported_platforms and s.bioreactor_capacity_liters >= c.bioreactor_volume_liters_required:
                    x[c.candidate_id, s.slot_id] = solver.BoolVar(f"x_{c.candidate_id}_{s.slot_id}")

        # Constraint 1: Each candidate is assigned to AT MOST one slot
        for c_id in candidate_map:
            assigned_slots = [x[c_id, s.slot_id] for s in active_slots if (c_id, s.slot_id) in x]
            if assigned_slots:
                solver.Add(solver.Sum(assigned_slots) <= 1)

        # Constraint 2: Each slot is assigned to AT MOST one candidate (No double-booking)
        for s in active_slots:
            assigned_candidates = [x[c.candidate_id, s.slot_id] for c in candidates if (c.candidate_id, s.slot_id) in x]
            if assigned_candidates:
                solver.Add(solver.Sum(assigned_candidates) <= 1)

        # Objective: Maximize total number of allocated candidates
        all_vars = list(x.values())
        if all_vars:
            solver.Maximize(solver.Sum(all_vars))
            status = solver.Solve()
        else:
            status = pywraplp.Solver.OPTIMAL

        allocations: Dict[str, str] = {}
        conflicts: List[str] = []

        if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
            for (c_id, s_id), var in x.items():
                if var.solution_value() > 0.5:
                    allocations[c_id] = s_id

        unallocated = [c_id for c_id in candidate_map if c_id not in allocations]

        if unallocated:
            for u in unallocated:
                cand = candidate_map[u]
                conflicts.append(
                    f"Candidate '{u}' ({cand.platform.value}, {cand.bioreactor_volume_liters_required}L) "
                    "could not be allocated due to capacity shortage or platform incompatibility."
                )

        is_feasible = (len(unallocated) == 0)
        return AllocationResult(
            is_feasible=is_feasible,
            allocations=allocations,
            unallocated_candidates=unallocated,
            conflicts=conflicts
        )
