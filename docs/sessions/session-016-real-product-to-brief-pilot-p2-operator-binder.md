# Session-016 — Real Product-to-Brief Pilot P2 Operator Binder

**Date:** 2026-08-31

**Base:** `cb77de2f96954a2d63ef00eead2f93bea1197649`

**Branch status:** `OPERATOR_BINDER_IMPLEMENTATION_PENDING_REVIEW`

## Fact: merge-effective prerequisite

Issue #347 / PR #349 is merged and made provider-free P2 readiness
`P2_READINESS_IMPLEMENTED = YES` at the exact current `main` commit
`cb77de2f96954a2d63ef00eead2f93bea1197649`. The real P01 Grant is
`NOT_CONSUMED`; no Provider, Secret, Pilot or participant action is authorized.
Issue #350 is the sole follow-up Issue for the operator-binder outcome.

## Fact: bounded implementation

The branch adds one deep production module,
`bootstrap/pilot_p2_operator.py`, with `PilotP2Operator.apply(command)` and
`read()`. Its four typed commands own one resumable lifecycle:

1. `StartAttempt` validates actual repository HEAD, exact P01/input/cap/
   pricing/root controls before side effects, reads only the validated input
   path (there is no caller text bypass), reserves the outside-Git root,
   composes the existing P2 PostgreSQL/FastAPI application, persists real
   Task/Input/Result identities and revisions, validates the concrete
   observer's ordered calls, and pauses at `AWAITING_CONFIRMATION` without
   auto-confirm or review.
2. `ConfirmAndCapture` closes/recomposes from Business Truth, makes zero model
   calls, requires explicit confirmation values, confirms the persisted result,
   captures one or two exact immutable HTTP exports and returns
   `PENDING_HUMAN_REVIEW`.
3. `SubmitHumanReview` records one explicit immutable seven-dimension
   APPROVED/REJECTED decision with exact role/time/rationale/notes and
   inspected export IDs; no review values are inferred.
4. `FinalizeAttempt` records explicit PASS/FAIL/BLOCKED. PASS qualification
   is derived from captured export sidecars, not predeclared in `run.json`;
   actual invoice charge is typed unknown when runtime metadata cannot derive
   it, never replaced by a reservation or bound.

The existing P2 composition now exposes a minimum sanitized runtime observer
for call order/status, attempted/completed counts, runtime metadata and usage;
the public Model Runtime contract is unchanged. Artifact finalization accepts
missing result identity only for non-PASS failure and permits a typed unknown
actual cost only when the persisted reservation is a known value within the
explicit Owner cap and pricing reference. Any attempted call without usage
produces fully typed unknown aggregate usage. Durable persistence errors and
cleanup errors are surfaced as fixed safe binder categories; cleanup cannot
mask a primary durable failure.

## Observation: tests-first progression

The six required vertical seams were executed one at a time with tests-only
RED before each production increment:

- Start fake-five-call success and actual persisted IDs;
- stage-3 runtime failure with durable safe terminal evidence;
- head/input/cap/pricing/root rejection before artifact/PG/runtime/client;
- recomposed Confirm/export capture with zero runtime calls;
- explicit Human Review and PASS/FAIL finalization with unknown actual cost;
- thin future-Grant-gated live entrypoint calling the production binder.

The focused provider-free suite is `89 passed, 4 skipped`. Full backend
non-live regression is `2164 passed, 22 skipped, 4 deselected`; Pyright,
Ruff, Import Linter and `uv build` are green. A guarded PostgreSQL/API
integration lifecycle drove the production binder end-to-end with a fake
runtime and passed once on a unique loopback/paired-volume scope; cleanup
removed only owned resources.

The guarded cleanup helper itself returned RC 0; the surrounding shell audit
then hit an unquoted `YES` comparison under `set -u` and exited nonzero. A
separate exact check confirmed the generated container and paired volume were
absent and loopback 55432 was free. This is a harness-only observation and
does not change the binder lifecycle PASS.

## Observation: independent review remediation

The independent Sol/xhigh review at the initial follow-up head requested
explicit human/business inputs, file-truth input loading, concrete observer
telemetry validation, durable failure/cleanup behavior, production-binder-only
live delegation, durable Task/Input/Result identity, and reservation/usage
truth. The follow-up tree removes confirmation/review defaults and the live
factory override, validates exact observed calls and DTO identities, persists
the input revision reference, raises safe durability/cleanup categories,
requires complete usage or typed unknowns, and checks a known reservation
against the explicit Owner cap before unknown-actual PASS. The branch remains
merge-conditional pending fresh independent review and Required Checks.

## Fact: preserved boundaries

The exact Issue #350 18-path allowlist is unchanged. No migration/schema,
OpenAPI/generated client/public route, dependency/lockfile, `local_demo.py`,
default scripted path, Pilot Contract/P0 plan, private P01 material, `.env`,
Secret, Provider, participant, UI or numerator/denominator behavior changed.
The existing #347 / PR #349 review and Session-015 history remain intact.

## External-action truth

```text
Provider calls = 0
Paid model calls = 0
Secret reads = 0
Secret injections = 0
Actual charge = USD 0
Pilot samples executed = 0
Participant executions = 0
REAL_P01_GRANT = NOT_CONSUMED
P01_ATTEMPT_EXECUTED = NO
P01_RESULT = NOT_EXECUTED
P02_PLUS = NOT_AUTHORIZED
SECRET_STATUS = NOT_CHECKED
```

## Archive result

- This session records the Issue #350 provider-free operator-binder branch and
  its merge-conditional status.
- Previous Decisions, Contract, P0/P1 history and the merge-effective #347 /
  PR #349 evidence were not rewritten.
- No ADR was needed: the implementation reuses accepted seams and introduces
  no hard-to-reverse architecture or public-contract decision.
- Independent Sol/xhigh review, fresh Required Checks and a clean Ready PR
  remain outstanding; merge is not performed by the implementing worker.
