# MVP-0L L4 DeepSeek offline qualification

**Issue:** [#333](https://github.com/JettxonHo/ai-ecommerce-agent/issues/333)
**Branch:** `codex/mvp0l-l4-deepseek-offline-qualification`
**Reviewed base:** `2124a9bb20d6b7b327c828331bdc8293ec76577e`
**Disposition:** `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`

## Result

Phase A completed as a read-only, provider-free qualification of the retained
official DeepSeek path. The current repository seams are coherent, the
sanitized diagnosis remains observationally ambiguous, and no reproducible
general correctness defect justified a production repair. Production diff is
zero. No Phase-B amendment, `rejection_disposition`, profile/prompt/schema/
domain/runtime/evidence/public-contract/dependency change was created.

This is not live Provider acceptance, does not reopen the consumed historical
authorizations, and does not authorize L5. The historical Fast Lane remains
`GOAL_BLOCKED`; the accepted `8192 == max_tokens` observation remains a
diagnostic lead only.

## Scope and controls

- Fresh isolated clone was created at the reviewed base above. `origin/main`
  and `HEAD` both resolved to that SHA; the worktree was clean before edits.
- The custom worker configuration was parsed with Python 3.12 `tomllib` from
  `/Users/ketchup/.codex/agents/luna-worker.toml`: `name=luna-worker`,
  `model=gpt-5.6-luna`, `model_reasoning_effort=max`. This records
  `CONFIG_VERIFIED` only; runtime model identity is not claimed.
- Only the eight Issue pre-amendment slots were considered: this review,
  `AGENTS.md`, `README.md`, `apps/web/README.md`, the Goal, the readiness
  handoff, the DeepSeek live-smoke handoff, and at most one offline diagnostic
  test. No diagnostic test was added because the retained suite demonstrates
  the required invariant.
- No Secret or environment value was read, created, inspected, printed,
  measured or hashed. No `.env`, `DEEPSEEK_API_KEY`, Provider/model/API call,
  paid action, raw response/reasoning/prompt/candidate/traceback/account/
  balance material, PostgreSQL, Docker, API/Web/browser runtime, L5 smoke,
  public contract, migration or dependency action was used.

## Code and contract trace

`DeterministicPipelineCoordinator.generate` performs the fixed preflight, then
constructs five ordered requests. Each stage receives the previously parsed
and validated candidate as `upstream_candidate`; a stage exception stops the
loop before later calls. The DeepSeek adapter then:

1. resolves one catalog entry by the exact `ModelExecutionProfile`;
2. serializes the system instruction (including the project schema) and the
   deterministic context;
3. calls synchronous Chat Completions once with `max_retries=0`, using
   `response_format={"type":"json_object"}`, `extra_body={"thinking":{"type":"enabled"}}`,
   `reasoning_effort="high"`, `stream=False`, and the profile `max_tokens`;
4. applies the post-return application deadline fence before mapping;
5. maps one assistant Chat Completion, requiring `object=chat.completion`, one
   choice, assistant role, no refusal/tool call, `finish_reason=stop`, and
   non-empty JSON object content; and
6. sends the mapped result through duplicate/non-finite-safe JSON parsing,
   Draft 2020-12 project-schema validation, then the Fast Lane domain gate.

The current five request/profile/schema tuples are:

| Stage | Call id | Execution profile | Output schema | `max_tokens` | Timeout | Effort |
| --- | --- | --- | --- | ---: | ---: | --- |
| 1 | `deterministic-stage-1` | `product_intake_v1/v1` | `product_intake_fact_candidate/v1` | 8,192 | 120 s | `high` |
| 2 | `deterministic-stage-2` | `customer_insight_v1/v1` | `customer_insight_candidate/v1` | 12,288 | 180 s | `high` |
| 3 | `deterministic-stage-3` | `product_positioning_v1/v1` | `product_positioning_candidate/v1` | 16,384 | 240 s | `high` |
| 4 | `deterministic-stage-4` | `marketing_brief_v1/v1` | `marketing_brief_candidate/v1` | 16,384 | 180 s | `high` |
| 5 | `deterministic-stage-5` | `xiaohongshu_mapping_v1/v2` | `xiaohongshu_brief_candidate/v1` | 16,384 | 240 s | `high` |

The mapper records a readable provider-neutral Version Tuple (`deepseek`,
`chat_completions`, SDK version, configured/resolved model, prompt/schema/
skill/domain/context versions and the profile tuple) and usage/latency only.
Provider objects are not retained. The Fast Lane admission allows the fixed
stage decisions and, at stage 5, requires Marketing Brief mandatory/prohibited
messages and evidence limitations to remain represented in the Xiaohongshu
mapping.

## Offline evidence

The retained synthetic probe uses the fictional Anchor SKU only and an in-process
`httpx.MockTransport`; it does not start PostgreSQL, FastAPI or a browser and
does not make a networked Provider request. It holds the sanitized usage and
latency signature at `2353 / 8192 / 10545`, `106434 ms`, one stage-1 call and
zero retries while exercising six representative branches. The same signature
maps to multiple real runtime categories (`INCOMPLETE_OUTPUT`,
`INVALID_CANDIDATE`, and `TRANSIENT_PROVIDER_FAILURE`) across finish-length,
empty-content, malformed JSON, non-success finish, project-schema and domain
admission cases. This confirms ambiguity; it does not identify the historical
response or cause.

The existing offline diagnosis therefore remains the accepted
`INSUFFICIENT_SANITIZED_EVIDENCE` result. No duplicate RED was manufactured and
no production behavior was changed.

## Current first-party DeepSeek contract (read-only recheck)

Checked 2026-08-28 from the official `api-docs.deepseek.com` domain only:

| Contract point | First-party observation | Qualification |
| --- | --- | --- |
| Base and model | Quick Start lists OpenAI base `https://api.deepseek.com` and model `deepseek-v4-pro`; the Chat Completions reference accepts that model. | Matches frozen contract. |
| Chat Completions | The API reference documents `POST /chat/completions`, synchronous non-stream responses, and `stream=false`. | Matches frozen API family/operation. |
| JSON Output | JSON Output requires `response_format={"type":"json_object"}` and instructing the model to produce JSON. | Matches request preparation. |
| Thinking and effort | Thinking Mode documents `extra_body={"thinking":{"type":"enabled"}}` for the OpenAI SDK and `reasoning_effort="high"`; the API reference lists `high` as valid. | Matches enabled thinking/high effort. |
| `max_tokens` / truncation | The reference defines `max_tokens`; JSON Output guidance says to set a reasonable limit. `finish_reason="length"` can indicate the generation exceeded `max_tokens` or context length and content may be cut off. | Supports the existing mapper and diagnostic lead; does not prove historical cause. |
| Empty content | JSON Output guidance says the API may occasionally return empty `content`. | Supports the existing incomplete-output branch; does not prove historical cause. |

Sources: [Quick Start](https://api-docs.deepseek.com/), [Chat Completions
API](https://api-docs.deepseek.com/api/create-chat-completion/), [JSON
Output](https://api-docs.deepseek.com/guides/json_mode/), [Thinking
Mode](https://api-docs.deepseek.com/guides/thinking_mode/), and [Models &
Pricing](https://api-docs.deepseek.com/quick_start/pricing/).

The current pages also describe additional model capabilities (including a
Responses API). That is additive documentation, not a conflict: the required
`deepseek-v4-pro` Chat Completions JSON-mode path remains documented and this
Stage does not migrate the accepted API family.

## Validation record

All commands were run offline against the fresh clone and used synthetic or
fictional fixtures only:

| Check | Result |
| --- | --- |
| Retained diagnosis: `test_fl2_deepseek_offline_diagnosis.py` | `1 passed` |
| Focused diagnosis + DeepSeek runtime/mapper + pipeline/schema tests | `207 passed in 1.40s` |
| DeepSeek/pipeline/output contract and schema suite | `946 passed in 17.13s` |
| Provider-boundary/structured-output architecture contracts | `9 passed in 0.30s` |
| Ruff format check (12 affected source/test files) | pass |
| Ruff lint check (same relevant paths) | pass |
| Canonical backend Pyright | `0 errors, 0 warnings, 0 informations` |

No Python production path was changed; CI remains responsible for global
regression checks.

## Disposition and follow-up boundary

**Disposition: `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`.** The retained
official path and local validation gates are coherent, while the historical
sanitized signature cannot distinguish several current rejection boundaries.
There is no general correctness RED and therefore no Phase-B repair amendment.
The L4 review/PR still requires independent five-axis review and merge; only
after that reviewed record reaches `main` may a separately authorized L5 human
Gate consider one paid DeepSeek acceptance. No L5 call, Secret access or live
runtime is part of this delivery.
