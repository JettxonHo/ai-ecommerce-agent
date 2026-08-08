# TS-03 — LangGraph `PostgresSaver` compatibility slice

This is the disposable MVP0-005 evidence workspace for Issue #67. It is not
production Runtime, Worker, Recovery Store, Business Repository, or a business
Graph. The only durable data it creates is vendor checkpoint data in the
dedicated local Checkpoint database, under test-only thread identifiers.

## Bounded evidence

- explicit operator/test setup calls `PostgresSaver.setup()`; graph construction
  and ordinary runtime fixtures never migrate the store;
- official synchronous `PostgresSaver` on the independent Checkpoint database;
- compact deterministic `StateGraph` with `durability="sync"` and a real
  `interrupt` / `Command(resume=...)` round trip;
- stable `task_id` / `thread_id` with a new harness `run_id` / attempt on
  resume;
- cross-task, stale-input/review/stage, and incompatible compatibility tuple
  refusal before graph invocation, with an in-memory Business Current Truth
  probe proving no pollution;
- one representative deterministic test for each accepted DEC-051 recovery
  action.

The Business probe is intentionally in-memory and test-only. Checkpoint state
is runtime evidence and never authorizes or writes Business Current Truth.

## Locked compatibility tuple

The independent `pyproject.toml` and `uv.lock` are the authoritative slice
manifest. Resolution was performed with Python 3.13.14 on 2026-08-08:

| Component | Locked version / boundary |
|---|---|
| Python | 3.13.14 (`>=3.13,<3.14`) |
| LangGraph | 1.2.9 |
| `langgraph-checkpoint-postgres` | 3.1.0 |
| `langgraph-checkpoint` | 4.2.0 (resolved transitively) |
| `langchain-core` | 1.5.3 (resolved transitively) |
| Psycopg | 3.2.10 + `psycopg-binary` 3.2.10 |
| `psycopg-pool` | 3.2.6 |
| PostgreSQL | 16.14 (`postgres:16.14-bookworm`, provided by the shared local service) |

The matrix is recorded in [`compatibility-matrix.yaml`](compatibility-matrix.yaml).
The executed command/output record is [`evidence.md`](evidence.md).
The references below are official LangChain/LangGraph API or source documents
used to confirm the synchronous API, `setup()` boundary, and package behavior:

- <https://docs.langchain.com/oss/python/langgraph/persistence>
- <https://reference.langchain.com/python/langgraph.checkpoint.postgres/PostgresSaver>
- <https://reference.langchain.com/python/langgraph.checkpoint.postgres/PostgresSaver/setup>
- <https://reference.langchain.com/python/langgraph/types/Durability>
- <https://reference.langchain.com/python/langgraph/graph/state/StateGraph>
- <https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint-postgres/langgraph/checkpoint/postgres/__init__.py>

## Reproduction

From the repository root, first start/verify the existing local PostgreSQL
service (these commands preserve the demo volume and do not reset it):

```bash
scripts/mvp0/up
scripts/mvp0/verify
```

Then run this slice in its own environment:

```bash
cd spikes/ts-03-langgraph-checkpoint-compatibility
uv sync --locked
uv run python scripts/setup_checkpoint.py
uv run pytest -m unit
TS03_RUN_INTEGRATION=1 uv run pytest -m integration
uv run ruff format --check .
uv run ruff check .
uv run pyright
```

`TS03_RUN_INTEGRATION=1` is an explicit opt-in because integration tests need
the local Checkpoint DB. An optional
`TS03_CHECKPOINT_DATABASE_URL` may point at an operator-managed equivalent;
otherwise defaults mirror `compose.yaml`. The setup command is required and is
never called from graph construction or a worker/runtime fixture.

Cleanup is limited to this slice's `ts03-*` thread identifiers. Do not use the
repository `reset-demo` command for this evidence; it is a destructive demo
volume operation and is outside the slice.

## Stop / limitation boundary

This evidence does not claim production migration, retention, Worker leases,
business transactions, or any SQLite compatibility. If the locked tuple fails
against PostgreSQL 16.14, or if reconciliation cannot refuse stale/foreign /
incompatible state before graph invocation, stop the dependent production
Issue and retain the failure evidence rather than downgrading or changing the
accepted boundary.
