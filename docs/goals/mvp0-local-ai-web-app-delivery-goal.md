# MVP-0L Local AI Web App Delivery Goal

> **Status on this branch:** `ACTIVATION_PENDING` — becomes `ACTIVE` only when the L0 PR for [Issue #316](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316) reaches `main`.
>
> **Decision authority:** [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md) · [Session-009](../sessions/session-009-local-ai-web-app-goal-activation.md)
>
> **Predecessor:** [MVP-0P Local Action Workbench Productization Goal](mvp0-local-action-workbench-productization-goal.md), now historical `MVP0P_GOAL_COMPLETE` after final-review PR [#315](https://github.com/JettxonHo/ai-ecommerce-agent/pull/315) reached `main`.
>
> **Historical Fast Lane:** [MVP-0 Fast Lane Goal](mvp0-fast-lane-goal.md) remains terminal `GOAL_BLOCKED`; its two failed DeepSeek runs, `INSUFFICIENT_SANITIZED_EVIDENCE`, observational ambiguity, no Provider acceptance and no inherited live authorization are preserved.

## 1. Goal outcome

Deliver a real-AI local Web App for a single operator on Apple Silicon Mac. The first release runs locally with user-installed Docker Desktop and opens in the system default browser. It builds on the completed deterministic Action Workbench, then closes the explicitly staged Needs Input, persistence, lifecycle, offline DeepSeek diagnosis, paid DeepSeek acceptance and clean-Mac review gates.

The eventual real-AI contract remains the official DeepSeek API with model `deepseek-v4-pro`. L0 itself is governance-only: it performs no code, test, environment, Secret, Provider, model, product-runtime/API/platform network activity, PostgreSQL or platform action. Ordinary Git/GitHub branch, push, PR and CI transport is part of the docs workflow and is not product-runtime activity. The current FastAPI task resource still projects `needsInputRequest: null`; L1 starts from that real backend gap.

## 2. Activation and operating rule

- `MVP0P_GOAL_COMPLETE` is the merge-effective historical status of the predecessor and is not reopened.
- This successor is `ACTIVATION_PENDING` on the L0 branch and becomes `ACTIVE` only when the L0 PR reaches `main`.
- Only one Stage may be active at a time.
- Create the next Stage Issue only after the previous Stage's independently reviewed PR reaches `main`.
- Batch ordinary reversible follow-up fixes inside the active Stage/PR; do not pre-create speculative later Issues.
- A Stage/PR must state its problem, solution, scope, evidence, risk, rollback and documentation impact and receive independent review.

## 3. Frozen Stage order

The exact order is **L0 → L1 → L2 → L3 → L4 → L5 → L6**.

### L0 — Governance activation

**Result:** this docs-only Issue records DEC-084, the successor Goal, predecessor completion and Session-009 using exactly the nine tracked paths in Issue #316. No implementation or external action is authorized.

**Exit:** the nine-path diff is clean, relative links are bidirectionally discoverable, predecessor/current status wording is truthful, and the Ready PR's Required Checks are terminal green. The Goal remains branch `ACTIVATION_PENDING` until that PR reaches `main`.

### L1 — Real Needs Input backend

**Result:** implement and independently review the real FastAPI Needs Input read/resolve boundary and bounded Recovery. Preserve the current `needsInputRequest: null` state as the starting gap until the accepted L1 result changes it.

**Gate:** one L1 Issue/PR with a real consumer, representative behavior/error/invariant evidence and no unrelated persistence or public-contract expansion.

### L2 — Minimum Source/Brief persistence

**Result:** reconcile open tracking parents [#81](https://github.com/JettxonHo/ai-ecommerce-agent/issues/81) and [#82](https://github.com/JettxonHo/ai-ecommerce-agent/issues/82), then create only the immediately required bounded child Issues. Neither parent is treated as a one-PR implementation contract.

**Gate:** each child has a concrete consumer, ownership, acceptance and independent review; no speculative source/review platform is activated.

### L3 — Local Web lifecycle

**Result:** on Apple Silicon with Docker Desktop installed by the user, provide one reliable local command plus preflight, health, stop behavior and opening in the system default browser.

**Deferred:** native macOS App/WebView, signing and notarization. Intel support is Deferred; excluded from the first release.

### L4 — DeepSeek offline diagnosis/repair

**Result:** diagnose and, if independently justified, minimally repair the retained DeepSeek path offline while preserving the official base/model contract and local `.env` boundary.

**Gate:** no paid/live Provider call, Secret value access or inherited authorization. Any repair requires an exact bounded contract and independent review.

### L5 — Real DeepSeek acceptance

**Result:** after L4 reaches `main`, execute exactly one separately reviewed, exact-commit paid acceptance contract for official DeepSeek `deepseek-v4-pro` using fictional/sanitized material.

**Gate:** this is a new human Gate. The two historical DeepSeek authorizations and any previous smoke result do not carry forward; no retry, second Task or unbounded live matrix is implied.

### L6 — Clean-Mac acceptance and final Goal Review

**Result:** validate the reviewed result on another clean Apple Silicon Mac with the user-installed Docker Desktop prerequisite, then conduct an independent final Goal Review.

**Gate:** only the independent review can decide Goal completion; passing local CI, a screenshot or a single HTTP response is not sufficient by itself.

## 4. Product boundary

### In Scope

- Apple Silicon Macs only for the first release.
- Docker Desktop installed and managed by the user as a local prerequisite.
- A local Web App opened in the system default browser.
- The existing fixed single-user Action Workbench and its deterministic foundation as the starting product surface.
- Fictional or sanitized data for acceptance; no real customer/product material is required.
- Eventual real AI generation through the official DeepSeek API with model `deepseek-v4-pro`.
- A later project-root, Git-ignored `.env` convention containing `DEEPSEEK_API_KEY`, subject to the Secret rules below.

### Deferred

- Native macOS App/WebView, signing and notarization.
- Intel support is Deferred; excluded from the first release.
- Login, RBAC, multi-user behavior, tenant management and public deployment.
- macOS Keychain and Secret UI.
- Any capability not assigned to an active L Stage with an independently reviewed consumer.

### Out of Scope

- Real customer or production material in acceptance.
- Spider_XHS code reuse, cloning, installing, Cookie/login, proxy, signature/fingerprint execution, platform requests, scraping or publishing; `P5_REUSE_FROZEN` remains unchanged.
- Automatic publishing, unapproved Provider/model substitutions, fallback routing and extra paid calls.
- Public contracts, migrations, dependency/lockfile changes or architecture expansion unless a later accepted Stage explicitly requires them.

## 5. Secret and Provider boundary

The project-root `.env` convention is accepted only for a later implementation Stage. It must be Git-ignored and never committed, copied into a container image/build artifact, stored in PostgreSQL/browser storage, or included in logs/errors/evidence. A later preflight may check presence only and must never print, measure, hash or expose the value; only the local backend/provider adapter may receive it, and the browser receives capability/safe-error state only. L0 does not create, read, inspect or load `.env`, environment variables or Secret values.

The official DeepSeek API and `deepseek-v4-pro` remain the sole future real-AI contract. L4 is offline-only. L5 is a separate exact-commit paid Gate. No live authorization is inherited from the Fast Lane or predecessor Goal.

## 6. Evidence and acceptance

Use proportional evidence under [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md): one representative normal path, the primary recoverable failure and a critical invariant for each changed boundary, plus applicable Required Checks and independent review. Do not call the deterministic predecessor foundation real-Provider acceptance, general production readiness, public deployment or a complete real FastAPI Needs Input backend.

L0 acceptance requires:

- exactly the nine allowlisted tracked paths and no tenth tracked path;
- DEC-084 marked Accepted solely from the owner's explicit Codex conversation/session direction; the `ORCHESTRATOR_REVIEWER` durably recorded it in Issue #316;
- bidirectional relative links among DEC-084, this Goal, Session-009 and the predecessor Goal;
- predecessor `MVP0P_GOAL_COMPLETE` historical truth and successor branch `ACTIVATION_PENDING` truth;
- preserved terminal Fast Lane / `P5_REUSE_FROZEN` language and current `needsInputRequest: null` gap;
- stale/conflict scan, Markdown heading/fence/link checks and `git diff --check`;
- one Ready, non-draft PR closing Issue #316 with fresh Required Checks terminal green.

## 7. Human gates and stop conditions

Stop and request the owner for any real paid Provider call or Secret value access, new migration, destructive/broad data operation, public contract or product-direction change, expansion to Intel support (Deferred; excluded from the first release), native App/signing/login/multi-user/public deployment/real data/Spider_XHS behavior, inability to use exact `luna-worker`, or unresolved Accepted Decision conflict. Ordinary reversible in-contract local repository/branch/test/PR work remains governed by the active Stage and independent review.

## 8. Agent routing

Executable implementation in later Stages is routed to exact custom `luna-worker` per [DEC-071](../decisions/dec-071-luna-worker-exclusive-implementation-routing.md) and [DEC-072](../decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md). The configuration evidence is `CONFIG_VERIFIED` for `luna-worker` / `gpt-5.6-luna` / `max`; runtime metadata is not exposed, so no separate runtime status is claimed. Terra and Kimi are not fallbacks or L0 participants. Implementers do not approve or merge their own PRs.

## 9. Relationships

- **Decision:** [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md)
- **Session:** [Session-009](../sessions/session-009-local-ai-web-app-goal-activation.md)
- **Predecessor Goal:** [MVP-0P Local Action Workbench Productization Goal](mvp0-local-action-workbench-productization-goal.md)
- **Historical Fast Lane:** [MVP-0 Fast Lane Goal](mvp0-fast-lane-goal.md)
- **Activation Issue:** [Issue #316](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316)

## 10. Authorization boundary

This Goal authorizes only the L0 docs-only activation contract while its branch status is `ACTIVATION_PENDING`. No code, test, configuration, dependency, lockfile, migration, OpenAPI/generated client, Web implementation, Docker action, API/PostgreSQL launch, environment/Secret inspection, Provider/model/live call, Kimi/Terra action, native App work, public deployment or Spider_XHS action is authorized in L0. Later Stages require their own Issue/PR contract, independent review and applicable human Gate.
