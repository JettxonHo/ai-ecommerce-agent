# AI Ecommerce Agent

> **Status: predecessor `MVP0P_GOAL_COMPLETE` is historical merge-effective truth · successor [MVP-0L Local AI Web App Delivery Goal](docs/goals/mvp0-local-ai-web-app-delivery-goal.md) is `ACTIVE` after L0 PR #317 reached `main` · L1 Issue #318 is merged/current through PR #328 with independent review `PASS` and provider-free runtime acceptance · L2 Issue #329 / PR #330 is merged/current at exact base `dbccacacc54cb21c393987a8612dfc6aa825093b`, with provider-free runtime `PASS`, independent five-axis `PASS` and fresh Required Checks `12/12`; Issue #329 is closed · L3 Issue #331 has offline GREEN and a completed second provider-free runtime `PASS` after a first build-only `HOLD` on the unpublished `uv==0.12.8`; independent review and merge remain pending · historical Fast Lane terminal `GOAL_BLOCKED` · `P5_REUSE_FROZEN` preserved**
>
> The current L0 activation authority is [DEC-084](docs/decisions/dec-084-apple-silicon-local-ai-web-app-goal.md), [Session-009](docs/sessions/session-009-local-ai-web-app-goal-activation.md) and the successor Goal. The completed [MVP-0P Local Action Workbench Productization Goal](docs/goals/mvp0-local-action-workbench-productization-goal.md) is its historical predecessor. The [MVP-0 Fast Lane Goal](docs/goals/mvp0-fast-lane-goal.md) remains a terminal `GOAL_BLOCKED` historical execution record, and the original [end-to-end MVP-0 Goal](docs/goals/end-to-end-demo-mvp0-goal.md) remains historical traceability.

## Product

AI Ecommerce Agent is a local, fixed-workspace product-launch strategy workbench for small ecommerce operators. It turns user-provided product information into:

- grounded product facts;
- customer insight;
- product positioning;
- a platform-neutral Marketing Brief;
- a Xiaohongshu Brief;
- a Markdown export reviewed by the user.

The core is platform-neutral. Xiaohongshu is the first demonstration adapter. The main workflow is deterministic; constrained model calls perform semantic analysis, and one human review remains the final decision point.

[DEC-082](docs/decisions/dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md) and [DEC-083](docs/decisions/dec-083-local-action-workbench-productization-goal.md) describe the completed local Action Workbench predecessor: `/tasks`, the Chinese five-stage rail, Active Workspace, Context Rail, structured Review and separate Marketing / Xiaohongshu Results. Its final review merged in PR #315, making `MVP0P_GOAL_COMPLETE` historical current truth. The successor [DEC-084](docs/decisions/dec-084-apple-silicon-local-ai-web-app-goal.md) and [DEC-085](docs/decisions/dec-085-docker-only-local-web-lifecycle.md) freeze the next order as L0 → L1 → L2 → L3 → L4 → L5 → L6; L0 is merged/current through PR #317, L1 through PR #328, and L2 is merged/current through PR #330 at exact base `dbccacacc54cb21c393987a8612dfc6aa825093b` with Issue #329 closed. Issue #331 is the active L3 implementation Stage; its first provider-free runtime is historical `HOLD` at image build only on unpublished `uv==0.12.8`, and its single corrected-pin runtime passed health, browser and cleanup; independent review and merge remain pending. The human A+C verdict remains `HUMAN_SELECTED_AC_BASELINE` only; PR #299 remains open / unmerged.

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
- the Issue #318 PostgreSQL-backed Needs Input read/resolve boundary, current-request projection and bounded recovery reconciliation, consumed by the existing Web Workbench without OpenAPI/generated-client changes;
- a real-backend Chromium harness covering sufficient and insufficient input, review, download and reload persistence; the Issue #318 one-time run passed the four real-backend cases with exact ephemeral cleanup;
- the Issue #329 L2 characterization proving Task primary input, generated/confirmed Marketing and Xiaohongshu results, and both immutable Markdown export snapshots across recomposition/replay and a materially newer fictional input.

The deterministic browser-to-backend loop remains provider-free evidence, not live Provider acceptance. Issue #318 closes the real FastAPI gap: a durable Task-owned request is projected from insufficient persisted input, read/resolve operations enforce ownership/revision/idempotency, newer insufficient results supersede prior requests, and a sufficient save/generate clears the current reference after recomposition. PR #328 makes L1 merge-effective with its exact provider-free 6/6 backend and 4/4 browser acceptance and independent five-axis `PASS`. Issue #329 records the bounded L2 persistence characterization from reviewed `main` at exact base `dbccacacc54cb21c393987a8612dfc6aa825093b`: after the v2 input revision advances, stale generate and confirmation replays return `409` before and after recomposition without mutating current truth; the single follow-up runtime passed all 6 tests in `1.41s`, fresh Required Checks are `12/12`, and PR #330 is merged/current with Issue #329 closed. Issue #331 records the next bounded Docker-only local Web lifecycle; the ORCHESTRATOR_REVIEWER bounded repair/runtime ruling under the owner's standing serial-order instruction records a first provider-free runtime `HOLD` at image build only (Web built, API failed on unpublished `uv==0.12.8`; guarded cleanup passed without service, health, browser or product-behavior evidence), then tests-first `uv==0.12.6` repair produced one new provider-free runtime `PASS` (both images built, PostgreSQL/API/Web healthy, browser after health, bounded `/tasks` read, Ctrl-C 130 and exact cleanup). Independent review and merge remain pending. The new evidence does not change production behavior or public contracts. The predecessor's P4B fictional-data rehearsal and exact cleanup remain `P4_LOCAL_RELEASE_ACCEPTED`; P5 docs/research remains independently reviewed as `P5_REUSE_FROZEN`, with direct Spider_XHS reuse and platform behavior frozen and unauthorized. The predecessor final review merged in PR #315, making `MVP0P_GOAL_COMPLETE` historical current truth. L0 is merged/current through PR #317 and the successor Goal is `ACTIVE`. The eventual real-AI contract is official DeepSeek `deepseek-v4-pro`; no Provider/model call or Secret access is part of Issue #331. Ordinary Git/GitHub branch, push, PR and CI transport is documentation workflow transport, not product-runtime activity. The later project-root Git-ignored `.env` containing `DEEPSEEK_API_KEY` is an accepted Secret convention; no Stage may create/read/inspect it. The historical first smoke completed five calls and failed before `awaiting_review`; the second under [Issue #281](https://github.com/JettxonHo/ai-ecommerce-agent/issues/281) stopped after one `product_intake_v1 / v1` call with fixed safe HTTP 500 before `awaiting_review`. Neither is Provider acceptance; both authorizations are consumed and no further run is authorized. [DEC-081](docs/decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) Phase A ended with `INSUFFICIENT_SANITIZED_EVIDENCE` and observational ambiguity across mapper/schema/domain-admission boundaries only. No production repair or Phase B contract exists, and `rejection_disposition` remains a Proposal only.

Advanced retrieval, distributed recovery and other deferred capabilities remain intentionally out of this release slice.

## Delivery stages

The completed predecessor P0 → P1 → P2 → P3 → P4 → P5 chain is historical evidence. The successor Goal freezes the next serial order as **L0 → L1 → L2 → L3 → L4 → L5 → L6**:

1. **L0 — Governance activation:** completed and merged through PR #317; its historical docs-only boundary remains unchanged.
2. **L1 — Real Needs Input backend:** Issue #318 implements the real FastAPI read/resolve boundary and bounded Recovery with one additive Task-owned table, existing Web consumer and provider-free runtime acceptance; PR #328 is merged/current after independent five-axis review `PASS`.
3. **L2 — Minimum Source/Brief persistence:** Issue #329 / PR #330 was exactly one bounded persistence acceptance/reconciliation delivery, not an umbrella or child-Issue implementation batch. From reviewed `main` at exact base `dbccacacc54cb21c393987a8612dfc6aa825093b`, its provider-free characterization proves Task primary input, current generated and confirmed Marketing/Xiaohongshu results, immutable export snapshots and protected stale revision/idempotency rejections across recomposition/replay and a materially newer fictional input; the single follow-up runtime passed `6/6` in `1.41s`, independent five-axis review is `PASS`, fresh Required Checks are `12/12`, PR #330 is merged/current and Issue #329 is closed. Residual unconsumed #81/#82 scope is Deferred; do not close or mutate either parent, create child implementation Issues or revive the full Source/Review platform without a concrete later consumer and a new explicit contract. Review Draft autosave, diff and stale-draft recovery remain Deferred; no production repair, migration, public-contract change or dependency/lockfile authorization was made.
4. **L3 — Local Web lifecycle:** Issue #331 supplies the Apple Silicon + user-installed Docker Desktop one-command lifecycle, bounded preflight/health/stop, private API, loopback Web and system-default-browser ordering. Its offline evidence and one provider-free runtime `PASS` (after the historical first-attempt `HOLD` and corrected pin) are recorded on the implementation branch; independent review and merge remain pending. Native App/WebView, signing and notarization are Deferred; Intel support is Deferred; excluded from the first release.
5. **L4 — DeepSeek offline diagnosis/repair:** preserve official DeepSeek `deepseek-v4-pro` and the local `.env` boundary; no paid/live call.
6. **L5 — Real DeepSeek acceptance:** one separately reviewed exact-commit paid acceptance after L4; no prior authorization carries forward.
7. **L6 — Clean-Mac acceptance and final Goal Review:** another clean Apple Silicon Mac, then an independent completion decision.

Only one successor Stage may be active at a time; the next Issue waits for the prior independently reviewed PR to reach `main`. Native App/WebView/signing/notarization, login/RBAC/multi-user/public deployment, Keychain/Secret UI, real data and Spider_XHS behavior are Deferred or Out of Scope; Intel support is Deferred; excluded from the first release.

## Deferred from this Goal

- JSON / CSV / PDF / image / OCR intake;
- semantic or hybrid retrieval and the full EvidencePackage lifecycle;
- distributed Worker lease/fencing and complete checkpoint recovery;
- partial rerun, full cancellation/recovery matrices and Source replace/remove UX;
- Review Draft autosave/diff/stale-draft recovery, multiple outcomes and Brief comparison;
- unused public operations, login, RBAC, multi-tenancy and public deployment;
- multi-agent runtime, multi-provider routing, automatic publishing and generic compliance or telemetry platforms.

Existing code for deferred capabilities is preserved but frozen unless a productization Stage directly needs it.

## Security and quality

Required protections remain: external-input limits, fixed-workspace scope, parameterized SQL, atomic current-result persistence, React/Markdown safety, loopback same-origin transport, mutation idempotency, Secret/provider-payload isolation and safe errors.

Productization does not add a new AST scanner, exact private-directory inventory, exhaustive every-field mutation matrix, login/RBAC or public-internet threat model for each module. Tests cover representative behavior and real boundaries in accordance with [DEC-039](docs/decisions/dec-039-proportional-validation-and-review-governance.md) and the concise [Testing Strategy](docs/development/testing-strategy.md).

## Execution entry points

Read in this order for the active L2 implementation/review:

1. [AGENTS.md](AGENTS.md)
2. [DEC-084](docs/decisions/dec-084-apple-silicon-local-ai-web-app-goal.md)
3. [MVP-0L Local AI Web App Delivery Goal](docs/goals/mvp0-local-ai-web-app-delivery-goal.md)
4. [Session-009](docs/sessions/session-009-local-ai-web-app-goal-activation.md)
5. [Implementation Readiness](docs/handoffs/implementation-readiness.md)
6. [MVP-0P Local Action Workbench Productization Goal](docs/goals/mvp0-local-action-workbench-productization-goal.md) as historical predecessor
7. [MVP-0 Fast Lane Goal](docs/goals/mvp0-fast-lane-goal.md) and [DEC-081](docs/decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) for preserved terminal boundaries
8. the current Issue and the actual code/tests it changes

For an important frontend design or implementation slice, also read [DEC-082](docs/decisions/dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md). Applicable taste skills are mandatory for important design work. A user-accepted exact frontend contract may explicitly route work to local Kimi Code + Kimi K3; that narrow exception is not a Luna / Terra fallback, does not extend to backend or Provider boundaries, keeps requested configuration evidence separate from runtime identity, and still requires independent Sol review.

Historical RFCs and Decisions are consulted only when the current vertical changes their public or irreversible boundary.

## Local development

The completed predecessor's local foundation is documented in [apps/backend/README.md](apps/backend/README.md) and [apps/web/README.md](apps/web/README.md). L0 was documentation-only and is merged/current. Issue #318's one-time provider-free local runtime acceptance used the existing Apple Silicon + user-installed Docker Desktop lifecycle and passed backend 6/6 plus browser 4/4; PR #328 makes L1 merge-effective with independent five-axis review `PASS`. Issue #329 / PR #330's one-time provider-free L2 runtime acceptance passed the six-test backend characterization in `1.41s` on an isolated ephemeral scope from exact base `dbccacacc54cb21c393987a8612dfc6aa825093b`; the blocking stale revision/idempotency finding was resolved test-only, independent five-axis review is `PASS`, fresh Required Checks are `12/12`, PR #330 is merged/current and Issue #329 is closed. Issue #331's Docker-only local Web lifecycle has offline RED→GREEN, rendered-Compose evidence and one provider-free runtime `PASS` on its isolated branch; the first attempt remains historical `HOLD` and the corrected-pin attempt is complete, while independent five-axis review and merge remain pending. No Provider/model call, Agent UI production work or Secret access was made. The L3 entry is [AI Ecommerce Agent.command](AI%20Ecommerce%20Agent.command), with details in [DEC-085](docs/decisions/dec-085-docker-only-local-web-lifecycle.md) and the [L3 review](docs/reviews/mvp0l-l3-docker-local-web-lifecycle.md). The later L5 contract will separately govern one paid DeepSeek acceptance; no live call is authorized here.

The accepted later Secret convention is a project-root Git-ignored `.env` containing `DEEPSEEK_API_KEY`. Do not create, read, inspect, print, measure or hash that file or value during L0. Native App/WebView, signing/notarization, login/RBAC/multi-user/public deployment and Keychain/Secret UI remain Deferred. Intel support is Deferred; excluded from the first release.

## Governance

- The user accepts product/architecture Decisions, Goal activation and high-risk changes.
- Sol orchestrates and independently reviews.
- The exact custom `luna-worker` implements code Issues; it is not silently replaced by Terra.
- Local Kimi Code + Kimi K3 may handle only an explicitly contracted frontend design / implementation slice under DEC-082. Kimi does not self-approve or merge, and Issue #291 authorizes no model call.
- Completed sub-agents are closed promptly unless an immediate bounded follow-up is required.
- One Issue must deliver one observable vertical outcome; speculative contract-only work is not accepted.
- Destructive migrations, public deployment, real user data, Provider Secrets and paid live calls remain human gates.
- DEC-081 Phase A is complete with terminal `INSUFFICIENT_SANITIZED_EVIDENCE`; it established observational ambiguity only, made no production repair and created no Phase B contract. `rejection_disposition` remains a Proposal only, and no future Provider call inherits authorization from either phase.
- L0 was docs-only and makes no Kimi, Terra, Provider or model call; Issue #318 is provider-free, its independent five-axis review is `PASS`, and PR #328 makes L1 merge-effective. Issue #329 / PR #330 is provider-free and records the one-time L2 runtime `PASS`, independent five-axis `PASS` and fresh Required Checks `12/12` from exact base `dbccacacc54cb21c393987a8612dfc6aa825093b`; PR #330 is merged/current and Issue #329 is closed. Issue #331 is now the active bounded L3 Docker-only lifecycle with offline GREEN and one provider-free runtime `PASS` (first attempt `HOLD`, second corrected-pin `PASS`); independent review and merge remain pending. The local full-access grant does not override independent Review, Secret/provider/platform, destructive-action, public-contract/migration or exact implementation-agent gates.
- Spider_XHS remains frozen and unauthorized after the P5 Gate: no code reuse, clone, install, Cookie/login, proxy, signature, platform request, scraping or publishing is authorized. Any future positive permission or official path would require a separate, explicit contract outside this completed Goal.

See [Decision Log](docs/decisions/decision-log.md) for historical traceability. The merged L2 boundary is recorded by [Issue #329](https://github.com/JettxonHo/ai-ecommerce-agent/issues/329), PR #330 and exact base `dbccacacc54cb21c393987a8612dfc6aa825093b`; the active L3 implementation/review is governed by [Issue #331](https://github.com/JettxonHo/ai-ecommerce-agent/issues/331) and [DEC-085](docs/decisions/dec-085-docker-only-local-web-lifecycle.md). The merged L1 boundary remains recorded in [Issue #318](https://github.com/JettxonHo/ai-ecommerce-agent/issues/318). L0 activation remains historical authority through [DEC-084](docs/decisions/dec-084-apple-silicon-local-ai-web-app-goal.md), [Session-009](docs/sessions/session-009-local-ai-web-app-goal-activation.md) and the successor Goal. [DEC-083](docs/decisions/dec-083-local-action-workbench-productization-goal.md), [DEC-078](docs/decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md), DEC-079 and [DEC-081](docs/decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) remain historical / boundary authority for the completed predecessor and terminal Fast Lane record.
