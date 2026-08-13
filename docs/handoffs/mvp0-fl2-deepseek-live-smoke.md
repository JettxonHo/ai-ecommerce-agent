# MVP-0 FL-2 DeepSeek V4 Pro live-smoke handoff

STATUS: IMPLEMENTED_OFFLINE_NOT_LIVE_VERIFIED

This handoff describes the opt-in seam delivered by Issue #270. No Provider
call, Secret read, credit use or PostgreSQL live smoke was performed while
implementing or reviewing the seam.

## Authorization gate

Do not run without new explicit user authorization after the adapter PR has
passed its Required Checks and independent review. The authorized run must use
one exact reviewed commit and one fictional `fixture-sufficient-v1` Anchor SKU
Task only.

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

## Expected run

The smoke makes five ordered, synchronous DeepSeek Chat Completions calls
through the existing deterministic pipeline, then performs one bounded review
and two immutable Markdown export/download checks. The runtime uses
`deepseek-v4-pro`, JSON Mode, enabled thinking, `reasoning_effort=high`, the
fixed per-stage token/time ceilings and SDK `max_retries=0`.

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
only after the separately authorized run passes and a human records the
result. This offline implementation itself remains
`IMPLEMENTED_OFFLINE_NOT_LIVE_VERIFIED`.
