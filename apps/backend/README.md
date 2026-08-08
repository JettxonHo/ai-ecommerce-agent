# AI E-commerce Agent — Backend

This is the backend production package foundation for the AI E-commerce Agent.

**Current scope (FND-001 + FND-002 + FND-003):** a minimal, installable,
buildable, testable Python package with a unified local quality toolchain,
executable architecture enforcement (Import Linter contracts + custom
architecture tests with positive/negative fixtures), and CI plus repository
protection (GitHub Actions required checks, dependency audit, secret
detection, Dependabot, branch protection). These directories
establish *where* production Python code lives, *how* dependencies are
locked, *how* local quality checks run uniformly, and *how* the accepted
architecture is enforced automatically — nothing more. CI reuses exactly the
local commands below (see
[CI and Repository Governance](../../docs/development/ci-and-repository-governance.md)).

## Requirements

- **Python:** `>=3.13,<3.14` (pinned patch in [`.python-version`](.python-version))
- **uv:** project environment, dependency resolution, lockfile, and tool
  execution are all managed by [`uv`](https://docs.astral.sh/uv/).

## Setup

Sync the environment exactly from the lockfile:

```bash
uv sync --locked
```

## Unified local commands

All commands run from `apps/backend/`. Each fails with a non-zero exit
status on error, and each is reusable verbatim (or equivalent) by future CI
(FND-003).

| Capability                | Command |
| ------------------------- | ------- |
| Format                    | `uv run ruff format .` |
| Format check              | `uv run ruff format --check .` |
| Lint                      | `uv run ruff check .` |
| Type check                | `uv run pyright` |
| Unit tests (`test-unit`)  | `uv run pytest -m unit` |
| Contract tests (`test-contract`) | `uv run pytest -m contract` |
| Architecture tests (`test-architecture`) | `uv run pytest -m architecture` |
| Architecture enforcement (`architecture`) | `uv run lint-imports && uv run pytest -m architecture` |
| Fast tests (`test-fast`)  | `uv run pytest -m "not live and not slow"` |
| All local tests (`test-all-local`) | `uv run pytest -m "not live"` |
| Quality gate              | `uv run ruff format --check . && uv run ruff check . && uv run pyright && uv run lint-imports && uv run pytest -m "not live and not slow"` |
| Build                     | `uv build` |
| OpenAPI specification validation | `uv run openapi-spec-validator ../../contracts/openapi/openapi.yaml` |
| Authored OpenAPI catalog validation | `uv run python ../../contracts/openapi/tools/validate.py ../../contracts/openapi/openapi.yaml` |
| Authored OpenAPI breaking diff | `uv run python ../../contracts/openapi/tools/diff.py <accepted-baseline.yaml> ../../contracts/openapi/openapi.yaml` |

The quality gate (`format-check` → `lint` → `typecheck` → `lint-imports` →
`test-fast`) is the single local entry point a developer or coding agent
runs before opening a pull request. It deliberately runs the `test-fast`
selection rather than bare `pytest`: default commands must never execute
`live`-marked tests (real external network or providers).

## Test classification (pytest markers)

Strict markers are enforced (`--strict-markers`); unknown markers fail
collection. Warnings are errors (one precise, documented exception for a
`pytest-socket` warning emitted while its `SocketBlockedError` is raised).

| Marker | Meaning |
| ------ | ------- |
| `unit` | Hermetic, fast unit tests with no external resources |
| `integration` | Real technical adapters with isolated resources; never production services |
| `contract` | Public contract, port, adapter compliance, schema, event and dispatch payload tests |
| `architecture` | Layer direction, module boundary, public facade, module DAG, configuration boundary, spike isolation |
| `e2e` | Complete business or runtime flows across real components |
| `evaluation` | AI output quality evaluation with fixed fixtures or scorers |
| `live` | Real external network or providers; costly or nondeterministic; **opt-in only**, excluded from every default selection |
| `slow` | Exceeds the fast-test budget; still part of the full local suite |

## Architecture enforcement (FND-002)

The accepted architecture (RFC-001-DQ-03/04/05/06/08/09) is enforced by
three complementary checkers — each rule has exactly one authoritative
checker, never duplicated:

- **Import Linter** (`uv run lint-imports`, configured in
  `[tool.importlinter]`): ten import-graph contracts — spike isolation,
  per-module layer direction, top-level package direction (including shared
  kernel independence), domain/application internal and external dependency
  purity, bootstrap direction, orchestration and entrypoint boundaries.
- **Custom graph tests** (`pytest -m architecture`): public-facade-only
  cross-module imports and the module dependency DAG, evaluated on the same
  `grimp` graph engine Import Linter uses.
- **Custom AST tests** (`pytest -m architecture`): environment access in
  core layers, public-contract technical type leakage, and the skill
  boundary.

Every contract has positive fixtures (legal architecture must never be
rejected) and negative fixtures (each violation must be detected with a
locatable report: `Rule` / `Source` / `Illegal Target` /
`Expected Boundary`). See [`tests/architecture/README.md`](tests/architecture/README.md)
for the fixture strategy, how to add contracts, and how to read failures.

## Development dependencies

All development-only; none are runtime dependencies of the package.

| Dependency | Purpose |
| ---------- | ------- |
| `ruff` | Formatter, linter, import sorting (FND-001) |
| `pyright` | Strict type checking (FND-001) |
| `pytest` | Test runner with strict markers and warnings-as-errors (FND-001) |
| `pytest-cov` | Branch-aware coverage measurement, threshold deferred (FND-001) |
| `pytest-socket` | Default network blocking for non-`live` tests (FND-002): minimal, maintained, MIT; provides the socket-level guard and `SocketBlockedError` semantics that a hand-rolled conftest patch would duplicate poorly |
| `import-linter` | Executable import-graph architecture contracts (FND-002): minimal, maintained, BSD-2-Clause; the standard tool for layer/boundary contracts — a hand-written equivalent would be the prohibited "large custom architecture framework" |
| `pip-audit` | Known-vulnerability audit of the locked environment (FND-003): maintained, Apache-2.0; the standard OSV-backed auditor — runs in CI as the `security / dependency-audit` required check and locally via `uv run pip-audit --progress-spinner off --skip-editable` |
| `openapi-spec-validator` | Dev-only official Python OpenAPI validator for authored OAS 3.1; validates the contract but never generates or rewrites it (MVP0-001) |

## Coverage

Branch-aware coverage measurement is available but its merge threshold is
deliberately **deferred**. Per RFC-001-DQ-09, the global 80% `fail-under`
merge gate activates only after real executable production logic lands; it
is not faked here by import-only tests or broad exclusions.

```text
Coverage Measurement = AVAILABLE
Coverage Merge Threshold = DEFERRED
```

Run measurement explicitly:

```bash
uv run pytest --cov=src/ai_ecommerce_agent --cov-branch --cov-report=term-missing
```

## Current implementation scope

Implemented now:

- Independent, valid Python project under `apps/backend/`
- `src/ai_ecommerce_agent/` package layout with `py.typed`
- Dependency locking via `uv.lock`
- Ruff (formatter + linter + import sorting), Pyright (strict), pytest
  (strict markers, warnings-as-errors)
- Branch-aware coverage measurement (threshold deferred)
- Unified local quality commands (above)
- Architecture enforcement: ten Import Linter contracts, public-facade and
  module-DAG graph tests, environment/leakage/skill semantic tests,
  positive/negative fixtures, default network blocking for non-`live` tests

Not implemented yet (and **not** claimed to exist):

- API / HTTP server
- Database / ORM / migrations
- Worker / queue / durable dispatch
- LangGraph runtime / graphs / checkpointer
- Model / retrieval / observability runtimes
- Business modules, business workflows, or production bootstrap

The authored MVP-0 OpenAPI contract foundation lives in
[`../../contracts/openapi/`](../../contracts/openapi/). It is a contract source
only; no HTTP handler or API runtime is claimed by this repository yet.

Architecture tests reference future package shapes (`modules.<module>.*`,
`orchestration/`, `entrypoints/`, `shared_kernel/`, `bootstrap/`) through
test-only fixtures; those packages do not exist in the production tree.

## CI and repository protection (FND-003)

The repository's required CI checks run exactly the commands in the table
above — no CI-only quality rules exist. The eight stable required checks
(`quality / format`, `quality / lint`, `quality / typecheck`,
`quality / architecture`, `test / unit-contract`, `test / package-build`,
`security / dependency-audit`, `security / secret-detection`) plus
Dependabot, secret detection and `main` branch protection are documented in
[docs/development/ci-and-repository-governance.md](../../docs/development/ci-and-repository-governance.md),
including how to reproduce every required check locally.

## Spike source boundary

Spike code under `spikes/` is throwaway exploration. It **must not** be
copied, moved, or imported into this production package — this is now
machine-enforced by the `Production and Spike isolation` Import Linter
contract. Production code is written here fresh against the accepted
architecture.
