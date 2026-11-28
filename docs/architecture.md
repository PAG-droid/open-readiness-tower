# Architecture and implementation status

## Vision

OpenReadiness aims to replace static preparedness assessments with an event-driven
network that continuously checks operational evidence, maps dependencies, detects
capacity conflicts, and tracks accountable corrective actions across partners.

The intended architecture separates unstructured-input parsing by bounded agents
from deterministic scheduling and capacity allocation. Partner-owned evidence
should remain decentralized, with hashes, freshness metadata, and verification
results exchanged instead of proprietary source documents.

## Current prototype

- Pydantic contracts describe candidate interventions, manufacturing slots,
  action records, and agent runtime manifests. Dose counts and volumes must be
  positive (volumes must also be finite), and manufacturing windows must end
  after they start. Negative storage temperatures remain valid.
- An OR-Tools mixed-integer solver matches candidates to available slots by
  production platform and volume, assigning at most one candidate per slot.
  Slots are eligible only when their evidence expiry is strictly later than the
  evaluation time. This validates freshness metadata, not the evidence itself.
- A six-state engine enforces sequential transitions and records an in-memory
  audit entry for each transition. The final transition requires a nonempty
  evidence string.
- A command-line replay selects synthetic fixtures, runs allocation, and advances
  allocated actions through APPROVED and ACCEPTED. Included scenarios cover
  successful allocation, capacity shortage, and incompatible platforms.
- Docker Compose includes Redis as a placeholder; no event-bus integration is
  implemented and the replay exits after one run.

## Design requirements still to implement

The current solver does not schedule within manufacturing date windows or check
cross-slot facility collisions, routing, or cold-chain constraints. The state
machine does not authenticate actors, independently verify evidence, enforce
allocation checks at approval, or persist its audit log. Placeholder evidence
strings in fixtures are not cryptographic proofs.

Federated vault connectors, commitment decay, bounded agent execution, a durable
event bus, operational dashboards, and authorization are future work. Keep these
requirements separate from claims about current behavior when extending the
project.

## Allocation timestamps and reproducible replays

Manufacturing `window_start`, `window_end`, and `evidence_expires_at` are normalized
to UTC during validation. For compatibility with existing fixtures, a timestamp
without an offset is interpreted as UTC; explicit offsets are converted to UTC.
Mixed naive and aware inputs therefore compare on the same timeline. A window
whose normalized end is not later than its start raises a validation error.
This policy covers allocation timestamps; action audit timestamp modernization
is separate work.

`BioreactorAllocationSolver.solve(..., as_of=timestamp)` accepts an explicit
evaluation time using the same UTC policy. Omitting it uses the current UTC clock.
Evidence expiring exactly at that time is expired. A future expiry never overrides
an unavailable status, incompatible platform, or insufficient capacity.

The replay accepts `--fixture PATH` and `--as-of ISO_TIMESTAMP`. Evaluation time
comes from the CLI override, then the fixture's optional `evaluation_time`, then
the current UTC clock. Included fixtures specify a fixed historical evaluation
time so their results remain reproducible as wall-clock time advances. These
results describe the synthetic scenario at that time, not current readiness.

Invalid files, JSON structure, model fields, and timestamps produce a nonzero
exit with a diagnostic. A valid scenario with unallocated candidates exits zero
and reports a conflict; it is an expected simulation outcome.
