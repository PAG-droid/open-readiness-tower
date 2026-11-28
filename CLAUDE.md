# OpenReadiness: Architecture and code-generation guidance

Read [AGENTS.md](AGENTS.md) for shared repository instructions, development
commands, validation requirements, and contribution conventions. Read
[README.md](README.md) and [docs/architecture.md](docs/architecture.md) before
changing behavior.

The following non-goals, reference baseline, and roadmap govern all code
generation and pull requests. Keep these sections synchronized with README.md.
Map behavior changes to a roadmap phase, preserve the 100-day medical
countermeasure reference baseline, and document implementation limits. Do not
silently expand scope or represent future safeguards as implemented.

## What OpenReadiness Is NOT (Non-Goals)

To preserve architectural clarity, OpenReadiness explicitly avoids the following patterns:

- **NOT an Interactive Chatbot**: Agents are event-driven, schema-bounded background workers that ingest documents, audit evidence, and emit structured JSON records. They are not conversational chat assistants.
- **NOT an LLM Decision-Maker**: Language models are strictly confined to unstructured ingestion and summarization. Solvers (Google OR-Tools) handle mathematical allocations, graph databases enforce dependency constraints, and accountable humans retain sole authority over all operational, policy, and funding decisions.
- **NOT a Centralized Data Lake**: Participating partner organizations (manufacturers, clinical trial networks, regulators) do not pool proprietary operational data into a central repository. The system queries decentralized edge endpoints (Vault Connectors) and stores only SHA-256 cryptographic hashes, verification timestamps, and validity expiration metadata.
- **NOT a Generic Workflow Manager**: The system is purpose-built around a deterministic 6-stage finite state machine (`PROPOSED -> APPROVED -> ACCEPTED -> EXECUTING -> COMPLETED -> VERIFIED`) that requires cryptographic proof verification before any task can be marked `VERIFIED`.

**Implementation status:** These are required architectural boundaries, not claims
that every safeguard is implemented. The current FSM checks for a nonempty
evidence string and records transitions in memory; it does not independently
verify cryptographic proof or authenticate actors. Vault Connectors, a graph
database, and an executable agent runtime are not yet implemented. A SHA-256
hash alone does not establish authenticity or operational readiness. See
[architecture and implementation status](docs/architecture.md).

## Domain Scope & Reference Baseline

While OpenReadiness is architected as a domain-agnostic control tower for complex multi-entity crises, the **primary reference benchmark for synthetic data, unit tests, and simulation scenarios is rapid medical countermeasure response under a 100-day operational timeline**:

- **Upstream Inputs**: Biological threat intelligence, sequence-matched vaccine/therapeutic candidate platforms, target dose requirements, and required bioreactor volumes.
- **Downstream Resources**: Global manufacturing bioreactor slots (mRNA, viral vector, recombinant protein), cold-chain transit envelopes, regulatory submission dossiers, and clinical trial network readiness.
- **Core Constraint Challenge**: Preventing capacity collisions (double-booking of shared facilities) and surfacing expired commitments before crisis activation.

The 100-day timeline defines the reference benchmark for development; the current
synthetic replay does not yet validate an end-to-end 100-day response or all of
these resource domains. Current allocation prevents reuse of a single slot and
excludes expired evidence metadata; cross-slot facility collisions remain future
work.

## 3-Phase Engineering Roadmap

Phase 1 checkmarks indicate implemented prototype components, not completion of
all architectural safeguards or validation of operational readiness.

### Phase 1: Core Deterministic Baseline (Current)

- [x] Pydantic v2 schemas for candidates, manufacturing capacity slots, and agent manifests (`packages/schemas`).
- [x] Deterministic 6-stage finite state machine (FSM) enforcing auditable action lifecycles (`packages/fsm_engine`).
- [x] Google OR-Tools Mixed-Integer Linear Programming (MILP) solver for bioreactor slot allocations (`services/constraint_solver`).
- [x] Runnable chronological outbreak replay harness (`simulation/timeline_emitter`).

### Phase 2: Ingestion Agents & Event-Driven Bus (Next Milestone)

- [ ] Connect Redis/NATS event bus to stream candidate intervention payloads to workers.
- [ ] Implement bounded agent runtime manifests (`services/agent_runtime`) to parse mock regulatory filings and CMO contracts into structured `ActionRecord` payloads.
- [ ] Add cold-chain storage and formulation dependency checks to the constraint solver.
- [ ] Expand synthetic fixtures with multi-pathogen outbreak timelines and disruption injects.

### Phase 3: Zero-Trust Federated Proofs & Control Dashboard

- [ ] Implement Vault Connector edge adapters calculating and verifying SHA-256 evidence hashes.
- [ ] Automated cryptographic decay engine (marking unconfirmed reservations as `EXPIRED`).
- [ ] Web-based operational readiness dashboard (`apps/control-dashboard`) for human decision queues and supply chain graph visualization.

In Phase 3, "decay" means expiration of evidence validity or commitments, not
expiration of a SHA-256 digest. Current evidence-expiry filtering does not
implement the planned automated reservation-state decay engine.
