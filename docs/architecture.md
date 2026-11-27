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
  action records, and agent runtime manifests.
- An OR-Tools mixed-integer solver matches candidates to available slots by
  production platform and volume, assigning at most one candidate per slot.
- A six-state engine enforces sequential transitions and records an in-memory
  audit entry for each transition. The final transition requires a nonempty
  evidence string.
- A command-line replay reads synthetic fixtures, runs allocation, and advances
  allocated actions through APPROVED and ACCEPTED.
- Docker Compose includes Redis as a placeholder; no event-bus integration is
  implemented and the replay exits after one run.

## Design requirements still to implement

The current solver does not validate evidence expiry, manufacturing date windows,
cross-slot facility collisions, routing, or cold-chain constraints. The state
machine does not authenticate actors, independently verify evidence, enforce
allocation checks at approval, or persist its audit log. Placeholder evidence
strings in fixtures are not cryptographic proofs.

Federated vault connectors, commitment decay, bounded agent execution, a durable
event bus, operational dashboards, and authorization are future work. Keep these
requirements separate from claims about current behavior when extending the
project.
