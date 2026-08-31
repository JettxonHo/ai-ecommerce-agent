# Real Product-to-Brief Pilot P2 REAL-P01 Pre-call Handoff

**Main status:** Issue [#352](https://github.com/JettxonHo/ai-ecommerce-agent/issues/352)
and PR #353 are merge-effective at
`main@87f5315074bb3858ff09163c38c84b6e1e834577`, with durable main truth
`REAL_P01_EXECUTION_CONTROL_ALIGNED = YES`. **Current branch status:** this
branch carries only a docs-only closure follow-up for the same Issue #352
record; its follow-up PR is pending review. This handoff records controls only;
it is not a Provider Grant, a Pilot run, or business acceptance.

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

The current closure follow-up changes only these six already-allowlisted docs:

1. `AGENTS.md`
2. `README.md`
3. `apps/web/README.md`
4. `docs/goals/real-product-to-brief-pilot-goal.md`
5. `docs/handoffs/implementation-readiness.md`
6. this handoff

The code and tests remain byte-identical to merge-effective `main`.

The protected `PilotP2Operator`, artifact service, cost gate,
PostgreSQL/FastAPI composition, migrations/schema, OpenAPI/generated client,
dependencies/locks, private roots, `.env`, Secret and Provider paths are
unchanged.

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

## Current truth and stop boundary

The historical held Grant remains `NOT_CONSUMED_BUT_STALE_FOR_NEW_MAIN` for
any future exact-main run. The pre-merge branch wording that marked alignment
pending independent review is historical only; PR #353 is now on main.
`REAL_P01_INPUT_FILE_READY=NO` is based only on Owner/pre-call authority. This
provider-free implementation run did not inspect or create the private input
or artifact roots, and no real P01 content is retained. A future run with a
new Grant may perform only the metadata pre-call checks described above.

```text
REAL_P01_EXECUTION_CONTROL_ALIGNED = YES
REAL_P01_GRANT = NOT_CONSUMED_BUT_STALE_FOR_NEW_MAIN
REAL_P01_INPUT_FILE_READY = NO
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

The current docs-only closure follow-up still needs independent review and
fresh Required Checks (including secret-detection), but it does not change the
already merge-effective alignment. The next single action is
`WAIT_FOR_REAL_P01_INPUT_HANDOFF_AND_NEW_EXACT_MAIN_OWNER_GRANT`.
