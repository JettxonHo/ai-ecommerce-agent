# MVP-0L Local AI Web App Delivery Goal

> **Status on this branch:** `REBASELINE_PENDING`. L0–L4 accepted evidence remains preserved. L5 [Issue #335](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335) / [PR #336](https://github.com/JettxonHo/ai-ecommerce-agent/pull/336) is terminal `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` at exact head `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`, with no export files; authorization is consumed and no further run is authorized. L6 is `NOT_EXECUTED`; Agent UI remains frozen. **Only after the Issue #339 PR reaches `main`** does this Goal become `TERMINAL_INCOMPLETE_L5_FAILED`.
>
> **Decision authority:** [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md) · [DEC-085](../decisions/dec-085-docker-only-local-web-lifecycle.md) · [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md) · [Session-009](../sessions/session-009-local-ai-web-app-goal-activation.md) · [Session-011](../sessions/session-011-mvp0l-terminal-rebaseline.md)
>
> **Predecessor:** [MVP-0P Local Action Workbench Productization Goal](mvp0-local-action-workbench-productization-goal.md), now historical `MVP0P_GOAL_COMPLETE` after final-review PR [#315](https://github.com/JettxonHo/ai-ecommerce-agent/pull/315) reached `main`.
>
> **Historical Fast Lane:** [MVP-0 Fast Lane Goal](mvp0-fast-lane-goal.md) remains terminal `GOAL_BLOCKED`; its two failed DeepSeek runs, `INSUFFICIENT_SANITIZED_EVIDENCE`, observational ambiguity, no Provider acceptance and no inherited live authorization are preserved.
>
> **Successor validation:** [Real Product-to-Brief Pilot Goal](real-product-to-brief-pilot-goal.md) is `ACTIVATION_PENDING` and P0 `NOT_STARTED` on this branch. Only after the same PR reaches `main` does Pilot become `ACTIVE` and P0 `READY_NOT_STARTED`; the Pilot does not resume [#335 / PR #336](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335) or authorize another run.

## 1. Goal outcome

The Goal attempted to deliver a real-AI local Web App for a single operator on Apple Silicon Mac. It preserved the completed deterministic Action Workbench and closed L0–L4, but the paid L5 attempt ended without exports. DEC-087 therefore terminally rebaselines the Goal instead of continuing repair, Agent UI or L6.

The eventual real-AI contract remains the official DeepSeek API with model `deepseek-v4-pro`. L0–L3 are merged/current through PRs #317, #328, #330 and #332 at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`. Issue #333 is closed via merged PR #334 at exact `origin/main@ef5ac0d4b372c1478ee2541ee3ec5318e72a1060` with provider-free `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`, production diff zero and no Phase-B amendment. No Provider/model call or Secret access was made in L4; the single authorized L5 #335 / PR #336 run has terminal disposition `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` at exact head `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`, with authorization consumed and no further run authorized. Documentation validation and ordinary Git/GitHub branch, push, PR and CI transport remain workflow activity, not product-runtime activity.

## 2. Activation and operating rule

- `MVP0P_GOAL_COMPLETE` is the merge-effective historical status of the predecessor and is not reopened.
- On this branch the Goal is `REBASELINE_PENDING`. L1–L4 merged evidence and the exact L5 terminal failure remain preserved; L6 is `NOT_EXECUTED`, Agent UI frozen, and no new Provider or Secret action is authorized.
- Only after the Issue #339 PR reaches `main` does the Goal become `TERMINAL_INCOMPLETE_L5_FAILED`. It does not become `COMPLETE`.
- Historical operating rule through L5: only one MVP-0L Stage could be active at a time, and a next Stage Issue waited for the previous Stage's independently reviewed PR to reach `main`.
- Historical same-Stage rule through L5: ordinary reversible follow-up fixes stayed inside the active Stage/PR, whose problem, solution, scope, evidence, risk, rollback and documentation impact required independent review.
- DEC-087 retires those rules after terminal L5. No L6 or next MVP-0L Stage Issue is authorized; L6 remains `NOT_EXECUTED` and Agent UI remains frozen.
- The Real Product-to-Brief Pilot is `ACTIVATION_PENDING` on this branch and becomes `ACTIVE` only at the same merge-effective rebaseline event; P0 then becomes only `READY_NOT_STARTED`.

## 3. Frozen Stage order

The exact order is **L0 → L1 → L2 → L3 → L4 → L5 → L6**.

The historical planned sequence was **L2 → L3 → L4 → L5 → Agent UI → L6**. DEC-087 terminates that continuation after failed L5: Agent UI stays frozen and L6 stays `NOT_EXECUTED`.

### L0 — Governance activation

**Result:** this docs-only Issue recorded DEC-084, the successor Goal, predecessor completion and Session-009 using exactly the nine tracked paths in Issue #316. It is merged/current through PR #317; no implementation or product-runtime/Provider/API/platform action was authorized in L0.

**Exit:** the nine-path diff was clean, relative links were bidirectionally discoverable, predecessor/current status wording was truthful, and the Ready PR's Required Checks reached terminal green. The Goal is now `ACTIVE`.

### L1 — Real Needs Input backend

**Result:** Issue #318 implements the real FastAPI Needs Input read/resolve boundary and bounded Recovery over one additive Task-owned PostgreSQL table, with current-request projection, recomposition durability and the existing Web one-page Intake consumer. Its provider-free runtime acceptance passed 6/6 backend integration cases and 4/4 real-backend browser cases, including newer-request supersession, sufficient recovery and reload persistence.

**Gate:** one L1 Issue/PR with a real consumer, representative behavior/error/invariant evidence and no unrelated persistence or public-contract expansion; independent five-axis review is `PASS`, and PR #328 is merged/current. L2 is merged/current through PR #330; L3 is merged/current through PR #332. L4 Issue #333 is closed via merged PR #334 at exact `origin/main@ef5ac0d4b372c1478ee2541ee3ec5318e72a1060` with its offline qualification disposition and no production repair; L5 #335 / PR #336 is terminal `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` with no further run authorized.

### L2 — Minimum Source/Brief persistence

**Result:** L2 is exactly one bounded persistence acceptance/reconciliation Issue/PR, not an umbrella or multi-child implementation batch. Issue #329 / PR #330's one-time provider-free runtime characterization from reviewed `main` proves that Task primary input, current generated and confirmed Marketing/Xiaohongshu results, immutable export snapshots and stale revision/idempotency fences survive accepted recomposition/replay paths and a materially newer fictional input. At exact merge-effective base `dbccacacc54cb21c393987a8612dfc6aa825093b`, the follow-up runtime passed all six tests in `1.41s`; the blocking review finding was resolved by test-only assertions, independent five-axis review is `PASS`, fresh Required Checks are `12/12`, PR #330 is merged/current and Issue #329 is closed. The historical first `6 passed / 1 failed` `TEST_FIXTURE_PRECONDITION_MISMATCH` and lost temporary clones/eight-path diff remain disclosed history, not a product defect. Residual unconsumed scope in tracking parents [#81](https://github.com/JettxonHo/ai-ecommerce-agent/issues/81) and [#82](https://github.com/JettxonHo/ai-ecommerce-agent/issues/82) remains Deferred; neither parent is closed or mutated, and L2 creates no child implementation Issues or revives the full Source/Review platform without a concrete later consumer and a new explicit contract. Review Draft autosave, diff and stale-draft recovery remain Deferred. If evidence contradicts the minimum persistence, stop and return the exact gap; no silent production-code repair, migration, public-contract change or child-Issue creation/widening is authorized.

**Gate:** one independently reviewed L2 Issue/PR records the exact reviewed-main evidence. The merge-effective base `dbccacacc54cb21c393987a8612dfc6aa825093b` has provider-free runtime `PASS`, independent five-axis `PASS` and fresh Required Checks `12/12`; PR #330 is merged/current and Issue #329 is closed. No child Issues, migration, public contract, dependency authorization or full Source/Review platform revival is authorized without a concrete later consumer and a new explicit contract.

### L3 — Local Web lifecycle

**Result:** Issue #331 / PR #332 is merged/current at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e` after the recorded offline RED→GREEN, historical image-build `HOLD`, corrected-pin provider-free runtime `PASS`, independent five-axis review `PASS` at `f831519` and fresh Required Checks `12/12`. Native App/WebView, signing and notarization remain Deferred; Intel support is Deferred and excluded from the first release.

**Deferred:** native macOS App/WebView, signing and notarization. Intel support is Deferred; excluded from the first release.

### L4 — DeepSeek offline diagnosis/repair

**Result:** Issue #333 completes the provider-free Phase-A diagnosis against the retained DeepSeek path. The current seams and first-party contract are coherent, the sanitized evidence remains observationally ambiguous, and no general correctness RED justified a production repair. Disposition: `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`; production diff is zero and no Phase-B amendment exists.

**Gate:** L4 qualification is closed via merged PR #334 at exact `origin/main@ef5ac0d4b372c1478ee2541ee3ec5318e72a1060`; its independent review/merge is complete, with no paid/live Provider call, Secret value access, Phase-B repair or inherited authorization. L5 #335 / PR #336 is terminal `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` at exact head `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`; no further run is authorized.

### L5 — Real DeepSeek acceptance

**Result:** the single owner-authorized #335 / PR #336 exact-commit paid acceptance run for official DeepSeek `deepseek-v4-pro` at head `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f` has terminal disposition `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS`. It made five ordered calls with retry/recovery `0/0`; sanitized evidence records token totals `23845`/`43999`/`67844`, `validated_candidates=true`, `confirmed_result=true`, both immutable export gates false and the UTF-8/download gate false. No export directory/file resulted, so no human usability judgment was possible. Authorization is consumed; no rerun, repair, substitution, top-up or further run is authorized. The fictional/sanitized material is engineering/L5 evidence only, not Pilot business-cohort material.

**Gate:** the #335 authorization was scoped only to that exact contract and is consumed by its single run. The two historical Fast Lane DeepSeek authorizations and any previous smoke result did not carry forward; no retry, second Task, repair, substitution, top-up or unbounded live matrix is implied.

### L6 — Clean-Mac acceptance and final Goal Review

**Result:** `NOT_EXECUTED`. The terminal L5 no-export result left no accepted reviewed result for clean-Mac validation.

**Gate:** DEC-087 does not authorize L6. The Goal becomes `TERMINAL_INCOMPLETE_L5_FAILED`, never `COMPLETE`, only after the Issue #339 PR reaches `main`.

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

Use proportional evidence under [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md): one representative normal path, the primary recoverable failure and a critical invariant for each changed boundary, plus applicable Required Checks and independent review. L0–L3 are merged/current through PRs #317, #328, #330 and #332 at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`. Issue #333's provider-free Phase-A evidence and first-party contract recheck are recorded in the [L4 review](../reviews/mvp0l-l4-deepseek-offline-qualification.md) with disposition `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`, production diff zero and no Phase-B amendment; PR #334 merged and closed #333 at exact `origin/main@ef5ac0d4b372c1478ee2541ee3ec5318e72a1060`. Current #335 / PR #336 records terminal `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` at exact head `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`; no further run is authorized. G0 creates no new runtime or Provider authorization.

L0 acceptance requires:

- exactly the nine allowlisted tracked paths and no tenth tracked path;
- DEC-084 marked Accepted solely from the owner's explicit Codex conversation/session direction; the `ORCHESTRATOR_REVIEWER` durably recorded it in [Issue #316 comment](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316#issuecomment-5388616747);
- bidirectional relative links among DEC-084, this Goal, Session-009 and the predecessor Goal;
- predecessor `MVP0P_GOAL_COMPLETE` historical truth and successor `ACTIVE` truth after L0 PR #317;
- preserved terminal Fast Lane / `P5_REUSE_FROZEN` language and recorded the pre-L1 `needsInputRequest: null` gap;
- stale/conflict scan, Markdown heading/fence/link checks and `git diff --check`;
- one Ready, non-draft PR closing Issue #316 with fresh Required Checks terminal green.

Issue #318 L1 acceptance is recorded in the [current review](../reviews/mvp0l-l1-needs-input-backend.md); Issue #329 / PR #330 records the bounded L2 persistence acceptance; Issue #331 / PR #332 records the merged/current L3 lifecycle at exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`; and Issue #333 / the [L4 review](../reviews/mvp0l-l4-deepseek-offline-qualification.md) records provider-free offline qualification with `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`, closed by merged PR #334 at exact `origin/main@ef5ac0d4b372c1478ee2541ee3ec5318e72a1060`. Current L5 #335 / PR #336 records terminal `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS`; no Provider acceptance or further run is claimed.

## 7. Human gates and stop conditions

Stop and request the owner for any real paid Provider call or Secret value access, new migration, destructive/broad data operation, public contract or product-direction change, expansion to Intel support (Deferred; excluded from the first release), native App/signing/login/multi-user/public deployment/real data/Spider_XHS behavior, inability to use exact `luna-worker`, or unresolved Accepted Decision conflict. Ordinary reversible in-contract local repository/branch/test/PR work remains governed by the active Stage and independent review.

## 8. Agent routing

Executable implementation in later Stages is routed to exact custom `luna-worker` per [DEC-071](../decisions/dec-071-luna-worker-exclusive-implementation-routing.md) and [DEC-072](../decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md). The configuration evidence is `CONFIG_VERIFIED` for `luna-worker` / `gpt-5.6-luna` / `max`; runtime metadata is not exposed, so no separate runtime status is claimed. Terra and Kimi are not fallbacks or L0 participants. Implementers do not approve or merge their own PRs.

## 9. Relationships

- **Decisions:** [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md) · [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md)
- **L3 Decision:** [DEC-085](../decisions/dec-085-docker-only-local-web-lifecycle.md)
- **Sessions:** [Session-009](../sessions/session-009-local-ai-web-app-goal-activation.md) · [Session-011](../sessions/session-011-mvp0l-terminal-rebaseline.md)
- **Predecessor Goal:** [MVP-0P Local Action Workbench Productization Goal](mvp0-local-action-workbench-productization-goal.md)
- **Historical Fast Lane:** [MVP-0 Fast Lane Goal](mvp0-fast-lane-goal.md)
- **Activation Issue:** [Issue #316](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316)
- **Current L2 Issue:** [Issue #329](https://github.com/JettxonHo/ai-ecommerce-agent/issues/329)
- **Current L3 Issue:** [Issue #331](https://github.com/JettxonHo/ai-ecommerce-agent/issues/331)
- **Current L4 Issue:** [Issue #333](https://github.com/JettxonHo/ai-ecommerce-agent/issues/333) · [L4 qualification review](../reviews/mvp0l-l4-deepseek-offline-qualification.md)
- **Activation-pending successor validation:** [Real Product-to-Brief Pilot Goal](real-product-to-brief-pilot-goal.md) · [Pilot Contract](../product/real-product-to-brief-pilot-contract.md) · [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md) · [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md)

## 10. Authorization boundary

L0–L4 accepted evidence remains preserved. L5 #335 / PR #336 is terminal `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` at exact head `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`; its authorization is consumed and no further run is authorized. L6 is `NOT_EXECUTED`; Agent UI is frozen. On this branch MVP-0L is `REBASELINE_PENDING`, Pilot `ACTIVATION_PENDING`, P0 `NOT_STARTED`. Only after the Issue #339 PR reaches `main` do MVP-0L `TERMINAL_INCOMPLETE_L5_FAILED`, Pilot `ACTIVE` and P0 `READY_NOT_STARTED` become effective. No new Provider/model/live call, Secret/.env access, P0 execution, real input, public contract, migration/schema expansion, dependency/lockfile change, native App, public deployment or Spider_XHS action is authorized.
