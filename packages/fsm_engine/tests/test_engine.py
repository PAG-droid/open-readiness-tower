import unittest
from datetime import datetime
from open_readiness_schemas.models import ActionRecord, ActionState
from open_readiness_fsm.engine import ActionStateMachine, InvalidStateTransitionError


class TestActionStateMachine(unittest.TestCase):
    def test_valid_lifecycle(self):
        record = ActionRecord(
            action_id="act_001",
            domain="MANUFACTURING",
            title="Reserve Fill-Finish Slot",
            description="Reserve 2000L fill-finish line at Site B",
            assigned_human_owner="owner@ops.org",
            executing_partner_id="cmo_site_b"
        )
        fsm = ActionStateMachine(record)
        self.assertEqual(fsm.current_state, ActionState.PROPOSED)

        fsm.transition_to(ActionState.APPROVED, actor_id="lead@ops.org", reason="Funding secured")
        self.assertEqual(fsm.current_state, ActionState.APPROVED)

        fsm.transition_to(ActionState.ACCEPTED, actor_id="cmo_site_b", reason="Slot reserved in MES")
        self.assertEqual(fsm.current_state, ActionState.ACCEPTED)

        fsm.transition_to(ActionState.EXECUTING, actor_id="cmo_site_b", reason="Batch run initiated")
        self.assertEqual(fsm.current_state, ActionState.EXECUTING)

        fsm.transition_to(ActionState.COMPLETED, actor_id="cmo_site_b", reason="Fill finish complete")
        self.assertEqual(fsm.current_state, ActionState.COMPLETED)

        fsm.transition_to(
            ActionState.VERIFIED,
            actor_id="auditor_agent_09",
            reason="QA batch release signed",
            evidence_hash="sha256_mock_hash_abc123"
        )
        self.assertEqual(fsm.current_state, ActionState.VERIFIED)
        self.assertEqual(len(fsm.audit_log), 5)

    def test_illegal_transition_jump(self):
        record = ActionRecord(
            action_id="act_002",
            domain="CLINICAL",
            title="Deploy Phase 1 Trial",
            description="Protocol activation",
            assigned_human_owner="owner@ops.org",
            executing_partner_id="site_12"
        )
        fsm = ActionStateMachine(record)
        with self.assertRaises(InvalidStateTransitionError):
            fsm.transition_to(ActionState.VERIFIED, actor_id="auditor", reason="skip", evidence_hash="hash")

    def test_verified_requires_evidence(self):
        record = ActionRecord(
            action_id="act_003",
            domain="REGULATORY",
            state=ActionState.COMPLETED,
            title="File Rolling Submission",
            description="FDA pre-IND",
            assigned_human_owner="owner@ops.org",
            executing_partner_id="reg_office"
        )
        fsm = ActionStateMachine(record)
        with self.assertRaises(ValueError):
            fsm.transition_to(ActionState.VERIFIED, actor_id="agent", reason="No hash provided")


if __name__ == "__main__":
    unittest.main()
