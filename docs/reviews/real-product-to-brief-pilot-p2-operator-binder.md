# Real Product-to-Brief Pilot P2 Operator-Binder Review

**Status on this branch:** `OPERATOR_BINDER_IMPLEMENTATION_PENDING_REVIEW`

**Merge-effective prerequisite:** Issue #347 / PR #349 made
`P2_READINESS_IMPLEMENTED = YES` at `main@cb77de2f96954a2d63ef00eead2f93bea1197649`.
This Issue does not alter that history. Only an independent review and a Ready
PR for Issue #350 reaching `main` may record
`OPERATOR_BINDER_IMPLEMENTED = YES`.

## Authority and bounded outcome

Issue #350 delivers exactly:

```text
REAL_P01_OPERATOR_BINDER_PROVIDER_FREE_READY
```

The implementation is the provider-free, repository-owned binder for the
already merged P2 seams. It does not execute a real P01 attempt, consume the
held Grant, or claim Pilot/business acceptance. The frozen P0 → P6 order,
P01–P08 cohort, denominator eight and human/Provider gates remain unchanged.

Authority is [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md),
[DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md),
the [Pilot Goal](../goals/real-product-to-brief-pilot-goal.md), [Pilot
Contract](../product/real-product-to-brief-pilot-contract.md), [P0
plan](../product/real-product-to-brief-pilot-p0-plan.md), and the merge-effective
[P2 readiness review](real-product-to-brief-pilot-p2-readiness.md) and
[Session-015](../sessions/session-015-real-product-to-brief-pilot-p2-readiness.md).

## Deep module interface

`apps/backend/src/ai_ecommerce_agent/bootstrap/pilot_p2_operator.py` exposes
one small interface:

```text
PilotP2Operator.apply(command) -> PilotP2OperatorSnapshot
PilotP2Operator.read() -> PilotP2OperatorSnapshot
```

The four typed commands are `StartAttempt`, `ConfirmAndCapture`,
`SubmitHumanReview` and `FinalizeAttempt`. The module hides the existing
Task/Input/Result/Review-Export HTTP choreography, idempotency keys,
PostgreSQL composition close/recompose, export DTO translation,
`PilotAttemptArtifacts` commands, runtime observation and cleanup.

## Lifecycle evidence

- **Start:** actual repository HEAD, exact P01 identity/input boundary, fixed
  pricing record, explicit positive Owner cap and absent artifact root are
  validated before artifact/PG/runtime/client/network access. The exact root
  is reserved outside Git, Task and Primary Input are persisted through the
  existing HTTP seam, and the lazy P2 coordinator runs at most five ordered
  calls. Success records actual Task/Input/Result identities and observed
  call metadata, then returns `AWAITING_CONFIRMATION` without auto-confirm or
  Human Review.
- **Durable failure:** a provider/runtime or later generation failure leaves
  sanitized run evidence with attempted/completed counts, ordered call IDs,
  fixed safe category/stage, zero retry/recovery/replay/fallback counts,
  typed usage/cost unknowns and terminal `FAIL`. Missing result identity is
  permitted only for non-PASS generation failure.
- **Resume:** `ConfirmAndCapture` recomposes the same persisted Task/Input/
  Result lifecycle and performs zero runtime calls. It explicitly confirms
  the result, creates one or two existing immutable Markdown snapshots,
  downloads exact bytes and captures their IDs/metadata/sidecars, returning
  `PENDING_HUMAN_REVIEW`. Run evidence keeps `export=false`; finalization
  derives qualification from captured immutable sidecars.
- **Review/finalization:** `SubmitHumanReview` requires an explicit
  APPROVED/REJECTED decision and binds the exact export IDs to the seven P0
  dimensions. `FinalizeAttempt` is explicit: APPROVED plus a qualifying
  sidecar can produce PASS; REJECTED produces non-qualifying FAIL. No review
  or approval is inferred. Usage input/output/total is persisted when
  exposed; actual invoice cost remains typed `NOT_EXPOSED` or `NOT_DERIVABLE`
  when the current runtime metadata cannot reproduce it. Reservation, Owner
  cap and actual charge remain distinct.

## Exact Issue #350 allowlist

Production:

1. `apps/backend/src/ai_ecommerce_agent/bootstrap/pilot_p2_operator.py`
2. `apps/backend/src/ai_ecommerce_agent/bootstrap/pilot_p2.py`
3. `apps/backend/src/ai_ecommerce_agent/orchestration/pilot_attempt_artifact.py`
4. `apps/backend/src/ai_ecommerce_agent/platform/model_runtime/deepseek/_cost_gate.py`

Tests:

5. `apps/backend/tests/unit/test_p2_live_controls.py`
6. `apps/backend/tests/unit/test_pilot_p2_composition.py`
7. `apps/backend/tests/unit/test_deepseek_cost_gate.py`
8. `apps/backend/tests/contract/test_pilot_attempt_artifact_contract.py`
9. `apps/backend/tests/integration/test_pilot_p2_postgres_composition.py`
10. `apps/backend/tests/integration/test_p2_deepseek_real_product_live.py`
11. `apps/backend/tests/architecture/test_pilot_p2_composition_boundaries.py`

Current truth/evidence:

12. `AGENTS.md`
13. `README.md`
14. `apps/web/README.md`
15. `docs/goals/real-product-to-brief-pilot-goal.md`
16. `docs/handoffs/implementation-readiness.md`
17. `docs/reviews/real-product-to-brief-pilot-p2-operator-binder.md`
18. `docs/sessions/session-016-real-product-to-brief-pilot-p2-operator-binder.md`

No nineteenth path is required or changed. Migrations/schema, OpenAPI/
generated client/public routes, dependencies/locks, `local_demo.py`, default
scripted path, Pilot Contract/P0 plan, private P01 material, `.env`, Secret,
Provider, participant and UI behavior remain protected.

## Verification

Provider-free local evidence on this branch:

- focused binder/P2/artifact/cost/live-control suite: `72 passed, 5 skipped`;
- backend non-live regression: `2151 passed, 22 skipped, 3 deselected`;
- Pyright: `0 errors, 0 warnings, 0 informations` on affected production and
  tests;
- Ruff format/check: PASS;
- Import Linter: `10 kept, 0 broken`;
- `uv build`: source distribution and wheel PASS;
- guarded PostgreSQL/API binder lifecycle: one PASS through repository
  lifecycle helpers, fake runtime, exact loopback and paired-volume cleanup;
- exact 13-path changed subset is within the Issue #350 18-path allowlist;
  protected paths are untouched, docs links/fences resolve, and
  `git diff --check` passes.

The guarded lifecycle used a unique ephemeral project/paired volume on
`127.0.0.1:55432`; owned resources were removed and the port was free. No raw
Compose command was used.

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

The thin opt-in live entrypoint remains skipped without a separate future
Grant and never reads a Secret in this Issue. The implementing worker has not
reviewed, approved or merged this branch. Independent Sol/xhigh five-axis
review and fresh Required Checks, including secret-detection, remain required.
