# Repository guidance

## Project and scope

OpenReadiness is an early Python prototype for an operational readiness control
tower. Read README.md and docs/architecture.md before changing behavior. Keep
implemented capabilities distinct from the longer-term project vision.

## Architecture

- `packages/schemas/`: Pydantic v2 data contracts.
- `packages/fsm_engine/`: deterministic six-stage action lifecycle and audit log.
- `services/constraint_solver/`: OR-Tools capacity allocation.
- `simulation/`: synthetic fixtures and replay runner.
- `docs/`: project context, architecture, and decisions.

Use deterministic algorithms for scheduling, capacity, and allocation. LLMs may
parse unstructured inputs but must not make scheduling or allocation calculations.
Preserve the lifecycle PROPOSED -> APPROVED -> ACCEPTED -> EXECUTING -> COMPLETED
-> VERIFIED. Each transition must retain an audit record. Independent evidence
verification and collision checks are design requirements; the current prototype
does not fully enforce them. Never imply that a nonempty hash proves validity.
Keep confidential partner data, credentials, and real operational records out of
the repository. Use synthetic fixtures for examples and tests.

## Development and validation

Use Python 3.12 or newer and a local `.venv`. Install the whole workspace with
`python -m pip install -r requirements-dev.txt`. Run `python -m pytest` and
`python simulation/timeline_emitter/run_replay.py` for changes that affect runtime
behavior. Add focused regression tests for behavior changes. Documentation-only
changes do not need new tests. Do not claim checks ran when they did not.

## Collaboration

Work on a descriptive branch and submit a pull request to `main`. Keep changes
focused; do not reformat unrelated files. Update documentation when setup or
behavior changes. Use readable commit messages. Never commit `.env` files,
virtual environments, bytecode, archives of the source, or machine-specific
settings. Do not change the repository's license without maintainer direction.
