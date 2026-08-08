# TS-03 Evidence Record (MVP0-005 / Issue #67)

**Status:** bounded, non-production slice; no stop condition triggered.

**Execution context:** branch `codex/mvp0-005-langgraph-checkpoint-compatibility`,
base `54f9842dbafac1db51169d98d7d2fc8f5d73478e`, scoped worktree
`/private/tmp/ai-ecommerce-mvp0-005`. Only
`spikes/ts-03-langgraph-checkpoint-compatibility/**` is changed.

## Locked tuple and official evidence

The independent `pyproject.toml` / `uv.lock` resolve on Python 3.13.14 to
LangGraph 1.2.9, `langgraph-checkpoint-postgres` 3.1.0,
`langgraph-checkpoint` 4.2.0, `langchain-core` 1.5.3, Psycopg 3.2.10 with
`psycopg-binary` 3.2.10, and `psycopg-pool` 3.2.6. The shared local service is
`postgres:16.14-bookworm` (PostgreSQL 16.14). The exact tuple and the
`exact_compatible` / no-downgrade boundary are recorded in
[`compatibility-matrix.yaml`](compatibility-matrix.yaml).
The explicit setup reads `checkpoint_migrations.max(v) = 9` and fixes the
readable store identity to `checkpoint_migrations_v9`; setup fails closed if a
different vendor migration version is present.

Official sources consulted on 2026-08-08:

- <https://docs.langchain.com/oss/python/langgraph/persistence> — checkpoint
  snapshots, thread persistence, and interrupt/resume use;
- <https://reference.langchain.com/python/langgraph.checkpoint.postgres/PostgresSaver>
  — synchronous `PostgresSaver` and connection-string constructor;
- <https://reference.langchain.com/python/langgraph.checkpoint.postgres/PostgresSaver/setup>
  — `setup()` creates/migrates vendor tables and must be called directly;
- <https://reference.langchain.com/python/langgraph/types/Durability> —
  `sync` means persistence completes before the next step;
- <https://reference.langchain.com/python/langgraph/graph/state/StateGraph> —
  StateGraph must be compiled before invocation;
- <https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint-postgres/langgraph/checkpoint/postgres/__init__.py>
  — source-level sync constructor/setup implementation.

## Reproduction and results

The existing local service was verified without volume reset:

```text
scripts/mvp0/verify
MVP-0 PostgreSQL status: running (health: healthy)
Databases: ecommerce_business (Business), ecommerce_checkpoint (Checkpoint)
Business role blocked from Checkpoint DB: PASS
Checkpoint role blocked from Business DB: PASS
```

The Checkpoint connection also reported `server_version = 16.14`
(`16.14 (Debian 16.14-1.pgdg12+1)`).

Setup is explicit and was run once before the integration suite:

```text
cd spikes/ts-03-langgraph-checkpoint-compatibility
uv sync --locked
uv run python scripts/setup_checkpoint.py
Checkpoint setup complete: database=ecommerce_checkpoint role=mvp0_checkpoint migration_version=9
```

The graph builder does not invoke `setup()`; an integration test monkeypatches
`PostgresSaver.setup` to fail and compiles the graph successfully. The normal
graph fixture therefore cannot silently migrate the store.

Resume reconciliation reads the latest `PostgresSaver.get_tuple()` directly
from PostgreSQL and derives the checkpoint task/thread, state channels, and
config before classification. Integration tests do not pass a hand-built
checkpoint metadata object as resume authorization.

Executed checks:

| Command | Result |
|---|---|
| `uv run pytest` | 12 passed, 7 skipped (integration opt-in absent) |
| `TS03_RUN_INTEGRATION=1 uv run pytest -m integration` | 7 passed |
| `TS03_RUN_INTEGRATION=1 uv run pytest` | 19 passed |
| `uv run ruff format --check .` | pass |
| `uv run ruff check .` | pass |
| `uv run pyright` | 0 errors, 0 warnings |

The integration suite proves the following with real PostgreSQL:

1. Checkpoint and Business databases expose distinct `current_database()` and
   `current_user`; vendor checkpoint tables exist only in the Checkpoint DB.
2. A compact StateGraph uses the official sync `PostgresSaver`, reaches a real
   `interrupt`, and resumes with `Command(resume=...)` and `durability="sync"`.
3. `task_id` and `thread_id` remain stable while the harness creates a new
   `run_id` and increments `attempt` for resume.
4. Resume uses the latest actual Postgres tuple/state/config, not caller-provided
   checkpoint identity; two unique task/thread identifiers retain separate histories;
   a foreign checkpoint is refused before graph invocation.
5. Stale input and review revisions, plus an incompatible workflow/state /
   serializer/checkpointer/store tuple, are refused before graph invocation.
6. The deterministic seven-action classifier has one representative unit path
   per accepted action (`resume_same_thread`, `reconcile_committed_result`,
   `retry_current_stage`, `rerun_from_earliest_invalid_stage`,
   `restart_from_safe_boundary`, `manual_recovery_required`,
   `reject_request`).
7. An unknown outcome without a non-null matching idempotency key is classified
   as `manual_recovery_required`, never as a committed result.
8. The test-only Business probe remains unchanged for every refused request;
   only the compatible resume test commits its explicit probe value after the
   reconciliation gate.

After the suite, the slice cleaned only its generated thread identifiers:

```text
checkpoint rows total/ts03= (0, 0)
```

## Boundaries and limitations

This evidence does not implement a production Recovery framework, Worker
dispatch/lease/fencing, Business transaction/repository, migration rollback,
retention, or live Provider. It does not use SQLite. No safe downgrade path or
forward converter is claimed; if the locked tuple becomes incompatible, the
accepted action is to stop and roll forward / enter manual recovery rather than
altering historical checkpoints or weakening this evidence.
