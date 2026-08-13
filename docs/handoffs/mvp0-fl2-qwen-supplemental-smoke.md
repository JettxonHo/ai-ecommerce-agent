# MVP-0 FL-2S Qwen Token Plan supplemental smoke

## Status

**BLOCKED_BY_PROVIDER_TERMS — DO NOT RUN.** The Token Plan Personal terms
prohibit using the plan for an automated script or custom application backend,
which includes this pytest / FastAPI / PostgreSQL smoke. The merged adapter is
offline-only and frozen pending the post-FL-2 bounded cleanup classification.
This document does not claim a live result and does not authorize Secret
injection, a Qwen call or Token Plan consumption. Current FL-2 authority is
[DEC-079](../decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md).

## Frozen lane

- Provider label: `qwen_token_plan`
- Credential reference: `qwen_token_plan_supplemental`
- Secret environment variable: `QWEN_TOKEN_PLAN_API_KEY`
- Model: `qwen3.8-max`
- Base URL: `https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`
- Operation: synchronous OpenAI-compatible `chat.completions.create`
- SDK: official `openai.OpenAI(max_retries=0)`
- Output: strict `json_schema` response format using the project-owned schema
- Retry: one transport attempt; no nested retry, repair model, fallback model or provider router

The private adapter is not exported from
`ai_ecommerce_agent.platform.model_runtime`, is not selected by default
bootstrap, and is not reachable from public HTTP configuration. Normal tests
remain offline and use the existing deterministic runtime.

## Offline verification

The adapter tests cover the exact credential and client configuration, frozen
five-profile order, deterministic request projection, strict schema request
shape, untrusted response mapping, safe typed errors, provider-neutral metadata,
project schema validation, private package boundaries, and zero default live
I/O. The integration module is marked `live` and is skipped unless both
explicit opt-in flags are set.

## Historical operator procedure — prohibited under current terms

The following shape is retained only to explain the merged offline seam. Do not
inject the Token Plan Secret and do not execute this smoke:

```text
RUN_QWEN_SUPPLEMENTAL_SMOKE=1
MVP0_RUN_TASK_HTTP_POSTGRES=1
GIT_COMMIT=<exact reviewed commit>
FL2_QWEN_LIVE_EVIDENCE_PATH=<new, non-existing operator path>
```

Run only:

```text
uv run pytest tests/integration/test_fl2_qwen_token_plan_live_smoke.py -q
```

The adapter resolves `QWEN_TOKEN_PLAN_API_KEY` inside its private factory,
before PostgreSQL setup. The smoke creates one Task, saves
`fixture-sufficient-v1`, executes the five ordered profiles, confirms the
result, and verifies both immutable Markdown exports/download invariants.
The evidence file is append-only and contains only provider-neutral IDs,
version tuples, token usage, latency, retry count, behavior gates, commit and
timing. It must not contain the Secret, prompts, context, raw responses,
fixtures, candidates, Markdown bytes, tracebacks or account identifiers.

No Qwen live result may be recorded from Token Plan Personal. The remaining
accepted Provider proof is direct DeepSeek official API and requires its own
implementation, exact-head review and separate paid authorization.

## Frozen disposition

No live attempt is permitted, so there is no paid failure or retry path to
operate. Do not revert or delete the merged adapter opportunistically. After
FL-2 reaches a terminal result, the single bounded legacy cleanup Issue must use
real consumer and dependency evidence to classify the Qwen package and tests as
`retain`, `freeze for later` or `remove now` without weakening Secret, payload or
traceback isolation.
