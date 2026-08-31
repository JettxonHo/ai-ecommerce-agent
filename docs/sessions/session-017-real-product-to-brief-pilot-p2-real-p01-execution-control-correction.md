# Session-017 — REAL-P01 Execution-Control Correction

## Contract

Owner-authorized Issue #355 is one provider-free implementation cycle on
`main@925a0318135784429096ddf30de2a34982c55bc0`, branch
`codex/mbl-pilot-p2-real-p01-execution-control-correction`. It does not issue a
REAL-P01 Grant, read a Secret, call a Provider, connect to PostgreSQL, or run
P01/Pilot/participant work.

## Accepted scope

The cycle corrects four observed controls at their current real consumer:

1. explicit P01/A1 caller identity binding and exact-HEAD-before-DB ordering;
2. a complete five-key idempotency bundle precommitted before DB configuration,
   durably bound in immutable outside-Git attempt identity evidence;
3. status-aware in-process Task/Generate creation handling that stops on an
   unexpected `200` replay without changing public routes; and
4. current-truth documentation reconciliation in the six allowlisted
   surfaces, with this session and its companion review as evidence records.

The dormant database-collision blocker remains
`UNKNOWN_NOT_INSPECTED` and is intentionally deferred to a later Owner-
authorized pre-call.

## Pre-merge truth

`REAL_P01_INPUT_FILE_READY = YES` is the Owner-frozen handoff state; this
provider-free implementation did not inspect the private input or artifact
roots. `REAL_P01_PRE_CALL = BLOCKED_BY_EXECUTION_CONTROL_CORRECTION`.
`REAL_P01_GRANT = NOT_ISSUED`; `P01_ATTEMPT_EXECUTED = NO`;
`P01_RESULT = NOT_EXECUTED`; P02+ remains unauthorized. Provider calls, Secret
reads/injections, PostgreSQL access, Pilot/participant executions and charge
remain zero.

## Provider-free implementation evidence

The vertical slices are complete on the replacement branch: explicit identity
and exact-HEAD/static preflight, the five-key immutable bundle and durable
identity evidence, strict-new Task/Generate replay handling, and current-truth
reconciliation. Focused controls/composition/artifact/runner/architecture
tests pass (`99 passed, 4 skipped`); the
PostgreSQL composition file remains unchanged and skipped. Ruff, Pyright,
Import Linter and package build pass; no PostgreSQL/API/Docker lifecycle ran.

## Merge-conditional next state

Only after exact-head independent review, all Required Checks and a clean merge
may the correction be recorded as merge-effective. That merge would make the
old pre-call stale and require one fresh provider-free pre-call on the new
exact `main`; it would not authorize the real P01 Grant or execution.
