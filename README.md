# AI Ecommerce Agent

> **Status: predecessor `MVP0P_GOAL_COMPLETE` is historical merge-effective truth · successor [MVP-0L Local AI Web App Delivery Goal](docs/goals/mvp0-local-ai-web-app-delivery-goal.md) is `ACTIVE` · L0–L3 are merged/current through PRs #317, #328, #330 and #332 at `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e` · L4 [Issue #333](https://github.com/JettxonHo/ai-ecommerce-agent/issues/333) is review-ready with `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`, production diff zero and no Phase-B amendment · L5 Phase A [Issue #335](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335) is `L5_HARNESS_REVIEW_READY`; owner authorization is pending and no live success is claimed · historical Fast Lane terminal `GOAL_BLOCKED` · `P5_REUSE_FROZEN` preserved**
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

[DEC-082](docs/decisions/dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md) and [DEC-083](docs/decisions/dec-083-local-action-workbench-productization-goal.md) describe the completed local Action Workbench predecessor. Its final review merged in PR #315, making `MVP0P_GOAL_COMPLETE` historical current truth. The successor [DEC-084](docs/decisions/dec-084-apple-silicon-local-ai-web-app-goal.md) and [DEC-085](docs/decisions/dec-085-docker-only-local-web-lifecycle.md) freeze L0 → L1 → L2 → L3 → L4 → L5 → L6; L0 is merged/current through PR #317, L1 through PR #328, L2 through PR #330, and L3 through PR #332 at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`. Issue #333 records the L4 offline qualification as `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR` with production diff zero and no Phase-B amendment. Issue #335 records the L5 Phase-A harness as `L5_HARNESS_REVIEW_READY`; owner authorization is pending and no live success is claimed. The human A+C verdict remains `HUMAN_SELECTED_AC_BASELINE` only and PR #299 remains open / unmerged.

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

The deterministic browser-to-backend loop remains provider-free evidence, not live Provider acceptance. Issue #318 closes the real FastAPI gap and PR #328 makes L1 merge-effective; Issue #329 / PR #330 records the bounded L2 persistence characterization and is merged/current. Issue #331 / PR #332 is the merged/current Docker-only local Web lifecycle at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`; its first build-only `HOLD`, tests-first pin repair, corrected-pin provider-free `PASS`, independent review and fresh checks remain recorded. Issue #333's new review records provider-free offline DeepSeek qualification: current seams and official contract are coherent, sanitized evidence is ambiguous, and no production behavior/public contract changed. Issue #335's Phase-A review records a tests-first, fail-closed export directory control as `L5_HARNESS_REVIEW_READY`; it does not claim a live run. The historical Fast Lane remains `GOAL_BLOCKED`, both old authorizations are consumed, no Provider acceptance exists, and owner authorization for L5 is pending. The predecessor final review merged in PR #315; P5 remains independently reviewed `P5_REUSE_FROZEN` and unauthorized. The eventual real-AI contract is official DeepSeek `deepseek-v4-pro`; no Secret or Provider value was accessed.

Advanced retrieval, distributed recovery and other deferred capabilities remain intentionally out of this release slice.

## Delivery stages

The completed predecessor P0 → P1 → P2 → P3 → P4 → P5 chain is historical evidence. The successor Goal freezes the next serial order as **L0 → L1 → L2 → L3 → L4 → L5 → L6**:

1. **L0 — Governance activation:** completed and merged through PR #317; its historical docs-only boundary remains unchanged.
2. **L1 — Real Needs Input backend:** Issue #318 implements the real FastAPI read/resolve boundary and bounded Recovery with one additive Task-owned table, existing Web consumer and provider-free runtime acceptance; PR #328 is merged/current after independent five-axis review `PASS`.
3. **L2 — Minimum Source/Brief persistence:** Issue #329 / PR #330 was exactly one bounded persistence acceptance/reconciliation delivery, not an umbrella or child-Issue implementation batch. From reviewed `main` at exact base `dbccacacc54cb21c393987a8612dfc6aa825093b`, its provider-free characterization proves Task primary input, current generated and confirmed Marketing/Xiaohongshu results, immutable export snapshots and protected stale revision/idempotency rejections across recomposition/replay and a materially newer fictional input; the single follow-up runtime passed `6/6` in `1.41s`, independent five-axis review is `PASS`, fresh Required Checks are `12/12`, PR #330 is merged/current and Issue #329 is closed. Residual unconsumed #81/#82 scope is Deferred; do not close or mutate either parent, create child implementation Issues or revive the full Source/Review platform without a concrete later consumer and a new explicit contract. Review Draft autosave, diff and stale-draft recovery remain Deferred; no production repair, migration, public-contract change or dependency/lockfile authorization was made.
4. **L3 — Local Web lifecycle:** Issue #331 / PR #332 is merged/current at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e` after offline RED→GREEN, the historical build-only `HOLD`, corrected-pin provider-free runtime `PASS`, independent five-axis review `PASS` at `f831519` and fresh Required Checks `12/12`. Native App/WebView, signing/notarization and Intel support remain Deferred.
5. **L4 — DeepSeek offline diagnosis/repair:** Issue #333 completed Phase A offline qualification with disposition `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`; no production repair or Phase-B amendment exists, and no paid/live call or Secret access is authorized.
6. **L5 — Real DeepSeek acceptance:** Issue #335 Phase A is `L5_HARNESS_REVIEW_READY` for export preservation; owner authorization is pending, and a future paid run remains a separately reviewed exact-commit Gate with no prior authorization carried forward.
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

Read in this order for the active L4 qualification/review:

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

The completed predecessor's local foundation is documented in [apps/backend/README.md](apps/backend/README.md) and [apps/web/README.md](apps/web/README.md). L0–L3 are merged/current through PRs #317, #328, #330 and #332 at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`; Issue #333's provider-free offline qualification is review-ready with `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`, production diff zero and no Phase-B amendment. Issue #335's Phase-A harness is review-ready as `L5_HARNESS_REVIEW_READY`, with owner authorization pending; no Provider/model call, Agent UI production work or Secret access was made. The later L5 contract will separately govern one paid DeepSeek acceptance; no live call is authorized here.

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
- L0–L3 are merged/current through PRs #317, #328, #330 and #332 at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`. Issue #333 is the review-ready L4 offline qualification with `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`, no production diff and no Phase-B amendment. Issue #335 is `L5_HARNESS_REVIEW_READY` for Phase-A export preservation; owner authorization is pending and no live success is claimed. No runtime, Provider/model call or Secret access is authorized in this Phase-A delivery. The local full-access grant does not override independent Review, Secret/provider/platform, destructive-action, public-contract/migration or exact implementation-agent gates.
- Spider_XHS remains frozen and unauthorized after the P5 Gate: no code reuse, clone, install, Cookie/login, proxy, signature, platform request, scraping or publishing is authorized. Any future positive permission or official path would require a separate, explicit contract outside this completed Goal.

See [Decision Log](docs/decisions/decision-log.md) for historical traceability. L0–L3 are merged/current through PRs #317, #328, #330 and #332 at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`. Issue #333 and the [L4 qualification review](docs/reviews/mvp0l-l4-deepseek-offline-qualification.md) record the provider-free disposition; Issue #335 and the [L5 Phase-A review](docs/reviews/mvp0l-l5-deepseek-live-acceptance.md) record `L5_HARNESS_REVIEW_READY` with authorization pending and no live success. The merged L1/L2 boundaries remain recorded in Issues #318/#329, while L3 is governed by Issue #331 and DEC-085.
