# AI Ecommerce Agent

> **Status: MVP-0 Fast Lane · FL-1/LOCAL DEMO COMPLETE · FL-2 TERMINAL GOAL_BLOCKED · CLEANUP COMPLETE**
>
> The current execution authority is the [MVP-0 Fast Lane Goal](docs/goals/mvp0-fast-lane-goal.md). The original [end-to-end MVP-0 Goal](docs/goals/end-to-end-demo-mvp0-goal.md) remains historical traceability, not the default remaining backlog.

## Product

AI Ecommerce Agent is a local, fixed-workspace product-launch strategy workbench for small ecommerce operators. It turns user-provided product information into:

- grounded product facts;
- customer insight;
- product positioning;
- a platform-neutral Marketing Brief;
- a Xiaohongshu Brief;
- a Markdown export reviewed by the user.

The core is platform-neutral. Xiaohongshu is the first demonstration adapter. The main workflow is deterministic; constrained model calls perform semantic analysis, and one human review remains the final decision point.

## Current repository truth

The repository already contains:

- PostgreSQL, SQLAlchemy, Psycopg and Alembic foundations;
- Task / Run / Stage and Source persistence components;
- bounded Durable Dispatch and checkpoint seams;
- a provider-neutral Model Runtime, scripted substitute, the reviewed offline direct DeepSeek adapter and retained shared live-evidence seam;
- private output contracts for Facts, Insight, Positioning, Marketing Brief and Xiaohongshu mapping;
- Marketing / Xiaohongshu domain snapshots and a safe Markdown renderer;
- a FastAPI fixed-workspace HTTP foundation;
- authored OpenAPI, generated TypeScript client and a private Task gateway;
- real Task/input/result/review/export routes backed by PostgreSQL;
- a deterministic five-stage scripted pipeline and safe Markdown exports;
- React `/tasks` list, Task creation, stable deep links, Workbench projection and TaskWorkbench review/results UI;
- a real-backend Chromium path covering sufficient and insufficient input, review, download and reload persistence.

The deterministic browser-to-backend loop is implemented and locally verifiable. The one-command release path is `scripts/mvp0/demo`; it starts the fixed PostgreSQL service, applies the Business Alembic head, runs the API and Vite Web process on loopback, and keeps those host processes in the foreground. [PR #271](https://github.com/JettxonHo/ai-ecommerce-agent/pull/271) implements the private direct DeepSeek `deepseek-v4-pro` runtime and opt-in smoke seam required by [DEC-079](docs/decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md), and [PR #280](https://github.com/JettxonHo/ai-ecommerce-agent/pull/280) merged the DEC-080 Xiaohongshu v2 deadline-fence repair offline. The historical first smoke at `main@1c7c2107ead332235d492ed063b67101784d35f1` completed five calls with zero retry/recovery and failed before `awaiting_review`. The second smoke under [Issue #281](https://github.com/JettxonHo/ai-ecommerce-agent/issues/281) ran at exact `main@ac4edfed6e8e216e9938affdc734298c8630d2de` and stopped after one `product_intake_v1 / v1` call with a fixed safe HTTP 500 before `awaiting_review`; retry/recovery remained 0/0 and all behavior gates were false. Its 8,192 output tokens equal the accepted first-stage ceiling and its 106,434 ms latency is below 120 s, but the equality is only a diagnostic lead because sanitized evidence excludes finish reason, raw response and internal error category. No OpenAI, Qwen or DeepSeek live acceptance is claimed. FL-2 remains terminal `GOAL_BLOCKED`; the bounded cleanup in [Issue #274](https://github.com/JettxonHo/ai-ecommerce-agent/issues/274) is complete, #281 authorization is consumed and closed, and no further Provider run is authorized. The OpenAI/Qwen provider-specific legacy adapters, direct tests and live handoffs are removed; `openai==2.53.0` remains because DeepSeek consumes it.

Advanced retrieval, distributed recovery and other deferred capabilities remain intentionally out of this release slice.

## Fast Lane scope

The remaining MVP-0 proves one user path:

1. create a Task;
2. provide pasted text or one UTF-8 TXT / Markdown file up to 1 MiB;
3. run Facts → Insight → Positioning → Marketing Brief → Xiaohongshu Brief;
4. inspect, make a bounded correction and confirm once;
5. download the current result as Markdown;
6. preserve the two terminal direct DeepSeek failure records without claiming live success; any repair, Provider run or product-direction change requires a new user Decision and separate contract.

The first implementation uses no more than three vertical Issues: input/backend routes, pipeline/current results, and review/export.

## Deferred from this Goal

- JSON / CSV / PDF / image / OCR intake;
- semantic or hybrid retrieval and the full EvidencePackage lifecycle;
- distributed Worker lease/fencing and complete checkpoint recovery;
- partial rerun, full cancellation/recovery matrices and Source replace/remove UX;
- review autosave/diff, multiple outcomes and Brief comparison;
- unused public operations, login, RBAC, multi-tenancy and public deployment;
- multi-agent runtime, multi-provider routing, automatic publishing and generic compliance or telemetry platforms.

Existing code for deferred capabilities is preserved but frozen unless the Fast Lane path directly needs it.

## Security and quality

Required protections remain: external-input limits, fixed-workspace scope, parameterized SQL, atomic current-result persistence, React/Markdown safety, loopback same-origin transport, mutation idempotency, Secret/provider-payload isolation and safe errors.

Fast Lane does not add a new AST scanner, exact private-directory inventory, exhaustive every-field mutation matrix, login/RBAC or public-internet threat model for each module. Tests cover representative behavior and real boundaries in accordance with [DEC-039](docs/decisions/dec-039-proportional-validation-and-review-governance.md) and the concise [Testing Strategy](docs/development/testing-strategy.md).

## Execution entry points

Read in this order:

1. [AGENTS.md](AGENTS.md)
2. [DEC-078](docs/decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md)
3. [DEC-079](docs/decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md) when work touches FL-2 or a Provider boundary
4. [MVP-0 Fast Lane Goal](docs/goals/mvp0-fast-lane-goal.md)
5. [Implementation Readiness](docs/handoffs/implementation-readiness.md)
6. the current Issue and the actual code/tests it changes

Historical RFCs and Decisions are consulted only when the current vertical changes their public or irreversible boundary.

## Local development

Backend setup and commands: [apps/backend/README.md](apps/backend/README.md)

Web setup and commands: [apps/web/README.md](apps/web/README.md)

Local PostgreSQL lifecycle:

```bash
cp .env.example .env
./scripts/mvp0/preflight --host-processes
(cd apps/backend && uv sync --locked)
(cd apps/web && npm ci)
./scripts/mvp0/demo
# open the printed URL: http://127.0.0.1:5173/tasks
# press Ctrl-C to stop only API/Web
./scripts/mvp0/down       # stop PostgreSQL; named volume is preserved
```

`./scripts/mvp0/up` and `./scripts/mvp0/verify` remain database-only lifecycle checks. `scripts/mvp0/demo` never starts a Worker or selects a live Provider runtime. JSON/CSV/PDF/image/OCR intake, retrieval, distributed Worker/checkpoint recovery, advanced Review/Diff, auth/multi-tenant/public deployment and automatic publishing remain deferred.

## Governance

- The user accepts product/architecture Decisions, Goal activation and high-risk changes.
- Sol orchestrates and independently reviews.
- The exact custom `luna-worker` implements code Issues; it is not silently replaced by Terra.
- Completed sub-agents are closed promptly unless an immediate bounded follow-up is required.
- One Issue must deliver one observable vertical outcome; speculative contract-only work is not accepted.
- Destructive migrations, public deployment, real user data, Provider Secrets and paid live calls remain human gates.

See [Decision Log](docs/decisions/decision-log.md) for historical traceability. Current execution is governed by DEC-078 plus the FL-2 Provider amendment in DEC-079 rather than by reading all prior planning documents.
