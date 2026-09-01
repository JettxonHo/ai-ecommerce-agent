# Real Product-to-Brief Pilot P2 REAL-P01 Pre-call Handoff

> **Issue #355 current truth (pre-merge):** `main@925a0318135784429096ddf30de2a34982c55bc0` is the exact base for the bounded provider-free execution-control correction. The replacement branch is under implementation; no merge or execution authorization is implied. `REAL_P01_INPUT_FILE_READY = YES` reflects the Owner-frozen handoff and was not re-inspected by this implementation. `REAL_P01_PRE_CALL = BLOCKED_BY_EXECUTION_CONTROL_CORRECTION`; `REAL_P01_GRANT = NOT_ISSUED`; `P01_ATTEMPT_EXECUTED = NO`; `P01_RESULT = NOT_EXECUTED`; `Blocker 3 = UNKNOWN_NOT_INSPECTED`; Provider calls, Secret reads/injections, PostgreSQL access, Pilot/participant executions and charge remain zero. After an independently reviewed merge, a fresh exact-main provider-free pre-call is required; the real P01 Grant remains unissued.

**Main status:** Issue [#352](https://github.com/JettxonHo/ai-ecommerce-agent/issues/352)
and PR #353 are merge-effective at
`main@87f5315074bb3858ff09163c38c84b6e1e834577`, with durable main truth
`REAL_P01_EXECUTION_CONTROL_ALIGNED = YES`. **Current branch status:** Issue
#355 is the bounded provider-free execution-control correction on this branch
and is not merged. This handoff records controls only; it is not a Provider
Grant, a Pilot run, or business acceptance.

## Scope and allowlist

The historical Issue #352 / PR #353 implementation changed exactly these eight
paths:

1. `apps/backend/tests/integration/test_p2_deepseek_real_product_live.py`
2. `apps/backend/tests/unit/test_p2_live_controls.py`
3. `AGENTS.md`
4. `README.md`
5. `apps/web/README.md`
6. `docs/goals/real-product-to-brief-pilot-goal.md`
7. `docs/handoffs/implementation-readiness.md`
8. this handoff

Issue #355 changes only the exact 15-path allowlist in its frozen contract,
including the two provider-free control modules and their tests:

1. `apps/backend/src/ai_ecommerce_agent/bootstrap/pilot_p2_operator.py`
2. `apps/backend/src/ai_ecommerce_agent/orchestration/pilot_attempt_artifact.py`
3. `apps/backend/tests/integration/test_p2_deepseek_real_product_live.py`
4. `apps/backend/tests/integration/test_pilot_p2_postgres_composition.py`
5. `apps/backend/tests/unit/test_p2_live_controls.py`
6. `apps/backend/tests/unit/test_pilot_p2_composition.py`
7. `apps/backend/tests/contract/test_pilot_attempt_artifact_contract.py`
8. `AGENTS.md`
9. `README.md`
10. `apps/web/README.md`
11. `docs/goals/real-product-to-brief-pilot-goal.md`
12. `docs/handoffs/implementation-readiness.md`
13. this handoff
14. `docs/reviews/real-product-to-brief-pilot-p2-real-p01-execution-control-correction.md`
15. `docs/sessions/session-017-real-product-to-brief-pilot-p2-real-p01-execution-control-correction.md`

The PostgreSQL composition test remains unchanged; no PostgreSQL/API/Docker
lifecycle is authorized.

Issue #355 changes the `PilotP2Operator` execution-control module and the
artifact service's internal identity evidence seam. The cost gate,
PostgreSQL/FastAPI composition, migrations/schema, OpenAPI/generated client,
dependencies/locks, private roots, `.env`, Secret and Provider paths remain
unchanged and protected.

## Pre-call controls

- A future run must receive a non-secret `GIT_COMMIT` environment handoff. The
  value is forwarded unchanged as `authorized_commit`, `git_commit` and
  `git_head`; the protected operator performs exact actual-HEAD validation.
  Missing or blank handoff fails before binder construction. A stale value
  fails at the existing core head check before artifact reservation or any
  runtime side effect. Branch/latest inference is not allowed.
- The canonical artifact parent is
  `/Users/ketchup/Private/ai-ecommerce-pilot`; the exact artifact root is
  `/Users/ketchup/Private/ai-ecommerce-pilot/p2/P01/P2-P01-A1`. The live-control
  field is `approved_artifact_parent`. The old parent-at-`.../p2` geometry is
  rejected before binder construction, while absent-root and exclusive
  reservation remain protected core behavior.
- The only accepted future input handoff is
  `/Users/ketchup/Private/ai-ecommerce-pilot/inputs/p01-public.txt`. A missing,
  symlinked, non-regular or non-canonical handoff fails before binder/artifact
  work. The runner does not search, synthesize, read alternate files or use a
  fixture/default fallback. Provider-free tests use only a `tmp_path` regular
  UTF-8 synthetic fixture and do not expose its contents.
- The existing Grant-absence gate remains first. Retry, recovery, replay,
  fallback and automatic repair remain zero and unauthorized.
- The caller must bind the exact P01/A1 identity and complete five-key
  idempotency bundle before database configuration. Task and Generate must
  return `201` for a new operation; an unexpected `200` replay stops safely.

## Current truth and stop boundary

Issue #355 is not a Grant. The prior pre-merge branch wording that marked
alignment pending independent review is historical only; PR #353 is on main.
`REAL_P01_INPUT_FILE_READY=YES` is the Owner-frozen handoff state; this
provider-free implementation did not inspect or create the private input or
artifact roots, and no real P01 content is retained. The current pre-call is
blocked by the correction; Blocker 3 remains `UNKNOWN_NOT_INSPECTED`.

```text
REAL_P01_EXECUTION_CONTROL_ALIGNED = YES
REAL_P01_GRANT = NOT_ISSUED
REAL_P01_INPUT_FILE_READY = YES
REAL_P01_PRE_CALL = BLOCKED_BY_EXECUTION_CONTROL_CORRECTION
Blocker 3 = UNKNOWN_NOT_INSPECTED
AUTHORIZATION_STATUS = REQUIRES_NEW_OWNER_GRANT
PILOT_EXECUTION_AUTHORIZATION = NOT_AUTHORIZED
P01_ATTEMPT_EXECUTED = NO
P01_RESULT = NOT_EXECUTED
P02_PLUS = NOT_AUTHORIZED
SECRET_STATUS = NOT_CHECKED
Provider calls = 0
Paid model calls = 0
Secret reads/injections = 0
Private-root inspection = 0
Input/artifact creation = 0
Actual charge = USD 0
```

Issue #355 still needs independent exact-head review and fresh Required Checks
(including secret-detection); after merge the old pre-call is stale and a fresh
provider-free pre-call is required. The next single action is
`WAIT_FOR_ISSUE_355_REVIEW_AND_MERGE`.
