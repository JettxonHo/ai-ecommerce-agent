# AI Ecommerce Agent

> **Status: MVP-0P Local Action Workbench Productization Goal ACTIVE · P0 COMPLETE · ISSUE #303 / PR #304 P1 SHELL MERGED AND CURRENT · ISSUE #305 / PR #306 P2 MERGED AND CURRENT · ISSUE #247 P3 IMPLEMENTATION ACTIVE (MERGE-CONDITIONAL) · P4 GATED · OLD FAST LANE TERMINAL `GOAL_BLOCKED`**
>
> The current productization authority is the [MVP-0P Local Action Workbench Productization Goal](docs/goals/mvp0-local-action-workbench-productization-goal.md), activated by [DEC-083](docs/decisions/dec-083-local-action-workbench-productization-goal.md). The [MVP-0 Fast Lane Goal](docs/goals/mvp0-fast-lane-goal.md) is preserved as a terminal `GOAL_BLOCKED` historical execution record, and the original [end-to-end MVP-0 Goal](docs/goals/end-to-end-demo-mvp0-goal.md) remains historical traceability.

## Product

AI Ecommerce Agent is a local, fixed-workspace product-launch strategy workbench for small ecommerce operators. It turns user-provided product information into:

- grounded product facts;
- customer insight;
- product positioning;
- a platform-neutral Marketing Brief;
- a Xiaohongshu Brief;
- a Markdown export reviewed by the user.

The core is platform-neutral. Xiaohongshu is the first demonstration adapter. The main workflow is deterministic; constrained model calls perform semantic analysis, and one human review remains the final decision point.

[DEC-082](docs/decisions/dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md) fixes the local single-user Action Workbench direction. [DEC-083](docs/decisions/dec-083-local-action-workbench-productization-goal.md) sequences its productization as P0 → P1 → P2 → P3 → P4 → P5. Issue #303 / [PR #304](https://github.com/JettxonHo/ai-ecommerce-agent/pull/304) carries the bounded P1 shell and is merged/current. Issue #305 / [PR #306](https://github.com/JettxonHo/ai-ecommerce-agent/pull/306) carries the P2 Running, Review and Results implementation and is merged/current. Reconciled [Issue #247](https://github.com/JettxonHo/ai-ecommerce-agent/issues/247) carries the P3 Needs Input and bounded Recovery implementation; P3 is repository-current only in a checkout containing its eventual merge commit. `/tasks` is the action home rather than a dashboard; a stable Task opens one Chinese five-stage progress rail, one Active Workspace and a collapsible `320–360px` Context Rail. Review is structured, Results are action-oriented with separate Marketing / Xiaohongshu views, and raw JSON stays behind technical details. The human A+C verdict is `HUMAN_SELECTED_AC_BASELINE` only: PR #299 remains open / unmerged.

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
- a private Needs Input gateway with generated-client and deterministic adapters, plus bounded Needs Input and Recovery workspaces;
- a real-backend Chromium path covering sufficient and insufficient input, review, download and reload persistence.

The deterministic browser-to-backend loop is implemented and locally verifiable as the accepted foundation input; it is not live Provider acceptance. The P3 Needs Input UI and adapters are frontend/deterministic evidence only: the current FastAPI task resource still projects `needsInputRequest: null` and does not implement the Needs Input read/resolve operations, so no real browser-to-FastAPI Needs Input completion is claimed. The one-command release path is `scripts/mvp0/demo`; it starts the fixed PostgreSQL service, applies the Business Alembic head, runs the API and Vite Web process on loopback, and keeps those host processes in the foreground. [PR #271](https://github.com/JettxonHo/ai-ecommerce-agent/pull/271) implements the private direct DeepSeek `deepseek-v4-pro` runtime and opt-in smoke seam required by [DEC-079](docs/decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md), and [PR #280](https://github.com/JettxonHo/ai-ecommerce-agent/pull/280) merged the DEC-080 Xiaohongshu v2 deadline-fence repair offline. The historical first smoke completed five calls and failed before `awaiting_review`; the second under [Issue #281](https://github.com/JettxonHo/ai-ecommerce-agent/issues/281) stopped after one `product_intake_v1 / v1` call with fixed safe HTTP 500 before `awaiting_review`. Neither is Provider acceptance; both authorizations are consumed and no further run is authorized. [DEC-081](docs/decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) Phase A ended with `INSUFFICIENT_SANITIZED_EVIDENCE` and observational ambiguity across mapper/schema/domain-admission boundaries only. No production repair or Phase B contract exists, and `rejection_disposition` remains a Proposal only. The OpenAI/Qwen provider-specific legacy adapters, direct tests and live handoffs are removed; `openai==2.53.0` remains because DeepSeek consumes it.

Advanced retrieval, distributed recovery and other deferred capabilities remain intentionally out of this release slice.

## Productization stages

The successor Goal is serial and bounded:

1. **P0 — Goal activation and current-truth reconciliation:** this docs-only Issue; exactly eight allowlisted files, no code or live action.
2. **P1 — Action Home and A+C production shell:** Chinese-first `/tasks`, Task identity/header, horizontal five-stage rail, Active Workspace and Context Rail; Issue #303 / [PR #304](https://github.com/JettxonHo/ai-ecommerce-agent/pull/304) is merged/current, preserving current generated client/gateway/data behavior without backend/public-contract changes.
3. **P2 — Core TaskWorkbench states:** Running, Review and Results with structured Marketing / Xiaohongshu views, safe Markdown preview/export and progressive technical disclosure; Issue #305 / [PR #306](https://github.com/JettxonHo/ai-ecommerce-agent/pull/306) is merged/current.
4. **P3 — Needs Input and essential recovery:** reconciled [Issue #247](https://github.com/JettxonHo/ai-ecommerce-agent/issues/247) delivers the private gateway, Chinese-first bounded actions and Recovery workspace; repository-current status is conditional on the eventual Issue #247 merge commit. The current FastAPI Needs Input read/resolve resource remains unimplemented, and no real-backend completion is claimed.
5. **P4 — Deterministic local release acceptance:** fictional-data browser → FastAPI → PostgreSQL path, one-command demo, exports and representative recovery; no live Provider/platform call.
6. **P5 — Spider_XHS feasibility Gate:** docs/research only first; exact upstream, license/commercial permission, platform risk, Cookie/Secret, dependencies/security and read-only seam. No reuse, code copy, clone, install, Cookie/login, proxy, signature, platform request, scraping or publishing without a positive Gate.

P0 is complete. Issue #303 / PR #304 and Issue #305 / PR #306 are merged/current P1 and P2 deliveries. Issue #247 is the reconciled P3 implementation record; this checkout is repository-current for P3 only once its eventual merge commit is present and independently reviewed. P4 remains gated on independent P3 review/merge and retains the provider-free deterministic release boundary. Open Dependabot work and unrelated old Issues remain outside this staged path.

## Deferred from this Goal

- JSON / CSV / PDF / image / OCR intake;
- semantic or hybrid retrieval and the full EvidencePackage lifecycle;
- distributed Worker lease/fencing and complete checkpoint recovery;
- partial rerun, full cancellation/recovery matrices and Source replace/remove UX;
- review autosave/diff, multiple outcomes and Brief comparison;
- unused public operations, login, RBAC, multi-tenancy and public deployment;
- multi-agent runtime, multi-provider routing, automatic publishing and generic compliance or telemetry platforms.

Existing code for deferred capabilities is preserved but frozen unless a productization Stage directly needs it.

## Security and quality

Required protections remain: external-input limits, fixed-workspace scope, parameterized SQL, atomic current-result persistence, React/Markdown safety, loopback same-origin transport, mutation idempotency, Secret/provider-payload isolation and safe errors.

Productization does not add a new AST scanner, exact private-directory inventory, exhaustive every-field mutation matrix, login/RBAC or public-internet threat model for each module. Tests cover representative behavior and real boundaries in accordance with [DEC-039](docs/decisions/dec-039-proportional-validation-and-review-governance.md) and the concise [Testing Strategy](docs/development/testing-strategy.md).

## Execution entry points

Read in this order:

1. [AGENTS.md](AGENTS.md)
2. [DEC-083](docs/decisions/dec-083-local-action-workbench-productization-goal.md)
3. [MVP-0P Local Action Workbench Productization Goal](docs/goals/mvp0-local-action-workbench-productization-goal.md)
4. [Implementation Readiness](docs/handoffs/implementation-readiness.md)
5. [DEC-081](docs/decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) for historical terminal diagnosis boundaries
6. [MVP-0 Fast Lane Goal](docs/goals/mvp0-fast-lane-goal.md) as preserved terminal history
7. the current Issue and the actual code/tests it changes

For an important frontend design or implementation slice, also read [DEC-082](docs/decisions/dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md). Applicable taste skills are mandatory for important design work. A user-accepted exact frontend contract may explicitly route work to local Kimi Code + Kimi K3; that narrow exception is not a Luna / Terra fallback, does not extend to backend or Provider boundaries, keeps requested configuration evidence separate from runtime identity, and still requires independent Sol review.

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
- Local Kimi Code + Kimi K3 may handle only an explicitly contracted frontend design / implementation slice under DEC-082. Kimi does not self-approve or merge, and Issue #291 authorizes no model call.
- Completed sub-agents are closed promptly unless an immediate bounded follow-up is required.
- One Issue must deliver one observable vertical outcome; speculative contract-only work is not accepted.
- Destructive migrations, public deployment, real user data, Provider Secrets and paid live calls remain human gates.
- DEC-081 Phase A is complete with terminal `INSUFFICIENT_SANITIZED_EVIDENCE`; it established observational ambiguity only, made no production repair and created no Phase B contract. `rejection_disposition` remains a Proposal only, and no future Provider call inherits authorization from either phase.
- P0 is docs-only and makes no Kimi, Terra, Provider or model call; the local full-access grant does not override independent Review, Secret/provider/platform, destructive-action, public-contract/migration or exact implementation-agent gates.
- Spider_XHS is a conditional P5 feasibility candidate only; no code reuse, clone, install, Cookie/login, proxy, signature, platform request, scraping or publishing is authorized before a positive feasibility Gate.

See [Decision Log](docs/decisions/decision-log.md) for historical traceability. Current execution is governed by [DEC-083](docs/decisions/dec-083-local-action-workbench-productization-goal.md) and the staged Goal; [DEC-078](docs/decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md), DEC-079 and [DEC-081](docs/decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) remain historical / boundary authority for the terminal Fast Lane record.
