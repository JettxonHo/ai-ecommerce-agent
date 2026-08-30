# Real Product-to-Brief Pilot P1 harness repair review

> **Issue:** [#345](https://github.com/JettxonHo/ai-ecommerce-agent/issues/345)<br>
> **Base:** `origin/main@ed17618e67c9bfb6693a77d96ef4518250cf93eb`<br>
> **Branch:** `codex/mbl-pilot-p1r-harness-response-key`<br>
> **Branch status:** `P1R_HARNESS_REPAIR_IN_PROGRESS`<br>
> **Merge-effective status:** `HARNESS_BLOCKER = REPAIRED` only after this PR reaches `main`.

## Outcome and boundary

Issue #343 / PR #344 is merge-effective P1 provider-free characterization
`CONFIRMED` for the retained live-smoke response-key blocker. Its historical
first-failure attribution remains `INCONCLUSIVE`. Issue #345 performs the one
separately bounded repair: the retained smoke now consumes the public
`exportSnapshotId` field and a provider-free regression proves that the smoke
continues into the content-download seam when `snapshotId` is absent.

This is a harness-consumer repair, not a production export fix or a Pilot run.
`P0_CONTRACT_FROZEN`, the exact P0 denominator and all P0/Pilot boundaries stay
unchanged. `PILOT_EXECUTION_AUTHORIZATION = NOT_AUTHORIZED` remains true.

## Authorization and exact scope

The Issue #345 allowlist is exactly these eight paths:

1. `apps/backend/tests/integration/test_fl2_deepseek_live_smoke.py`
2. `apps/backend/tests/unit/test_fl2_live_controls.py`
3. `AGENTS.md`
4. `README.md`
5. `docs/goals/real-product-to-brief-pilot-goal.md`
6. `docs/handoffs/implementation-readiness.md`
7. `docs/reviews/real-product-to-brief-pilot-p1-harness-repair.md`
8. `docs/sessions/session-014-real-product-to-brief-pilot-p1-harness-repair.md`

The Issue #343 P1 characterization report, the Pilot Contract, P0 plan and
Session-012, DEC-086/087, production export projection, OpenAPI/generated
client, migrations/schema, dependencies/locks and historical L5 evidence are
unchanged. No ninth path is in scope.

## PRE-EDIT checkpoint

The implementer used a fresh clean clone at
`/private/tmp/ai-ecommerce-agent-345b-e8LsBD/repo` on branch
`codex/mbl-pilot-p1r-harness-response-key`, with `HEAD` and `origin/main` both
`ed17618e67c9bfb6693a77d96ef4518250cf93eb`. The exact custom worker
configuration was parsed with Python 3.12 and recorded as
`CONFIG_VERIFIED` (`luna-worker` / `gpt-5.6-luna` / `max`); runtime model
identity was not inferred.

The public FastAPI snapshot projection and generated client expose
`exportSnapshotId` and the content route is keyed by `{exportSnapshotId}`.
Before this repair, the retained smoke selected `snapshot.json()["snapshotId"]`.
No Provider, Secret, `.env`, runtime, Docker, PostgreSQL, browser, Pilot or
private-material action occurred during the checkpoint.

## Tests-first RED

Only the new unit regression was added before changing the smoke. Its
interface-shaped fake returns a successful `201` snapshot body containing
`exportSnapshotId` and `contentLocation`, with no `snapshotId`; its client logs
download requests. The test executes the retained smoke through `runpy` and
asserts the intended download paths after the smoke returns.

The repository-approved offline command was:

```text
uv run --offline --project apps/backend python -m pytest apps/backend/tests/unit/test_fl2_live_controls.py::test_live_smoke_uses_public_export_snapshot_id_before_download -q
```

On the unchanged smoke the test collected and executed, then failed exactly at
the historical lookup with:

```text
KeyError: 'snapshotId'
```

The fake observed no download request. This was a behavioral RED; it was not an
import, collection, dependency, environment or runtime failure. The smoke file
was byte/diff-identical during RED.

## Minimal GREEN

After RED acceptance, the smoke changed only:

```python
snapshot_ids.add(snapshot.json()["exportSnapshotId"])
```

No fallback, dual-field lookup, refactor or production change was introduced.
The existing late-failure unit fake was updated to use the same public response
field so its cleanup assertion exercises the repaired seam.

The focused regression passed:

```text
1 passed
```

The affected provider-free controls, P1 characterization and export HTTP /
renderer checks passed:

```text
89 passed in 5.64s
```

The fake is engineering evidence only. It is not Pilot business evidence and
does not alter the fixed denominator, participant state, F1–F9, P2 gate or
Provider authorization.

## Validation record

The implementer ran the proportional provider-free and static checks before
handoff:

```text
Focused response-key regression: 1 passed in 0.70s
Affected controls, P1 characterization and export HTTP/renderer contracts: 89 passed in 5.64s
Architecture boundary/import tests: 28 passed in 2.05s
Import Linter: 10 contracts kept, 0 broken
Backend Pyright (repository command `uv run --offline pyright` from `apps/backend`): 0 errors, 0 warnings, 0 informations
Ruff format (`uv run --offline ruff format --check .` from `apps/backend`): 501 files already formatted
Ruff lint (`uv run --offline ruff check .` from `apps/backend`): All checks passed
`git diff --check` (including the two new files): PASS
Exact allowlist: 8 changed paths; protected/forbidden diff audit: PASS
Documentation local links/fences and stale-wording audit: PASS
```

The checks did not start the opt-in live smoke or a PostgreSQL integration
path; no runtime, Provider or Secret evidence is claimed.

## Security and failure boundaries

- No credential environment variable, `.env` file, Secret value or provider
  payload was read, injected, printed or persisted.
- No external Provider, paid request, platform request, browser, product
  runtime, Docker or PostgreSQL lifecycle was started.
- The public response contract remains the source of truth; the harness has no
  compatibility fallback to the removed `snapshotId` field.
- If the PR is not merged, close it without merging. After merge, rollback is
  an ordinary revert of the repair PR merge commit; no runtime or data rollback
  is involved.

## Merge gate and handoff

`HARNESS_BLOCKER = REPAIRED` is branch-pending until this PR reaches `main`.
Independent Sol five-axis review and fresh GitHub Required Checks remain
required. The implementer does not approve or merge its own PR. After merge,
verify the exact main commit and that P0/P1 protected truth is unchanged;
`PILOT_EXECUTION_AUTHORIZATION` remains `NOT_AUTHORIZED`, and no P2 action is
created or started.

## Relationships

- [Issue #345](https://github.com/JettxonHo/ai-ecommerce-agent/issues/345)
- [Issue #343 P1 characterization review](real-product-to-brief-pilot-p1-characterization.md)
- [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md)
- [Implementation Readiness](../handoffs/implementation-readiness.md)
- [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)
- [Session-014](../sessions/session-014-real-product-to-brief-pilot-p1-harness-repair.md)
