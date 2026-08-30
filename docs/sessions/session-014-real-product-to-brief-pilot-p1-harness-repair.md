# Session-014: Real Product-to-Brief Pilot P1 harness repair

## Metadata

- **Status:** `P1R_HARNESS_REPAIR_IN_PROGRESS` on this branch; `HARNESS_BLOCKER = REPAIRED` is merge-effective only after the PR reaches `main`.
- **Date:** 2026-08-30
- **Issue:** [#345](https://github.com/JettxonHo/ai-ecommerce-agent/issues/345)
- **Base:** `origin/main@ed17618e67c9bfb6693a77d96ef4518250cf93eb`
- **Branch:** `codex/mbl-pilot-p1r-harness-response-key`
- **Implementer configuration:** `CONFIG_VERIFIED` — `/Users/ketchup/.codex/agents/luna-worker.toml` parsed with Python 3.12 as `luna-worker` / `gpt-5.6-luna` / `max`; runtime identity was not inferred.
- **Authority:** [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md) · [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md) · [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md) · [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md) · [P0 plan](../product/real-product-to-brief-pilot-p0-plan.md) · [Session-013](session-013-real-product-to-brief-pilot-p1.md)

## Context and authorization

### Facts

- Issue #341 / PR #342 is merge-effective: P01–P08 are `ADMITTED`, the denominator is exactly eight frozen product/attempt units, P0 is `P0_CONTRACT_FROZEN`, and the Pilot remains `ACTIVE`.
- Issue #343 / PR #344 is merge-effective P1 provider-free characterization `CONFIRMED` for the retained response-key blocker; historical first-failure attribution remains `INCONCLUSIVE`.
- The public snapshot projection and generated client expose `exportSnapshotId`, while the retained live smoke previously selected `snapshotId` before the download seam.
- `PILOT_EXECUTION_AUTHORIZATION = NOT_AUTHORIZED`. This Session records no P0 observation, Pilot execution, numerator, participant, real input, Provider, Secret, browser, runtime, PostgreSQL or export artifact.

### Exact Issue #345 boundary

Issue #345 authorizes one provider-free harness repair and regression plus
merge-conditional truth updates in the exact eight-path allowlist:

1. `apps/backend/tests/integration/test_fl2_deepseek_live_smoke.py`
2. `apps/backend/tests/unit/test_fl2_live_controls.py`
3. `AGENTS.md`
4. `README.md`
5. `docs/goals/real-product-to-brief-pilot-goal.md`
6. `docs/handoffs/implementation-readiness.md`
7. `docs/reviews/real-product-to-brief-pilot-p1-harness-repair.md`
8. `docs/sessions/session-014-real-product-to-brief-pilot-p1-harness-repair.md`

No ninth path is authorized. The Issue #343 P1 report and historical evidence,
Pilot Contract, P0 plan/Session-012, DEC-086/087, production export API and
projection beyond the retained test consumer, OpenAPI/generated client,
migrations/schema and dependencies/locks remain unchanged.

## Tests-first trace

### Observation — TRUE RED

Before the smoke change, the new unit regression ran the retained smoke with
interface-shaped fakes. Each fake snapshot response was `201` with exactly
`exportSnapshotId` and `contentLocation`; `snapshotId` was absent. The fake
client logged content-download requests.

```text
uv run --offline --project apps/backend python -m pytest apps/backend/tests/unit/test_fl2_live_controls.py::test_live_smoke_uses_public_export_snapshot_id_before_download -q
```

The test collected and executed but failed at the unchanged harness line with
`KeyError: 'snapshotId'`; the download log was empty. This was the required
behavioral RED, not an import, collection, dependency, environment or runtime
failure. The live-smoke implementation was byte-identical during RED.

### Observation — Minimal GREEN

After RED acceptance, the retained smoke's single response-key lookup changed
to `snapshot.json()["exportSnapshotId"]`. No fallback, dual-field compatibility
path, refactor or production export change was made. The existing late-failure
fake was aligned to the public response field so its cleanup behavior remains
covered.

The focused regression passed (`1 passed in 0.70s`). The affected live-smoke
controls, P1 characterization and export HTTP/renderer contract checks passed
(`89 passed in 5.64s`). The fake remains engineering evidence only and cannot
satisfy Pilot business acceptance.

## Current interpretation

The repair is branch-pending: `P1R_HARNESS_REPAIR_IN_PROGRESS` remains the
current branch status, and `HARNESS_BLOCKER = REPAIRED` is merge-effective only
after this PR reaches `main`. The repair makes no claim about the first failure
of the historical L5 run; that attribution remains `INCONCLUSIVE` as recorded
by Issue #343 / PR #344. P0 remains frozen and no P2, retry, substitution or
Provider execution is authorized.

## Validation and safety

The implementer ran the proportional provider-free and static checks before
handoff:

```text
Architecture boundary/import tests: 28 passed in 2.05s
Import Linter: 10 contracts kept, 0 broken
Backend Pyright (`uv run --offline pyright` from `apps/backend`): 0 errors, 0 warnings, 0 informations
Ruff format (`uv run --offline ruff format --check .` from `apps/backend`): 501 files already formatted
Ruff lint (`uv run --offline ruff check .` from `apps/backend`): All checks passed
`git diff --check` (including the two new files): PASS
Exact allowlist: 8 changed paths; protected/forbidden diff audit: PASS
Documentation local links/fences and stale-wording audit: PASS
```

No live smoke, PostgreSQL, Docker, browser, Product runtime, Provider, Secret
or `.env` action is selected.

Independent Sol five-axis review and fresh GitHub Required Checks remain merge
gates. The implementer does not approve or merge its own PR. If the PR is not
merged, close it without merging; after merge, rollback is an ordinary revert
of the repair merge commit with no runtime or data rollback.

## Relationships

- [Issue #345](https://github.com/JettxonHo/ai-ecommerce-agent/issues/345)
- [Issue #343 P1 characterization Session](session-013-real-product-to-brief-pilot-p1.md)
- [Issue #343 P1 characterization review](../reviews/real-product-to-brief-pilot-p1-characterization.md)
- [P1 harness-repair review](../reviews/real-product-to-brief-pilot-p1-harness-repair.md)
- [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md)
- [Implementation Readiness](../handoffs/implementation-readiness.md)
