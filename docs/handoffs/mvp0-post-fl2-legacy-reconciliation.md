# MVP-0 Post-FL-2 Legacy Reconciliation

Status: Phase B delivered on merge; the MVP-0 Goal remains `GOAL_BLOCKED`.

This inventory records the bounded Phase B result authorized by Issue #274
after the terminal FL-2 result and the offline DEC-080 repair merge in PR #280.
It uses repository-wide import, test, handoff and dependency evidence. The
classification is not a line-count or directory-symmetry exercise.

## Remove now

| Inventory item | Consumer / dependency evidence | Removal risk and reason |
| --- | --- | --- |
| Superseded OpenAI Responses provider-specific request preparation, execution, runtime, response mapping and schema compatibility implementation | No current application or accepted next-Goal consumer; the only SDK imports in this slice were private provider files. The `openai` dependency remains required by DeepSeek, so only the provider-specific implementation is removed. | Direct provider tests and the OpenAI live-smoke handoff exercised only the superseded adapter. Removing them does not weaken the provider-neutral port, shared evidence writer or required security boundaries. |
| Superseded Qwen Token Plan private adapter implementation | No current application or accepted next-Goal consumer; its live path is blocked by provider terms. Its OpenAI SDK imports were private to the adapter and are no longer consumers after deletion. | Qwen direct tests, supplemental live smoke and provider-only guard covered an unavailable historical path. Removing them leaves the retained SDK dependency for DeepSeek and does not affect the deterministic demo. |
| OpenAI/Qwen direct provider tests, live-smoke tests and operator handoffs | Each is coupled to one of the two remove-now adapters and has no retained caller. | The smallest retained output-contract tests continue to cover project Schema/Domain behavior; DeepSeek Secret/preflight and shared evidence-writer tests remain. |

## Retain

| Inventory item | Current consumer / dependency evidence | Reason |
| --- | --- | --- |
| `openai_responses/_live_evidence.py` and the minimal package `__init__.py` | DeepSeek live controls import the shared serializer/writer by its existing path. | Preserves provider-neutral append-only, redacted evidence behavior without exporting deleted provider APIs or moving the shared helper. |
| DeepSeek adapter, project Schema/Domain admission, runtime/request/response tests and opt-in live seam | Current FL-2 provider and the only accepted real-provider path. The first run remains a safe failure before `awaiting_review`; no live acceptance is claimed. | Current code and failure evidence must remain visible. Phase B does not diagnose or change DeepSeek behavior. |
| `openai==2.53.0` | The retained DeepSeek `_response_mapping.py` and `_runtime.py` are the exact remaining SDK consumers. | Removing it would break the current provider and is outside this cleanup contract. |
| Provider-neutral `ModelRuntimePort`, scripted runtime, coordinator, local output contracts and mandatory boundary tests | Current deterministic local demo and retained application seams consume these modules. | They are part of the working vertical or protect input, scope, SQL, atomicity, Markdown, same-origin, idempotency, Secret/payload and safe-error boundaries. |
| Generic SDK-consumer architecture guard and Import Linter boundaries | The guard asserts exactly DeepSeek `_response_mapping.py` and `_runtime.py` and includes a synthetic-extra mutation proof. Import Linter continues to enforce repository direction. | Keeps the real consumer boundary without speculative directory inventories or broad AST scanning. |

## Freeze for later

Durable dispatch/lease/fencing, checkpoint recovery, advanced Source
association/processing, advanced Human Review, Retrieval/Evidence/vector/RRF,
and deferred public/history/auth/multi-tenant/deployment/telemetry contracts
remain in the repository under DEC-078's later-Gate classification. They have
no current Fast Lane consumer and are not represented as implemented MVP
functionality. This cleanup neither completes nor deletes them.

## Current truth after Phase B

- The deterministic local loop and one-command demo remain the working MVP
  boundary.
- The DEC-080 Xiaohongshu v2 deadline-fence repair is merged offline as PR #280.
- The single executed DeepSeek run at reviewed
  `main@1c7c2107ead332235d492ed063b67101784d35f1` remains a
  terminal `GOAL_BLOCKED` result; it is not live verification.
- Issue #274's bounded cleanup is delivered on merge. Issue #281 separately
  authorizes one second bounded DeepSeek v2 smoke as
  `AUTHORIZED_NOT_EXECUTED`: exactly one fictional Task, five ordered calls
  and zero retry/recovery, only after #274 Phase B is independently reviewed,
  checks pass and merges. Execution is outside #274 and requires ORCHESTRATOR exact-commit GO,
  with no further user confirmation. This reconciliation
  performs no DeepSeek/Qwen/OpenAI run, Secret action, PostgreSQL action or raw
  provider-material access. Goal remains `GOAL_BLOCKED` until a qualifying
  result and human judgment.
