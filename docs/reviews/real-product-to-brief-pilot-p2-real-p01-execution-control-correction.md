# Real Product-to-Brief Pilot P2 REAL-P01 Execution-Control Correction

**Status:** `READY_FOR_INDEPENDENT_REVIEW` on the exact base
`925a0318135784429096ddf30de2a34982c55bc0`.

**Scope:** Issue #355 is one bounded provider-free correction. It binds the
authoritative P01/A1 caller identity, precommits and durably records the five
internal idempotency keys, rejects unexpected Task/Generate replay statuses,
and reconciles current-truth documentation. Public routes, database schema,
migrations, cost/model policy and the accepted P0 cohort remain unchanged.

## Merge-conditional outcome

`REAL_P01_EXECUTION_CONTROL_CORRECTION = MERGED_PROVIDER_FREE` is conditional
on an independent exact-head review, all Required Checks, and a clean merge.
After such a merge, the old pre-call is stale and a fresh provider-free
pre-call on the new exact `main` is required. This Issue never authorizes a
real P01 run or Grant.

## Provider-free evidence contract

- `StartAttempt` requires explicit `sample_id=P01` and
  `attempt_id=P2-P01-A1`; omission or mismatch fails before artifact or
  composition work.
- The runner verifies the owner `GIT_COMMIT` against the caller checkout and
  validates all seven frozen P01 identity markers before reading the database
  URL. It forwards the exact identity and a complete immutable key bundle.
- The bundle keys are `task_create`, `generate`, `confirm`,
  `marketing_export`, and `xiaohongshu_export`; the outside-Git attempt
  `identity.json` records the bundle when supplied and a fresh artifact read
  validates it.
- The in-process HTTP adapter preserves response status for the two
  creation-required operations. A `200` replay where `201` is required raises
  a fixed `unexpected_replay` error before downstream generation. Existing
  public route semantics are unchanged.
- Blocker 3, dormant database collision, remains
  `UNKNOWN_NOT_INSPECTED`; this Issue does not connect to or inspect
  PostgreSQL.

## Provider-free validation

- Focused control, composition, artifact, runner and architecture tests:
  `99 passed, 4 skipped`.
- Backend non-live regression (`-m "not live and not slow"`):
  `2189 passed, 22 skipped, 4 deselected`.
- Ruff format/check, Pyright and Import Linter (`10 kept, 0 broken`) pass.
- `uv build` passes.
- The PostgreSQL composition integration file is unchanged and remains
  opt-in/skipped; no PostgreSQL/API/Docker lifecycle was run.
- Current-truth marker and stale-assertion checks pass across all six
  synchronized surfaces. Fourteen paths changed; the unchanged PG test is the
  fifteenth allowlisted path.

## External-action truth

Throughout this implementation cycle: Provider calls `0`, Secret reads and
injections `0`, PostgreSQL/Docker lifecycle actions `0`, real P01/Pilot and
participant executions `0`, artifacts in the real private root `0`, and
charge `USD 0`. The Owner-frozen input handoff is current
`REAL_P01_INPUT_FILE_READY = YES`; this implementation does not inspect the
private input or artifact roots. Current pre-call state is
`REAL_P01_PRE_CALL = BLOCKED_BY_EXECUTION_CONTROL_CORRECTION` and
`REAL_P01_GRANT = NOT_ISSUED`.

## Review and merge boundary

The implementer does not self-review, approve or merge. Sol performs a fresh
five-axis review on the exact PR head. Merge is allowed only when the exact
base/head, allowlist, Required Checks, secret detection, review and clean
merge state all pass. The post-merge gate remains
`REAL_P01_GRANT = NOT_ISSUED`.
