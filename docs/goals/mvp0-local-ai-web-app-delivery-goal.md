# MVP-0L Local AI Web App Delivery Goal

> **Status on this branch:** `ACTIVE` — L0–L3 are merged/current through PRs #317, #328, #330 and #332; L3 is merge-effective at `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`. L4 [Issue #333](https://github.com/JettxonHo/ai-ecommerce-agent/issues/333) is review-ready with `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`, production diff zero and no Phase-B amendment. L5 remains gated.
>
> **Decision authority:** [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md) · [DEC-085](../decisions/dec-085-docker-only-local-web-lifecycle.md) · [Session-009](../sessions/session-009-local-ai-web-app-goal-activation.md)
>
> **Predecessor:** [MVP-0P Local Action Workbench Productization Goal](mvp0-local-action-workbench-productization-goal.md), now historical `MVP0P_GOAL_COMPLETE` after final-review PR [#315](https://github.com/JettxonHo/ai-ecommerce-agent/pull/315) reached `main`.
>
> **Historical Fast Lane:** [MVP-0 Fast Lane Goal](mvp0-fast-lane-goal.md) remains terminal `GOAL_BLOCKED`; its two failed DeepSeek runs, `INSUFFICIENT_SANITIZED_EVIDENCE`, observational ambiguity, no Provider acceptance and no inherited live authorization are preserved.

## 1. Goal outcome

Deliver a real-AI local Web App for a single operator on Apple Silicon Mac. The first release runs locally with user-installed Docker Desktop and opens in the system default browser. It builds on the completed deterministic Action Workbench, then closes the explicitly staged Needs Input, persistence, lifecycle, offline DeepSeek diagnosis, paid DeepSeek acceptance and clean-Mac review gates.

The eventual real-AI contract remains the official DeepSeek API with model `deepseek-v4-pro`. L0–L3 are merged/current through PRs #317, #328, #330 and #332 at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`. Issue #333 completes the provider-free L4 Phase-A qualification with `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`: current seams and official contract are coherent, retained sanitized evidence is ambiguous, and production diff is zero. No Provider/model call or Secret access was made; L5 remains a new human Gate. Documentation validation and ordinary Git/GitHub branch, push, PR and CI transport remain workflow activity, not product-runtime activity.

## 2. Activation and operating rule

- `MVP0P_GOAL_COMPLETE` is the merge-effective historical status of the predecessor and is not reopened.
- This successor is `ACTIVE` after the L0 PR reached `main`; L1, L2 and L3 are merged/current through PRs #328, #330 and #332, with L3 merge-effective at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`. Issue #333 is the review-ready L4 offline qualification with disposition `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`, production diff zero and no Phase-B amendment. L5 remains separately gated; no Provider or Secret action is permitted.
- Only one Stage may be active at a time.
- Create the next Stage Issue only after the previous Stage's independently reviewed PR reaches `main`.
- Batch ordinary reversible follow-up fixes inside the active Stage/PR; do not pre-create speculative later Issues.
- A Stage/PR must state its problem, solution, scope, evidence, risk, rollback and documentation impact and receive independent review.

## 3. Frozen Stage order

The exact order is **L0 → L1 → L2 → L3 → L4 → L5 → L6**.

Within the successor's product delivery, the owner-confirmed MBL-first sequence is **L2 → L3 → L4 → L5 → Agent UI → L6**. The Agent UI remains gated until the real-AI MBL is accepted; it is not production scope in L2.

### L0 — Governance activation

**Result:** this docs-only Issue recorded DEC-084, the successor Goal, predecessor completion and Session-009 using exactly the nine tracked paths in Issue #316. It is merged/current through PR #317; no implementation or product-runtime/Provider/API/platform action was authorized in L0.

**Exit:** the nine-path diff was clean, relative links were bidirectionally discoverable, predecessor/current status wording was truthful, and the Ready PR's Required Checks reached terminal green. The Goal is now `ACTIVE`.

### L1 — Real Needs Input backend

**Result:** Issue #318 implements the real FastAPI Needs Input read/resolve boundary and bounded Recovery over one additive Task-owned PostgreSQL table, with current-request projection, recomposition durability and the existing Web one-page Intake consumer. Its provider-free runtime acceptance passed 6/6 backend integration cases and 4/4 real-backend browser cases, including newer-request supersession, sufficient recovery and reload persistence.

**Gate:** one L1 Issue/PR with a real consumer, representative behavior/error/invariant evidence and no unrelated persistence or public-contract expansion; independent five-axis review is `PASS`, and PR #328 is merged/current. L2 is merged/current through PR #330; L3 is merged/current through PR #332. L4 Issue #333 is review-ready with its offline qualification disposition and no production repair.

### L2 — Minimum Source/Brief persistence

**Result:** L2 is exactly one bounded persistence acceptance/reconciliation Issue/PR, not an umbrella or multi-child implementation batch. Issue #329 / PR #330's one-time provider-free runtime characterization from reviewed `main` proves that Task primary input, current generated and confirmed Marketing/Xiaohongshu results, immutable export snapshots and stale revision/idempotency fences survive accepted recomposition/replay paths and a materially newer fictional input. At exact merge-effective base `dbccacacc54cb21c393987a8612dfc6aa825093b`, the follow-up runtime passed all six tests in `1.41s`; the blocking review finding was resolved by test-only assertions, independent five-axis review is `PASS`, fresh Required Checks are `12/12`, PR #330 is merged/current and Issue #329 is closed. The historical first `6 passed / 1 failed` `TEST_FIXTURE_PRECONDITION_MISMATCH` and lost temporary clones/eight-path diff remain disclosed history, not a product defect. Residual unconsumed scope in tracking parents [#81](https://github.com/JettxonHo/ai-ecommerce-agent/issues/81) and [#82](https://github.com/JettxonHo/ai-ecommerce-agent/issues/82) remains Deferred; neither parent is closed or mutated, and L2 creates no child implementation Issues or revives the full Source/Review platform without a concrete later consumer and a new explicit contract. Review Draft autosave, diff and stale-draft recovery remain Deferred. If evidence contradicts the minimum persistence, stop and return the exact gap; no silent production-code repair, migration, public-contract change or child-Issue creation/widening is authorized.

**Gate:** one independently reviewed L2 Issue/PR records the exact reviewed-main evidence. The merge-effective base `dbccacacc54cb21c393987a8612dfc6aa825093b` has provider-free runtime `PASS`, independent five-axis `PASS` and fresh Required Checks `12/12`; PR #330 is merged/current and Issue #329 is closed. No child Issues, migration, public contract, dependency authorization or full Source/Review platform revival is authorized without a concrete later consumer and a new explicit contract.

### L3 — Local Web lifecycle

**Result:** Issue #331 / PR #332 is merged/current at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e` after the recorded offline RED→GREEN, historical image-build `HOLD`, corrected-pin provider-free runtime `PASS`, independent five-axis review `PASS` at `f831519` and fresh Required Checks `12/12`. Native App/WebView, signing and notarization remain Deferred; Intel support is Deferred and excluded from the first release.

**Deferred:** native macOS App/WebView, signing and notarization. Intel support is Deferred; excluded from the first release.

### L4 — DeepSeek offline diagnosis/repair

**Result:** Issue #333 completes the provider-free Phase-A diagnosis against the retained DeepSeek path. The current seams and first-party contract are coherent, the sanitized evidence remains observationally ambiguous, and no general correctness RED justified a production repair. Disposition: `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`; production diff is zero and no Phase-B amendment exists.

**Gate:** L4 qualification is review-ready and requires independent five-axis review/merge. No paid/live Provider call, Secret value access, Phase-B repair, or inherited authorization occurred. L5 remains a separate exact-commit human Gate.

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

Use proportional evidence under [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md): one representative normal path, the primary recoverable failure and a critical invariant for each changed boundary, plus applicable Required Checks and independent review. L0–L3 are merged/current through PRs #317, #328, #330 and #332 at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`. Issue #333's provider-free Phase-A evidence and first-party contract recheck are recorded in the [L4 review](../reviews/mvp0l-l4-deepseek-offline-qualification.md) with disposition `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`, production diff zero and no Phase-B amendment. No further runtime or Provider authorization is permitted.

L0 acceptance requires:

- exactly the nine allowlisted tracked paths and no tenth tracked path;
- DEC-084 marked Accepted solely from the owner's explicit Codex conversation/session direction; the `ORCHESTRATOR_REVIEWER` durably recorded it in [Issue #316 comment](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316#issuecomment-5388616747);
- bidirectional relative links among DEC-084, this Goal, Session-009 and the predecessor Goal;
- predecessor `MVP0P_GOAL_COMPLETE` historical truth and successor `ACTIVE` truth after L0 PR #317;
- preserved terminal Fast Lane / `P5_REUSE_FROZEN` language and recorded the pre-L1 `needsInputRequest: null` gap;
- stale/conflict scan, Markdown heading/fence/link checks and `git diff --check`;
- one Ready, non-draft PR closing Issue #316 with fresh Required Checks terminal green.

Issue #318 L1 acceptance is recorded in the [current review](../reviews/mvp0l-l1-needs-input-backend.md); Issue #329 / PR #330 records the bounded L2 persistence acceptance; Issue #331 / PR #332 records the merged/current L3 lifecycle at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`; and Issue #333 / the [L4 review](../reviews/mvp0l-l4-deepseek-offline-qualification.md) records provider-free offline qualification with `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`. No live Provider acceptance is claimed.

## 7. Human gates and stop conditions

Stop and request the owner for any real paid Provider call or Secret value access, new migration, destructive/broad data operation, public contract or product-direction change, expansion to Intel support (Deferred; excluded from the first release), native App/signing/login/multi-user/public deployment/real data/Spider_XHS behavior, inability to use exact `luna-worker`, or unresolved Accepted Decision conflict. Ordinary reversible in-contract local repository/branch/test/PR work remains governed by the active Stage and independent review.

## 8. Agent routing

Executable implementation in later Stages is routed to exact custom `luna-worker` per [DEC-071](../decisions/dec-071-luna-worker-exclusive-implementation-routing.md) and [DEC-072](../decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md). The configuration evidence is `CONFIG_VERIFIED` for `luna-worker` / `gpt-5.6-luna` / `max`; runtime metadata is not exposed, so no separate runtime status is claimed. Terra and Kimi are not fallbacks or L0 participants. Implementers do not approve or merge their own PRs.

## 9. Relationships

- **Decision:** [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md)
- **L3 Decision:** [DEC-085](../decisions/dec-085-docker-only-local-web-lifecycle.md)
- **Session:** [Session-009](../sessions/session-009-local-ai-web-app-goal-activation.md)
- **Predecessor Goal:** [MVP-0P Local Action Workbench Productization Goal](mvp0-local-action-workbench-productization-goal.md)
- **Historical Fast Lane:** [MVP-0 Fast Lane Goal](mvp0-fast-lane-goal.md)
- **Activation Issue:** [Issue #316](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316)
- **Current L2 Issue:** [Issue #329](https://github.com/JettxonHo/ai-ecommerce-agent/issues/329)
- **Current L3 Issue:** [Issue #331](https://github.com/JettxonHo/ai-ecommerce-agent/issues/331)
- **Current L4 Issue:** [Issue #333](https://github.com/JettxonHo/ai-ecommerce-agent/issues/333) · [L4 qualification review](../reviews/mvp0l-l4-deepseek-offline-qualification.md)

## 10. Authorization boundary

L0's docs-only activation contract is complete. L1, L2 and L3 are merged/current through PRs #328, #330 and #332 at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`. Issue #333 completes provider-free L4 Phase A with disposition `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`, production diff zero and no Phase-B amendment; independent review/merge remains required. No Provider/model/live call, Secret/.env access, public contract, migration/schema expansion, dependency/lockfile change, native App work, public deployment or Spider_XHS action is authorized. L5 remains a separate exact-commit human Gate.
