from datetime import datetime
from typing import Dict, List, Optional
from open_readiness_schemas.models import ActionRecord, ActionState


class InvalidStateTransitionError(Exception):
    pass


class ActionStateMachine:
    """
    Enforces the deterministic 6-Stage Action Lifecycle:
    PROPOSED -> APPROVED -> ACCEPTED -> EXECUTING -> COMPLETED -> VERIFIED
    """

    VALID_TRANSITIONS: Dict[ActionState, List[ActionState]] = {
        ActionState.PROPOSED: [ActionState.APPROVED],
        ActionState.APPROVED: [ActionState.ACCEPTED],
        ActionState.ACCEPTED: [ActionState.EXECUTING],
        ActionState.EXECUTING: [ActionState.COMPLETED],
        ActionState.COMPLETED: [ActionState.VERIFIED],
        ActionState.VERIFIED: [],  # Terminal state
    }

    def __init__(self, record: ActionRecord):
        self.record = record
        self.audit_log: List[Dict[str, str]] = []

    @property
    def current_state(self) -> ActionState:
        return self.record.state

    def transition_to(
        self,
        new_state: ActionState,
        actor_id: str,
        reason: str,
        evidence_hash: Optional[str] = None
    ) -> ActionRecord:
        allowed = self.VALID_TRANSITIONS.get(self.record.state, [])
        if new_state not in allowed:
            raise InvalidStateTransitionError(
                f"Illegal transition from {self.record.state} to {new_state}. "
                f"Permitted next states: {allowed}"
            )

        # Verification requires independent cryptographic evidence hash
        if new_state == ActionState.VERIFIED:
            if not evidence_hash:
                raise ValueError("Transition to VERIFIED requires a cryptographic evidence hash.")
            self.record.evidence_hashes.append(evidence_hash)

        previous_state = self.record.state
        self.record.state = new_state
        self.record.updated_at = datetime.utcnow()

        self.audit_log.append({
            "timestamp": self.record.updated_at.isoformat(),
            "from_state": previous_state.value,
            "to_state": new_state.value,
            "actor": actor_id,
            "reason": reason,
            "evidence_hash": evidence_hash or ""
        })

        return self.record
