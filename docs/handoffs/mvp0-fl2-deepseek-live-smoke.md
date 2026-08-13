# MVP-0 FL-2 DeepSeek V4 Pro live-smoke handoff

STATUS: GOAL_BLOCKED_REPAIR_AUTHORIZED_OFFLINE_NO_SECOND_LIVE

The opt-in seam was delivered by Issue #270. One separately authorized run at
exact reviewed `main@1c7c2107ead332235d492ed063b67101784d35f1` later executed
one fictional Task and exactly five calls with zero retries and zero recovery
calls. It failed safely before `awaiting_review`, so the current Goal result is
`GOAL_BLOCKED`, not live verified.

The fifth call recorded 12,288 output tokens and 136,622 ms latency against the
historical `xiaohongshu_mapping_v1 / v1` limit of 12,288 / 120 s. Sanitized
evidence does not retain the raw finish reason or error category; this is a
bounded repair lead, not a proven root cause. DEC-080 authorizes only an
offline `v2` implementation at 16,384 / 240 s plus a post-return deadline
fence. It does not authorize a second live run.

## Authorization gate

Do not run again without new explicit user authorization after the DEC-080
implementation PR has passed its Required Checks and independent review. A
future authorized run must use one exact reviewed commit and one fictional
`fixture-sufficient-v1` Anchor SKU Task only.

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

## Future bounded run, only if separately authorized

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

The terminal result may be reported as `DeepSeek V4 Pro direct live verified`
only after a new separately authorized run passes and a human records the
result. The first run remains `GOAL_BLOCKED`; the offline repair itself cannot
change that status.
