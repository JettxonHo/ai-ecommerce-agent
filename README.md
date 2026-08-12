# AI Ecommerce Agent

> **Status: MVP-0 Fast Lane · ACTIVE ON DEC-078 DOCUMENTATION MERGE**
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
- a provider-neutral Model Runtime, scripted substitute and OpenAI Responses transport components;
- private output contracts for Facts, Insight, Positioning, Marketing Brief and Xiaohongshu mapping;
- Marketing / Xiaohongshu domain snapshots and a safe Markdown renderer;
- a FastAPI fixed-workspace HTTP foundation;
- authored OpenAPI, generated TypeScript client and a private Task gateway;
- React `/tasks` list, Task creation, stable deep links, Workbench projection and TaskWorkbench progress shell.

The repository does **not** yet provide a complete browser-to-backend business loop. In particular, the FastAPI application has no registered Task/input/workflow/review/export business routes, and the Skills are not connected into a production workflow.

Refresh `main` before the first Fast Lane implementation Issue; a merged UI shell does not by itself complete the backend loop.

## Fast Lane scope

The remaining MVP-0 proves one user path:

1. create a Task;
2. provide pasted text or one UTF-8 TXT / Markdown file up to 1 MiB;
3. run Facts → Insight → Positioning → Marketing Brief → Xiaohongshu Brief;
4. inspect, make a bounded correction and confirm once;
5. download the current result as Markdown;
6. run the sufficient-input path once with the real OpenAI provider after deterministic E2E passes.

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
3. [MVP-0 Fast Lane Goal](docs/goals/mvp0-fast-lane-goal.md)
4. [Implementation Readiness](docs/handoffs/implementation-readiness.md)
5. the current Issue and the actual code/tests it changes

Historical RFCs and Decisions are consulted only when the current vertical changes their public or irreversible boundary.

## Local development

Backend setup and commands: [apps/backend/README.md](apps/backend/README.md)

Web setup and commands: [apps/web/README.md](apps/web/README.md)

Local PostgreSQL lifecycle:

```bash
cp .env.example .env
./scripts/mvp0/preflight
./scripts/mvp0/up
./scripts/mvp0/verify
./scripts/mvp0/down
```

The complete Fast Lane stack command is not yet implemented. Do not describe deterministic fixture transport or the HTTP foundation as a completed real backend workflow.

## Governance

- The user accepts product/architecture Decisions, Goal activation and high-risk changes.
- Sol orchestrates and independently reviews.
- The exact custom `luna-worker` implements code Issues; it is not silently replaced by Terra.
- Completed sub-agents are closed promptly unless an immediate bounded follow-up is required.
- One Issue must deliver one observable vertical outcome; speculative contract-only work is not accepted.
- Destructive migrations, public deployment, real user data and additional paid providers remain human gates.

See [Decision Log](docs/decisions/decision-log.md) for historical traceability. Current execution is governed by DEC-078 rather than by reading all prior planning documents.
