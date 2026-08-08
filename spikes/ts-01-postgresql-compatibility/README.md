# TS-01 PostgreSQL compatibility slice

This directory is a disposable, test-only compatibility slice for
MVP0-004 / Issue #63. It proves a small set of persistence invariants on the
MVP0-003 PostgreSQL service using synchronous SQLAlchemy 2.x, Psycopg 3 and
Alembic. It is evidence for the accepted TS-01 minimum slice; it is **not** a
production schema, repository, worker, queue or business implementation.

## Scope

The harness covers only these representative paths:

- fresh Alembic migration and a clean downgrade/forward-upgrade;
- a short `FOR UPDATE SKIP LOCKED` claim transaction on two independent
  connections (the second worker cannot double-claim a locked work item);
- lease expiry takeover with a strictly higher monotonic fencing token;
- stale holder/token commit rejection and current holder commit success;
- an injected failure after a Current Truth write, proving transaction
  rollback followed by an explicit forward repair with no partial Current
  Truth.

The schema lives under the dedicated `ts01_compat` namespace in the Business
database. Teardown drops only that schema. No production tables, migration
lineage, public API or worker code is imported or modified.

## Prerequisites

1. Python 3.13 and `uv`.
2. The MVP0-003 local PostgreSQL service is healthy:

   ```bash
   cd ../..
   ./scripts/mvp0/up
   ./scripts/mvp0/verify
   ```

The default URL targets the local demo Business database. Override it with
`TS01_DATABASE_URL` when using another PostgreSQL database. The URL must use
the synchronous Psycopg dialect (`postgresql+psycopg://...`); SQLite is
rejected by the tests.

## Reproduce

Run all commands from this directory:

```bash
uv sync --locked
uv run alembic upgrade head
uv run pytest -m integration
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv build
git diff --check
```

The test fixture performs a fresh migration for each test and removes only
`ts01_compat` during teardown. The explicit `alembic upgrade head` command is
useful as a smoke check; it can be followed by `alembic downgrade base` when
manually inspecting the test-only schema. No reset/delete operation is
performed against the PostgreSQL volume.

## Compatibility evidence

The lockfile is the executable compatibility tuple for this slice:

```text
Python 3.13.14
SQLAlchemy 2.0.43 (synchronous Core API)
Psycopg 3.2.9 (synchronous driver)
Alembic 1.16.4
PostgreSQL 16.14-bookworm (MVP0-003 image)
```

The implementation follows the relevant primary documentation:

- [SQLAlchemy PostgreSQL dialect — Psycopg](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#psycopg)
- [Psycopg 3 basic usage](https://www.psycopg.org/psycopg3/docs/basic/usage.html)
- [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [PostgreSQL `SELECT ... FOR UPDATE SKIP LOCKED`](https://www.postgresql.org/docs/16/sql-select.html#SQL-FOR-UPDATE-SHARE)

## Evidence record (run locally)

This section is intentionally filled only after a real run against the
MVP0-003 service. Record the exact commands, commit, Python/uv versions,
database target and test result here or in the PR description. A passing run
is bounded evidence, not a claim that the full 29-scenario concurrency matrix
or a production Worker has been implemented.

```text
Task / Issue: MVP0-004 / #63
Role / model: IMPLEMENTER / luna-worker (CONFIG_VERIFIED; runtime model not exposed)
Worktree / branch: codex/mvp0-004-postgres-compatibility
Base: 75e3325b67974594b3d1393302f91d1c417c90a6 (MVP0-003 merged)
Run date: 2026-08-08 (Asia/Shanghai)
Toolchain: Python 3.13.14; uv 0.12.0
Database: PostgreSQL 16.14-bookworm, MVP0-003 Business database `ecommerce_business`, schema `ts01_compat`
Commands:
  `./scripts/mvp0/verify` — PASS (service healthy, Business/Checkpoint DB and role isolation)
  `uv sync --locked` — PASS
  `uv run alembic upgrade head` — PASS
  `uv run pytest -m integration -q` — PASS (5 passed)
  `uv run ruff format --check .` — PASS
  `uv run ruff check .` — PASS
  `uv run pyright` — PASS (0 errors, 0 warnings, 0 informations)
  `uv build` — PASS (sdist and wheel)
  `git diff --check` — PASS
Result: bounded TS-01 representative invariants PASS on real PostgreSQL; no SQLite path used.
Limitations: test-only bounded evidence; no production Business schema, Worker, queue, retry framework or full 29-scenario matrix.
```
