# MVP-0 FL-2 DeepSeek V4 Pro live-smoke handoff

STATUS: GOAL_BLOCKED_REPAIR_MERGED_OFFLINE_CLEANUP_DELIVERED_ON_MERGE_SECOND_V2_AUTHORIZED_NOT_EXECUTED

The opt-in seam was delivered by Issue #270. The single previously authorized run at
exact reviewed `main@1c7c2107ead332235d492ed063b67101784d35f1` later executed
one fictional Task and exactly five calls with zero retries and zero recovery
calls. It failed safely before `awaiting_review`, so the current Goal result is
`GOAL_BLOCKED`, not live verified. The DEC-080 v2 deadline-fence repair was
implemented offline and merged as PR #280; the bounded legacy cleanup in Issue
#274 is delivered on merge. Issue #281 supplies explicit user authorization and
the exact second-run contract, currently `AUTHORIZED_NOT_EXECUTED`: exactly one
fictional Task, five ordered calls and zero retry/recovery, only after #274
Phase B is independently reviewed, checks pass and merges. Execution is
outside #274 and requires ORCHESTRATOR exact-commit GO, with no further user
confirmation.

The fifth call recorded 12,288 output tokens and 136,622 ms latency against the
historical `xiaohongshu_mapping_v1 / v1` limit of 12,288 / 120 s. Sanitized
evidence does not retain the raw finish reason or error category; this is a
bounded repair lead, not a proven root cause. PR #280 merged the offline `v2`
implementation at 16,384 / 240 s plus a post-return deadline fence. It does
not change the first run's `GOAL_BLOCKED` result.

## Authorization gate

The #281-authorized run remains outside this Issue and is not executed by Phase
B. It may run only after #274 Phase B has passed Required Checks and independent
review and has merged, with ORCHESTRATOR exact-commit GO. It uses one exact
reviewed commit and one fictional `fixture-sufficient-v1` Anchor SKU Task only;
no further user confirmation is required. Any run or Provider action outside
this exact one-Task/five-ordered-calls/zero-retry-or-recovery boundary requires
a new contract and explicit user authorization.

The live test is selected only when all of these are explicit:

- `RUN_DEEPSEEK_LIVE_SMOKE=1`;
- `MVP0_RUN_TASK_HTTP_POSTGRES=1`;
- a nonblank `DEEPSEEK_API_KEY` supplied by the operator's process (the test
  module does not read or print it);
- `GIT_COMMIT` exactly matching the reviewed repository `HEAD`;
- an absolute `FL2_DEEPSEEK_LIVE_EVIDENCE_PATH` outside the repository's
  tracked source.

Missing controls skip or fail before client construction and PostgreSQL setup
as appropriate. Secret presence alone never selects the test.

## #281 bounded run (authorized, not executed)

The smoke would make five ordered, synchronous DeepSeek Chat Completions calls
through the existing deterministic pipeline, then performs one bounded review
and two immutable Markdown export/download checks. The runtime uses
`deepseek-v4-pro`, JSON Mode, enabled thinking, `reasoning_effort=high`, the
fixed versioned per-stage token/time ceilings and SDK `max_retries=0`.

Any timeout, ambiguous transport failure, access/balance/model failure, empty
or invalid output, schema failure or Fast Lane domain-admission failure stops
the run. There is no transport retry, repair, regeneration, second Task,
second model/provider, or top-up.

Evidence is append-only and provider-neutral. It records only the reviewed
commit, timing, disposition, safe call metadata, retry/recovery counts and the
fixed behavior-gate booleans. It excludes the Secret, account/balance data,
fixture text, prompt/context, raw response, reasoning, candidate, Markdown
content and traceback.

The #281-authorized run may be reported as `DeepSeek V4 Pro direct live
verified` only if it passes and a human records the result. The first run
remains `GOAL_BLOCKED`; the offline repair itself cannot change that status.
