# MVP-0 FL-2S Qwen Token Plan supplemental smoke

## Status

Implementation handoff for the opt-in supplemental adapter and one live smoke
seam. This document does not claim a live result. It does not replace the
accepted OpenAI Responses provider, and it does not close Issue #255.

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

## One-run operator procedure

After an independently reviewed exact commit is available, the operator must
inject the Token Plan Secret outside source control and select a new evidence
path. The smoke must be run once:

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

Record the human-observed outcome separately as **Qwen supplemental live
verified** only after the automated gates and sanitized evidence have been
independently reviewed. OpenAI remains **live unverified** unless its own
authorized smoke has passed.

## Stop and rollback

Stop before or after a paid/ambiguous failure if the subscription, model,
endpoint, strict schema compatibility or evidence boundary is not satisfied;
do not retry without new explicit authorization. Rollback is deleting the
private adapter package, its tests, integration seam and this handoff from the
feature branch; no production/default bootstrap or database migration is
involved.
