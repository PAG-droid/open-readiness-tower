# Contributing to OpenReadiness

The project is maintained by [PAG-droid](https://github.com/PAG-droid). Bugs,
design discussions, documentation improvements, and focused pull requests are
welcome. For substantial changes, open an issue first to agree on scope.

## Find your first contribution

Start with the [newcomer issues](https://github.com/PAG-droid/open-readiness-tower/contribute)
or the [help-wanted backlog](https://github.com/PAG-droid/open-readiness-tower/issues?q=is%3Aissue%20is%3Aopen%20label%3A%22help%20wanted%22).
Each issue explains the problem, relevant files, acceptance criteria, and checks.
Comment with your intended approach so contributors can coordinate. If someone
is already working on a task, ask how to collaborate or choose another issue.

Try the [synthetic demo](docs/demo.md) to understand current behavior. Use
[Q&A](https://github.com/PAG-droid/open-readiness-tower/discussions/categories/q-a)
for setup questions and [Ideas](https://github.com/PAG-droid/open-readiness-tower/discussions/categories/ideas)
for design proposals and preparedness scenarios. Non-code contributions are welcome.

## Local setup

Follow the virtual environment and installation instructions in README.md.
The project uses Pydantic v2, OR-Tools, and pytest. All examples and fixtures must
use synthetic data.

## Pull request workflow

1. Fork the repository, or clone it directly if you have write access.
2. Create a branch: `git switch -c feat/short-description` (or `fix/...`).
3. Make a focused change and add regression tests for changed behavior.
4. Run `python -m pytest` and the replay command documented in README.md.
5. Open a pull request against `main`, explaining the problem, change, and checks.
6. Respond to review and keep CI passing. A maintainer merges the pull request.

Keep scheduling and resource allocation deterministic. Each action transition
must retain validation and an audit record. Read AGENTS.md and
docs/architecture.md for the current implementation boundaries.

## Areas for contribution

- Constraint optimization and allocation validation.
- Data schemas and evidence protocols.
- Action lifecycle validation and independent verification.
- Synthetic simulations and disruption scenarios.
- Bounded agent manifests and unstructured-input parsing.

## Community expectations

Be respectful, constructive, and specific. Critique ideas, support claims with
evidence, and respect privacy. The maintainer may moderate abusive interactions.
Contributions are provided under the repository's Apache License 2.0.

Report vulnerabilities using the private process in SECURITY.md.
