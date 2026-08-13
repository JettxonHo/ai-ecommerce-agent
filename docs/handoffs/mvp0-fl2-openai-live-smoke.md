# MVP-0 FL-2 OpenAI live smoke

> **Status: SUPERSEDED — DO NOT RUN.** [DEC-079](../decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md) replaces the remaining OpenAI FL-2 Gate with direct DeepSeek official `deepseek-v4-pro`. This file preserves the already-merged historical seam only; it is not a current operator instruction and does not authorize `OPENAI_API_KEY` injection or an OpenAI call.

The smoke is opt-in and runs exactly one sufficient `fixture-sufficient-v1`
Task through the real FastAPI/PostgreSQL path: five Responses calls, one
bounded confirmation, and immutable Markdown exports for Marketing and
Xiaohongshu.

Historical command shape (retained for traceability; **do not execute under the current Goal**):

```sh
GIT_COMMIT="$(git rev-parse HEAD)" \
MVP0_RUN_TASK_HTTP_POSTGRES=1 \
RUN_LIVE_MODEL_SMOKE=1 \
FL2_LIVE_EVIDENCE_PATH=/tmp/ai-ecommerce-agent-fl2-live.json \
uv run pytest tests/integration/test_fl2_openai_live_smoke.py -q
```

The test never loads `.env`, prints the key, or falls back to the scripted
runtime. `RUN_LIVE_MODEL_SMOKE=1` without a nonblank key fails fast with a
fixed safe message. Without both opt-in flags the module is skipped and makes
no provider call. `FL2_LIVE_EVIDENCE_PATH` is optional; the default is a new
file under the system temporary directory. Existing evidence is never
overwritten.

The sanitized JSON evidence contains only the commit, UTC start time and
duration, PASS/FAIL disposition and human-reason placeholder, five ordered
provider-neutral call records (IDs, attempt IDs, version tuples, usage and
latency), retry/recovery counts, and the five behavior-gate booleans. It never
contains the Secret, source fixture, prompt/context, SDK response, candidate
payload, Markdown body, or traceback.
