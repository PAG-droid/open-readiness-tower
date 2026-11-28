# OpenReadiness: Operational Control Tower for Complex Crises

[![CI](https://github.com/PAG-droid/open-readiness-tower/actions/workflows/ci.yml/badge.svg)](https://github.com/PAG-droid/open-readiness-tower/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)

OpenReadiness is an open-source project for continuously checking and coordinating
operational readiness across partner networks before and during complex crises.
It aims to replace static preparedness scorecards with inspectable evidence,
dependency mapping, capacity conflict detection, and accountable action tracking.

**Status: early prototype.** This repository contains data schemas, a deterministic
capacity allocator, a six-state action engine, and a synthetic replay. Federated
evidence verification, durable event processing, and agent execution are planned.
See [architecture and implementation status](docs/architecture.md) for boundaries.

## Join the project

We welcome Python developers, optimization specialists, and preparedness
practitioners. You can contribute code, tests, documentation, or synthetic
scenarios.

- **New to the project?** [Pick a good first issue](https://github.com/PAG-droid/open-readiness-tower/contribute).
- **Want a larger task?** [Browse help-wanted issues](https://github.com/PAG-droid/open-readiness-tower/issues?q=is%3Aissue%20is%3Aopen%20label%3A%22help%20wanted%22).
- **See it work:** [Follow the short synthetic demo](docs/demo.md).
- **Ask a question or propose a scenario:** [Join Discussions](https://github.com/PAG-droid/open-readiness-tower/discussions).

Every starter issue has acceptance criteria and pointers to the relevant files.
Read [CONTRIBUTING.md](CONTRIBUTING.md), comment on an issue with your approach,
and submit a focused pull request. Domain feedback is welcome without coding.

## Design principles

1. Verify operational evidence and its freshness instead of relying on self-assessment.
2. Use bounded agents to parse unstructured inputs and deterministic algorithms
   for scheduling, capacity calculations, and resource allocation.
3. Keep proprietary source evidence with partner institutions; exchange proof
   metadata through a future federated verification network.
4. Track actions through `PROPOSED -> APPROVED -> ACCEPTED -> EXECUTING -> COMPLETED -> VERIFIED`.

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

## Quickstart

Requires Python 3.12 or newer and Git. CI exercises Python 3.12 and 3.13.

```bash
git clone https://github.com/PAG-droid/open-readiness-tower.git
cd open-readiness-tower
python -m venv .venv
```

Activate the environment in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install all local packages and test dependencies, then run the checks:

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
python -m pytest
python simulation/timeline_emitter/run_replay.py
```

The replay uses synthetic data and should allocate two candidates, advance their
actions through APPROVED and ACCEPTED, and exit successfully. Fixture evidence
strings are placeholders, not verified cryptographic proofs.

Choose a disruption scenario or override the evaluation time:

```bash
python simulation/timeline_emitter/run_replay.py --fixture simulation/fixtures/capacity_shortage.json
python simulation/timeline_emitter/run_replay.py --fixture simulation/fixtures/platform_mismatch.json
python simulation/timeline_emitter/run_replay.py --as-of 2030-01-01T00:00:00Z
```

Expected allocation/unallocated counts are 1/1 for shortage, 0/1 for mismatch,
and 0/2 for the expired-evidence override. Included fixtures use a fixed
`evaluation_time`; `--as-of` overrides it. Without either, the solver uses the
current UTC clock. Naive allocation timestamps are interpreted as UTC. See the
[demo guide](docs/demo.md) for details and implementation limits.

## Containers

With Docker running:

```bash
docker compose run --build --rm constraint-worker
docker compose down
```

The worker runs the same one-shot replay. Redis is reserved for future event-bus
integration and is not currently used by the Python code.

## Repository layout

```text
.github/                      CI, ownership, issue and pull request templates
AGENTS.md                     Shared instructions for coding assistants
CONTRIBUTING.md               Contributor workflow
packages/schemas/             Pydantic data contracts
packages/fsm_engine/          Six-state action engine
services/constraint_solver/  OR-Tools capacity allocator
simulation/fixtures/         Synthetic input data
simulation/timeline_emitter/ Replay runner
docs/                        Architecture, specifications, and decisions
```

## Collaboration

Maintained by [PAG-droid](https://github.com/PAG-droid). Contributions use feature
branches and pull requests to `main`; external contributors can fork the public
repository. See [CONTRIBUTING.md](CONTRIBUTING.md) for checks and working areas,
and [SECURITY.md](SECURITY.md) for private vulnerability reporting.

## License

[Apache License 2.0](LICENSE), as specified in the original project scaffold.
