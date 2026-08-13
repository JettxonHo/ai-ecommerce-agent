# MVP-0 FL-2 DeepSeek V4 Pro live-smoke handoff

STATUS: GOAL_BLOCKED_OFFLINE_DIAGNOSIS_AUTHORIZED_NOT_YET_DIAGNOSED_OR_REPAIRED

The opt-in seam was delivered by Issue #270. The first authorized run at
exact reviewed `main@1c7c2107ead332235d492ed063b67101784d35f1` later executed
one fictional Task and exactly five calls with zero retries and zero recovery
calls. It failed safely before `awaiting_review`, so the current Goal result is
`GOAL_BLOCKED`, with no Provider acceptance. The DEC-080 v2 deadline-fence repair was
implemented offline and merged as PR #280; the bounded legacy cleanup in Issue
#274 then completed. Issue #281 subsequently executed the second bounded smoke
at exact `main@ac4edfed6e8e216e9938affdc734298c8630d2de`. It made exactly one
`product_intake_v1 / v1` call and stopped on a fixed safe HTTP 500 during
generate-result, before `awaiting_review`. Its authorization is consumed and
the Issue is closed. No further Provider run is authorized.

The fifth call recorded 12,288 output tokens and 136,622 ms latency against the
historical `xiaohongshu_mapping_v1 / v1` limit of 12,288 / 120 s. Sanitized
evidence does not retain the raw finish reason or error category; this is a
bounded repair lead, not a proven root cause. PR #280 merged the offline `v2`
implementation at 16,384 / 240 s plus a post-return deadline fence. It does
not change the first run's `GOAL_BLOCKED` result.

## Issue #281 terminal result

The second run passed all fail-closed preflight gates and used the reviewed
smoke unchanged. Sanitized evidence records provider/model/API family
`deepseek / deepseek-v4-pro / chat_completions`, SDK 2.53.0, input 2,353 /
output 8,192 / total 10,545 tokens and 106,434 ms latency. Retry/recovery are
0/0, all five behavior gates are false, and stages 2～5 did not run.

The accepted `product_intake_v1 / v1` ceiling is 8,192 output tokens / 120 s.
Output equality with that ceiling is a diagnostic lead only, not a proven root
cause: evidence intentionally excludes finish reason, raw response/reasoning,
candidate content, traceback and internal error category. The call remained
below the configured timeout.

No rerun, repair, substitution, top-up or raw-material inspection occurred.
Credential, bounded PostgreSQL and temporary checkout/cache cleanup completed;
the exclusive sanitized evidence remains outside the repository.

The historical #281 execution selected the retained live test only when all of
these were explicit:

- `RUN_DEEPSEEK_LIVE_SMOKE=1`;
- `MVP0_RUN_TASK_HTTP_POSTGRES=1`;
- a nonblank `DEEPSEEK_API_KEY` supplied by the operator's process (the test
  module does not read or print it);
- `GIT_COMMIT` exactly matching the reviewed repository `HEAD`;
- an absolute `FL2_DEEPSEEK_LIVE_EVIDENCE_PATH` outside the repository's
  tracked source.

Missing controls skip or fail before client construction and PostgreSQL setup
as appropriate. Secret presence alone never selects the test. These retained
controls describe the seam; they do not authorize another execution.

## DEC-081 offline recovery boundary

[DEC-081](../decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md)
keeps the canonical status as **MVP-0 Fast Lane `GOAL_BLOCKED`; bounded offline
diagnosis authorized, not yet diagnosed or repaired.** FL-1 deterministic
completion is an accepted foundation only.

Phase A may build a fast, deterministic, red-capable offline loop around the
exact `product_intake_v1 / v1` first-stage boundary. It must rank and falsify
the existing safe failure hypotheses and reproduce/minimize the boundary
before any production repair. The 8,192-token ceiling equality remains only a
diagnostic lead. If sanitized evidence cannot distinguish hypotheses without
raw Provider material or another call, Phase A returns
`INSUFFICIENT_SANITIZED_EVIDENCE` and stops.

Phase B is unavailable until `ORCHESTRATOR_REVIEWER` independently reviews
Phase A and freezes a new exact bounded repair contract from reproduced
evidence. Neither phase authorizes a Provider, Secret, PostgreSQL/live, raw
material, migration, dependency, public contract or product-direction action.

## Current authorization boundary

The #281 authorization is consumed and no additional Provider call is
authorized. The retained opt-in seam is historical/testable code, not current
execution authority. DEC-081 authorizes Phase A offline diagnosis only. Any
future real Provider run requires a separate exact-commit contract and fresh
explicit user authorization.

Neither controlled run establishes DeepSeek Provider acceptance. The MVP-0
Fast Lane Goal remains `GOAL_BLOCKED`.
