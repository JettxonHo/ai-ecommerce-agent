# DEC-084：激活 Apple Silicon 本地 AI Web App Delivery Goal

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-24
- **Decision Type:** Product Delivery / Goal Governance / Local Runtime Boundary / Stage Sequencing
- **Source:** 用户在 Codex conversation/session 中明确接受 successor direction；主控 `ORCHESTRATOR_REVIEWER` 将该方向持久记录于 [Issue #316 comment](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316#issuecomment-5388616747)
- **Amends:** [DEC-083](dec-083-local-action-workbench-productization-goal.md) 的已完成 Goal 入口与 Stage 结论
- **Preserves:** [DEC-039](dec-039-proportional-validation-and-review-governance.md)、[DEC-071](dec-071-luna-worker-exclusive-implementation-routing.md)、[DEC-072](dec-072-long-running-autonomy-and-agent-identity-governance.md)、[DEC-079](dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md)、[DEC-081](dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) 与 `P5_REUSE_FROZEN`

## Context

### Facts

- [MVP-0P Local Action Workbench Productization Goal](../goals/mvp0-local-action-workbench-productization-goal.md) reached `MVP0P_GOAL_COMPLETE` when its final-review record merged in PR [#315](https://github.com/JettxonHo/ai-ecommerce-agent/pull/315), at `main@c5dc2ae9d6e56c6da35f823df838cab4518830f0`. It is now a historical predecessor, not an active execution entry.
- The predecessor preserved the Fast Lane's terminal `GOAL_BLOCKED` history: two failed DeepSeek runs, `INSUFFICIENT_SANITIZED_EVIDENCE`, observational ambiguity, no Provider acceptance, no production repair or Phase B contract, and no inherited live authorization. `P5_REUSE_FROZEN` remains the independently reviewed Spider_XHS result; no reuse or platform behavior is authorized.
- The current FastAPI task resource still projects `needsInputRequest: null` and does not implement a real Needs Input read/resolve resource. This is the L1 starting gap, not a completed capability.

### Accepted Decision

The owner explicitly accepted the following successor direction in the Codex conversation/session; the `ORCHESTRATOR_REVIEWER` durably recorded that direction in [Issue #316 comment](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316#issuecomment-5388616747):

- first release supports Apple Silicon Macs only; Intel support is Deferred; excluded from the first release;
- Docker Desktop is a user-installed prerequisite;
- the product is a local Web App opened in the system default browser;
- native macOS App/WebView, signing and notarization are Deferred;
- the eventual local product must generate real AI content through the official DeepSeek API with model `deepseek-v4-pro`;
- the later Secret convention is a project-root, Git-ignored `.env` containing `DEEPSEEK_API_KEY`, with no macOS Keychain or Secret UI;
- acceptance uses fictional or sanitized data, not real product/customer material;
- login, RBAC, multi-user behavior and public deployment are Deferred;
- one Stage maps to one Issue/PR, with the next Stage created only after the prior independently reviewed PR reaches `main`.

## Decision

### 1. Successor Goal and merge-effective status

- Accept the single successor [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md), linked to [Session-009](../sessions/session-009-local-ai-web-app-goal-activation.md), the predecessor Goal and this Decision in both directions.
- On the L0 branch, the successor Goal is `ACTIVATION_PENDING`. It becomes `ACTIVE` only when the L0 PR for Issue #316 reaches `main`; branch documentation must not claim `ACTIVE` before that merge-effective event.
- The predecessor Goal remains historical `MVP0P_GOAL_COMPLETE`. This Decision does not reopen it, rewrite its evidence, or transfer any Provider authorization.

### 2. Frozen successor Stage order

The exact serial order is **L0 → L1 → L2 → L3 → L4 → L5 → L6**. Only one Stage may be active at a time. The next Issue may be created only after the prior Stage's independently reviewed PR reaches `main`; ordinary same-Stage follow-up fixes are batched into that Stage/PR.

1. **L0 — Governance activation:** this docs-only Issue and its exact nine-file allowlist.
2. **L1 — Real Needs Input backend:** implement the real FastAPI Needs Input read/resolve boundary and bounded Recovery. The current `needsInputRequest: null` gap remains explicit until independently accepted.
3. **L2 — Minimum Source/Brief persistence:** run exactly one bounded persistence acceptance/reconciliation Issue/PR, not an umbrella or multi-child implementation batch. Task primary input, current generated and confirmed Marketing/Xiaohongshu results, and immutable export snapshots are existing implementation surfaces/evidence candidates only; L2 must independently verify from reviewed `main` that they survive accepted reload/replay paths. Residual unconsumed scope in tracking parents [#81](https://github.com/JettxonHo/ai-ecommerce-agent/issues/81) and [#82](https://github.com/JettxonHo/ai-ecommerce-agent/issues/82) remains Deferred; do not close or mutate either parent, create child implementation Issues, or revive the full Source/Review platform without a concrete later consumer and a new explicit contract. Review Draft autosave, diff and stale-draft recovery remain Deferred. If evidence contradicts the minimum persistence, stop and return the exact gap; no silent production-code repair, migration, public-contract change or child-Issue creation/widening is authorized.
4. **L3 — Local Web lifecycle:** on Apple Silicon with user-installed Docker Desktop, provide one reliable command, preflight/health/stop behavior and system-default-browser opening. Native App/WebView, signing and notarization remain Deferred; Intel support is Deferred; excluded from the first release.
5. **L4 — DeepSeek offline diagnosis/repair:** preserve the official base/model contract and the local `.env` boundary; no paid or live call is allowed in this Stage.
6. **L5 — Real DeepSeek acceptance:** after L4, run exactly one separately reviewed, exact-commit paid acceptance contract. No previous smoke authorization carries forward.
7. **L6 — Clean-Mac acceptance and final Goal Review:** validate the reviewed result on another clean Apple Silicon Mac, then independently decide Goal completion.

### 3. Local product boundary

- **In Scope:** Apple Silicon Mac, Docker Desktop installed by the user, local Web App, system default browser, fictional/sanitized inputs, the staged local lifecycle, and eventual real DeepSeek `deepseek-v4-pro` generation behind the accepted boundary.
- **Deferred:** native macOS App/WebView, signing, notarization, login, RBAC, multi-user behavior, public deployment, macOS Keychain and Secret UI. Intel support is Deferred; excluded from the first release.
- **Out of Scope:** real customer/product material, Spider_XHS reuse or platform behavior, automatic publishing, any unapproved Provider/model, and any action that widens the frozen Stage contracts.

### 4. Secret and Provider boundary

The project-root `.env` convention is accepted for a later implementation Stage only. It must be Git-ignored, contain only the operator's `DEEPSEEK_API_KEY` value locally, never enter images, builds, PostgreSQL, browser storage, logs, errors or evidence, and be checked only for presence by a later preflight. L0 must not create, read, inspect, print, hash or otherwise access `.env`, environment variables or Secret values. The L5 paid call is a separate human Gate even when the file exists.

The official DeepSeek API and `deepseek-v4-pro` remain the sole future real-AI contract. L0 performs no Provider/model call, no product-runtime, Provider/API or platform network activity, no PostgreSQL launch, and no live or platform action. Ordinary Git/GitHub branch, push, PR and CI transport is part of the docs workflow and is not product-runtime activity.

### 5. Human gates and stop conditions

Stop and request the owner for any real paid Provider call or Secret value access, new migration, destructive/broad data action, public-contract or product-direction change, expansion to Intel support (Deferred; excluded from the first release), native App/signing/login/multi-user/public deployment/real data/Spider_XHS behavior, inability to use exact `luna-worker`, or unresolved Accepted Decision conflict. No inherited live authorization exists.

## Alternatives Considered

### Native macOS App/WebView as the first release

Deferred by the owner's explicit direction. The first release remains a local Web App in the system default browser; packaging, signing and notarization are later concerns.

### Intel and Apple Silicon together

Rejected for this Goal. The first release is Apple Silicon only; Intel support is Deferred; excluded from the first release rather than an implicit compatibility promise.

### Cloud/public multi-user delivery

Deferred. Login, RBAC, multi-user behavior and public deployment are not required to activate or complete this local Goal.

### Provider call during L0

Rejected. L0 is docs-only; L4 must complete offline diagnosis/repair first, and L5 is a new exact-commit paid Gate with no inherited authorization.

## Consequences

- The repository gains one successor delivery entry with a truthful branch-pending activation state and a merge-effective `ACTIVE` transition.
- The predecessor's completed local deterministic evidence and terminal Fast Lane failure history remain auditable without being mistaken for real-AI acceptance.
- The future implementation boundaries are explicit and serial for L1 and L3–L6; L2 is a bounded acceptance/reconciliation audit rather than an implementation boundary. If its evidence audit finds a gap, any repair waits for a later explicit contract, preventing parallel or speculative Issues without a reviewed consumer.
- Apple Silicon, user-installed Docker Desktop, local browser operation and the later `.env` convention are product constraints; deferred packaging, platform and account features cannot silently enter an L Stage.

## Relationships

- **Predecessor Goal:** [MVP-0P Local Action Workbench Productization Goal](../goals/mvp0-local-action-workbench-productization-goal.md)
- **Successor Goal:** [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md)
- **Session:** [Session-009](../sessions/session-009-local-ai-web-app-goal-activation.md)
- **Activation Issue:** [Issue #316](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316)
- **Prior Decision:** [DEC-083](dec-083-local-action-workbench-productization-goal.md)

## Authorization Boundary

This Decision records the owner's explicit successor direction from the Codex conversation/session, durably recorded by the `ORCHESTRATOR_REVIEWER` in Issue #316, and authorizes only the L0 docs-only activation contract. It does not authorize code, tests, configuration, dependencies, lockfiles, migrations, OpenAPI/generated-client changes, Web implementation, Docker action, API/PostgreSQL launch, environment or Secret inspection, Provider/model/live calls, Kimi/Terra use, native App work, public deployment, or Spider_XHS action. Ordinary Git/GitHub branch, push, PR and CI transport remains allowed for this docs workflow and is not product-runtime activity. Each later Stage requires its own Issue/PR contract, independent review, and applicable human Gate.
