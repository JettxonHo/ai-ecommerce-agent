# MVP-0 FL-2 DeepSeek V4 Pro live-smoke handoff

STATUS: GOAL_BLOCKED_PHASE_A_TERMINAL_INSUFFICIENT_SANITIZED_EVIDENCE_NO_PRODUCTION_REPAIR_NO_PHASE_B_CONTRACT

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
the Issue is closed. No further Provider run is authorized from that historical
contract; a new L5 Stage must pass its own gates.

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
the exclusive sanitized evidence remains outside the repository. Those two
authorizations are consumed; a new L5 Stage requires its own exact-commit
contract and owner authorization.

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
keeps the canonical status as **MVP-0 Fast Lane `GOAL_BLOCKED`; Phase A is
complete with terminal disposition `INSUFFICIENT_SANITIZED_EVIDENCE`.** FL-1
deterministic completion is an accepted foundation only.

Phase A completed a fast, deterministic, red-capable offline loop around the
exact `product_intake_v1 / v1` first-stage boundary. The same retained safe
signature reached multiple actual mapper, project-schema and domain-admission
rejection boundaries, so the result is observational ambiguity only and does
not identify the historical cause. The 8,192-token ceiling equality remains
only a diagnostic lead. The terminal disposition is
`INSUFFICIENT_SANITIZED_EVIDENCE`.

No production repair was made and no Phase B contract exists. Any future Phase
B would require independent `ORCHESTRATOR_REVIEWER` review and a new exact
bounded repair contract from reproduced evidence. `rejection_disposition`
remains a Proposal only, not an Accepted Decision or current truth. Neither
phase authorizes a Provider, Secret, PostgreSQL/live, raw material, migration,
dependency, public contract or product-direction action.

## Current authorization boundary

The #281 authorization is consumed and no additional Provider call is
authorized without a new L5 Gate. The retained opt-in seam is
historical/testable code, not current execution authority. DEC-081 Phase A is complete with terminal
`INSUFFICIENT_SANITIZED_EVIDENCE`; no production repair or Phase B contract
exists. Any future real Provider run requires a separate exact-commit contract
and fresh explicit user authorization.

Neither controlled run establishes DeepSeek Provider acceptance. The MVP-0
Fast Lane Goal remains `GOAL_BLOCKED`.

## MVP-0L L5 Phase A harness (Issue #335)

STATUS: `L5_HARNESS_REVIEW_READY` — owner authorization pending

Issue #335 prepares the retained opt-in smoke seam for a future, separately
authorized DeepSeek acceptance. The new explicit control
`FL2_DEEPSEEK_LIVE_EXPORT_DIR` must name an absolute target outside the
repository that does not already exist. Module preflight rejects an invalid or
existing target before private credential/runtime resolution, client creation,
PostgreSQL setup or network activity.

After the existing five-call Task-to-export path has passed all automated gates,
Phase A preserves exactly `marketing-brief.md` and `xiaohongshu-brief.md` with
exclusive/no-overwrite creation. Payloads remain UTF-8, BOM-free and exactly
one final newline. Failed validation or smoke execution retains only the
existing sanitized evidence record and does not fabricate review exports; raw
Provider response/reasoning, prompts, context, candidates, tracebacks, Secrets,
account data and database rows are not written.

Tests-first evidence is recorded in the [L5 Phase-A review](../reviews/mvp0l-l5-deepseek-live-acceptance.md): the unchanged harness produced
`4 failed, 3 passed`, then the minimal edit produced `7 passed`, affected Ruff
format/lint PASS and `git diff --check` PASS. No Provider, Secret, Docker,
PostgreSQL, API/Web/browser or paid runtime action occurred. The current truth
is harness review-ready only; no live success is claimed and no owner
authorization is implied.

## MVP-0L L4 qualification (Issue #333)

STATUS: `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR_REVIEW_READY`

The fresh exact-base Phase-A review at
`origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e` re-traced the retained
five-stage DeepSeek path and reran the existing synthetic/sanitized offline
diagnosis plus directly affected DeepSeek, pipeline, schema and architecture
tests. The current request/profile/version tuples, JSON-mode preparation,
response mapper, project-schema validation and Fast Lane domain admission are
coherent. The retained safe signature remains compatible with multiple real
mapper/schema/domain rejection categories, so no general correctness RED
justifies a repair. The exact disposition is
`L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`; production diff is zero and no
Phase-B amendment exists.

Current first-party DeepSeek documentation was rechecked read-only from
`api-docs.deepseek.com`: [Quick Start](https://api-docs.deepseek.com/), [Chat
Completions API](https://api-docs.deepseek.com/api/create-chat-completion/),
[JSON Output](https://api-docs.deepseek.com/guides/json_mode/), [Thinking
Mode](https://api-docs.deepseek.com/guides/thinking_mode/) and [Models &
Pricing](https://api-docs.deepseek.com/quick_start/pricing/). It continues to
document `https://api.deepseek.com`, `deepseek-v4-pro`, Chat Completions JSON
Output, enabled thinking with `reasoning_effort=high`, reasonable
`max_tokens`, `finish_reason=length` truncation and occasional empty content.
No documentation drift affects the frozen path. This offline qualification is
not live Provider acceptance and does not authorize L5, a Secret access or a
new run.
