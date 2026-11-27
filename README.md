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
