# AI E-commerce Agent — Backend

This is the backend production package foundation for the AI E-commerce Agent.

**Current scope (FND-001):** a minimal, installable, buildable, testable Python
package with a unified local quality toolchain. This directory establishes
*where* production Python code lives, *how* dependencies are locked, and *how*
local quality checks run uniformly — nothing more.

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

All commands run from `apps/backend/`. Each fails with a non-zero exit status on
error, and each is reusable verbatim (or equivalent) by future CI.

| Capability    | Command                              |
| ------------- | ------------------------------------ |
| Format        | `uv run ruff format .`               |
| Format check  | `uv run ruff format --check .`       |
| Lint          | `uv run ruff check .`                |
| Type check    | `uv run pyright`                     |
| Unit tests    | `uv run pytest -m unit`              |
| All tests     | `uv run pytest`                      |
| Quality gate  | `uv run ruff format --check . && uv run ruff check . && uv run pyright && uv run pytest` |
| Build         | `uv build`                           |

The quality gate (`format-check` → `lint` → `typecheck` → `test`) is the single
local entry point a developer or coding agent runs before opening a pull
request.

## Coverage

Branch-aware coverage measurement is available but its merge threshold is
deliberately **deferred**. Per RFC-001-DQ-09, the global 80% `fail-under` merge
gate activates only after real executable production logic lands; it is not
faked here by import-only tests or broad exclusions.

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

Not implemented yet (and **not** claimed to exist):

- API / HTTP server
- Database / ORM / migrations
- Worker / queue / durable dispatch
- LangGraph runtime / graphs / checkpointer
- Model / retrieval / observability runtimes
- Business modules or business workflows
- Production bootstrap

## Spike source boundary

Spike code under `spikes/` is throwaway exploration. It **must not** be copied,
moved, or imported into this production package. Production code is written here
fresh against the accepted architecture.
