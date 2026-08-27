# MVP-0L Local AI Web App Delivery Goal

> **Status on this branch:** `ACTIVE` — L0 PR #317 for [Issue #316](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316) reached `main`; L1 [Issue #318](https://github.com/JettxonHo/ai-ecommerce-agent/issues/318) is merged/current through PR #328 after its independent five-axis review `PASS` and provider-free runtime acceptance. L2 [Issue #329](https://github.com/JettxonHo/ai-ecommerce-agent/issues/329) / PR #330 is merged/current at exact `origin/main` base `dbccacacc54cb21c393987a8612dfc6aa825093b`; its provider-free runtime, independent five-axis review and fresh Required Checks are `PASS`/`12/12`, and Issue #329 is closed. L3 [Issue #331](https://github.com/JettxonHo/ai-ecommerce-agent/issues/331) is the active Docker-only local Web implementation Stage with offline GREEN and one corrected-pin provider-free runtime `PASS` after a historical first image-build `HOLD` on unpublished `uv==0.12.8`; independent review and merge remain pending.
>
> **Decision authority:** [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md) · [DEC-085](../decisions/dec-085-docker-only-local-web-lifecycle.md) · [Session-009](../sessions/session-009-local-ai-web-app-goal-activation.md)
>
> **Predecessor:** [MVP-0P Local Action Workbench Productization Goal](mvp0-local-action-workbench-productization-goal.md), now historical `MVP0P_GOAL_COMPLETE` after final-review PR [#315](https://github.com/JettxonHo/ai-ecommerce-agent/pull/315) reached `main`.
>
> **Historical Fast Lane:** [MVP-0 Fast Lane Goal](mvp0-fast-lane-goal.md) remains terminal `GOAL_BLOCKED`; its two failed DeepSeek runs, `INSUFFICIENT_SANITIZED_EVIDENCE`, observational ambiguity, no Provider acceptance and no inherited live authorization are preserved.

## 1. Goal outcome

Deliver a real-AI local Web App for a single operator on Apple Silicon Mac. The first release runs locally with user-installed Docker Desktop and opens in the system default browser. It builds on the completed deterministic Action Workbench, then closes the explicitly staged Needs Input, persistence, lifecycle, offline DeepSeek diagnosis, paid DeepSeek acceptance and clean-Mac review gates.

The eventual real-AI contract remains the official DeepSeek API with model `deepseek-v4-pro`. L0 was governance-only and is merged/current. Issue #318 now provides the real FastAPI Needs Input read/resolve and bounded Recovery vertical through one additive Task-owned table and the existing Web consumer; its provider-free runtime acceptance passed the exact 6/6 backend and 4/4 browser gates. No Provider/model call or Secret access was made. Independent five-axis review is `PASS` and PR #328 makes L1 merge-effective. Issue #329 / PR #330 records the bounded persistence characterization at the exact merge-effective base `dbccacacc54cb21c393987a8612dfc6aa825093b`; stale revision/idempotency replays are rejected with `409` before and after recomposition, the one-time provider-free runtime passed 6/6 backend cases in `1.41s`, independent five-axis review is `PASS`, fresh Required Checks are `12/12`, PR #330 is merged/current and Issue #329 is closed. Issue #331 now owns the bounded Docker-only local Web lifecycle. The ORCHESTRATOR_REVIEWER bounded repair/runtime ruling under the owner's standing serial-order instruction records the first image-build-only `HOLD` caused by unpublished `uv==0.12.8`, the tests-first `uv==0.12.6` repair, and one corrected-pin provider-free runtime `PASS` with both images, health, browser-after-health, bounded `/tasks`, Ctrl-C 130 and exact cleanup. Independent review, Ready PR/checks and merge remain pending. Documentation validation and ordinary Git/GitHub branch, push, PR and CI transport remain allowed as workflow activity, not product-runtime activity.

## 2. Activation and operating rule

- `MVP0P_GOAL_COMPLETE` is the merge-effective historical status of the predecessor and is not reopened.
- This successor is `ACTIVE` after the L0 PR reached `main`; Issue #318 is merged/current through PR #328, and Issue #329 / PR #330 is merged/current at exact base `dbccacacc54cb21c393987a8612dfc6aa825093b` with Issue #329 closed. L3 Issue #331 is the sole active Stage; its offline implementation is GREEN and its single corrected-pin provider-free runtime is `PASS` after the historical first build-only `HOLD`; independent review and merge remain pending.
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

**Gate:** one L1 Issue/PR with a real consumer, representative behavior/error/invariant evidence and no unrelated persistence or public-contract expansion; independent five-axis review is `PASS`, and PR #328 is merged/current. L2 is merged/current through PR #330; L3 is now the active Stage.

### L2 — Minimum Source/Brief persistence

**Result:** L2 is exactly one bounded persistence acceptance/reconciliation Issue/PR, not an umbrella or multi-child implementation batch. Issue #329 / PR #330's one-time provider-free runtime characterization from reviewed `main` proves that Task primary input, current generated and confirmed Marketing/Xiaohongshu results, immutable export snapshots and stale revision/idempotency fences survive accepted recomposition/replay paths and a materially newer fictional input. At exact merge-effective base `dbccacacc54cb21c393987a8612dfc6aa825093b`, the follow-up runtime passed all six tests in `1.41s`; the blocking review finding was resolved by test-only assertions, independent five-axis review is `PASS`, fresh Required Checks are `12/12`, PR #330 is merged/current and Issue #329 is closed. The historical first `6 passed / 1 failed` `TEST_FIXTURE_PRECONDITION_MISMATCH` and lost temporary clones/eight-path diff remain disclosed history, not a product defect. Residual unconsumed scope in tracking parents [#81](https://github.com/JettxonHo/ai-ecommerce-agent/issues/81) and [#82](https://github.com/JettxonHo/ai-ecommerce-agent/issues/82) remains Deferred; neither parent is closed or mutated, and L2 creates no child implementation Issues or revives the full Source/Review platform without a concrete later consumer and a new explicit contract. Review Draft autosave, diff and stale-draft recovery remain Deferred. If evidence contradicts the minimum persistence, stop and return the exact gap; no silent production-code repair, migration, public-contract change or child-Issue creation/widening is authorized.

**Gate:** one independently reviewed L2 Issue/PR records the exact reviewed-main evidence. The merge-effective base `dbccacacc54cb21c393987a8612dfc6aa825093b` has provider-free runtime `PASS`, independent five-axis `PASS` and fresh Required Checks `12/12`; PR #330 is merged/current and Issue #329 is closed. No child Issues, migration, public contract, dependency authorization or full Source/Review platform revival is authorized without a concrete later consumer and a new explicit contract.

### L3 — Local Web lifecycle

**Result:** Issue #331 supplies the tracked [AI Ecommerce Agent.command](../../AI%20Ecommerce%20Agent.command) entry and bounded `scripts/mvp0/local-web` lifecycle for Apple Silicon with user-installed Docker Desktop. The Docker-only `local-web` Compose profile renders exactly persistent Postgres, private FastAPI and loopback static Web services; preflight validates the profile and pinned images, readiness waits for API and Web health before opening the system default browser, default stop preserves the named database volume, and `--ephemeral` removes its exact repository-prefixed project and paired `${project}-pg` volume. The ORCHESTRATOR_REVIEWER ruling under the owner's standing serial-order instruction records the first provider-free runtime `HOLD` at image build because `uv==0.12.8` was unpublished, then tests-first `uv==0.12.6` and one corrected-pin runtime `PASS`: both images built, PostgreSQL/API/Web became healthy, the browser opened after health, one bounded `/tasks` read returned the expected title/heading, Ctrl-C exited 130, and exact ephemeral cleanup removed the target resources while ports 5173/55432 were free. Offline RED→GREEN, rendered configuration and static/backend/Web gates are complete; independent review, Ready PR/checks and merge remain pending. No Provider/model/Secret/.env or Agent UI/L4 action was authorized.

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

Use proportional evidence under [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md): one representative normal path, the primary recoverable failure and a critical invariant for each changed boundary, plus applicable Required Checks and independent review. Issue #318's provider-free runtime evidence is a bounded L1 acceptance input, not live Provider acceptance, general production readiness or public deployment; PR #328 makes L1 merge-effective with independent five-axis review `PASS`. Issue #329 / PR #330's provider-free six-test persistence characterization is a bounded L2 acceptance input at exact merge-effective base `dbccacacc54cb21c393987a8612dfc6aa825093b`; runtime, independent five-axis review and fresh Required Checks are `PASS`/`12/12`, PR #330 is merged/current and Issue #329 is closed. Issue #331's L3 review records the exact two-attempt history: first image-build-only `HOLD` on unpublished `uv==0.12.8`, tests-first official `uv==0.12.6` repair with frozen locks, then one corrected-pin provider-free runtime `PASS` for images, health, browser-after-health, bounded `/tasks`, Ctrl-C 130 and exact cleanup. Independent five-axis review, Ready PR/checks and merge remain pending.

L0 acceptance requires:

- exactly the nine allowlisted tracked paths and no tenth tracked path;
- DEC-084 marked Accepted solely from the owner's explicit Codex conversation/session direction; the `ORCHESTRATOR_REVIEWER` durably recorded it in [Issue #316 comment](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316#issuecomment-5388616747);
- bidirectional relative links among DEC-084, this Goal, Session-009 and the predecessor Goal;
- predecessor `MVP0P_GOAL_COMPLETE` historical truth and successor `ACTIVE` truth after L0 PR #317;
- preserved terminal Fast Lane / `P5_REUSE_FROZEN` language and recorded the pre-L1 `needsInputRequest: null` gap;
- stale/conflict scan, Markdown heading/fence/link checks and `git diff --check`;
- one Ready, non-draft PR closing Issue #316 with fresh Required Checks terminal green.

Issue #318 L1 acceptance is recorded in the [current review](../reviews/mvp0l-l1-needs-input-backend.md) and [live Issue comment](https://github.com/JettxonHo/ai-ecommerce-agent/issues/318#issuecomment-5436381488): one additive migration, real PostgreSQL lifecycle, existing Web consumer, exact 6/6 backend and 4/4 browser runtime gates, guarded cleanup, independent five-axis review `PASS`, and merge-effective PR #328. OpenAPI and generated Web types remain byte-identical. Issue #329's owner-confirmed contract is in [the owner confirmation](https://github.com/JettxonHo/ai-ecommerce-agent/issues/329#issuecomment-5437646180), its blocking review resolution is [durably recorded](https://github.com/JettxonHo/ai-ecommerce-agent/pull/330#issuecomment-5438696727), and its one-time evidence is recorded in [the L2 review](../reviews/mvp0l-l2-minimum-persistence.md): six-test provider-free backend persistence characterization, exact marker proof, stale revision/idempotency rejection, immutable snapshot/replay evidence and guarded cleanup. The merge-effective base is `dbccacacc54cb21c393987a8612dfc6aa825093b`; independent review is `PASS`, fresh Required Checks are `12/12`, PR #330 is merged/current and Issue #329 is closed. Issue #331's active L3 evidence is recorded in [the L3 review](../reviews/mvp0l-l3-docker-local-web-lifecycle.md).

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

## 10. Authorization boundary

L0's docs-only activation contract is complete. Issue #318 is merged/current through PR #328. Issue #329 / PR #330 is merged/current at exact base `dbccacacc54cb21c393987a8612dfc6aa825093b`; its one-time provider-free persistence acceptance, independent review and Required Checks are complete, and Issue #329 is closed. Issue #331 is the active, separately bounded L3 contract: it allows only the exact Docker-only local-Web lifecycle and its 22-path allowlist, offline RED→GREEN evidence, one provider-free `--ephemeral` runtime acceptance after offline gates, and one independent review; no Provider/model/live call, Secret/.env access, public contract, migration/schema expansion, dependency/lockfile change, native App work, public deployment or Spider_XHS action is authorized. The first image-build-only attempt is historical `HOLD`; the single corrected-pin provider-free runtime is `PASS`. L3's remaining gates are final evidence reconciliation, ordinary commit/Ready PR, fresh Required Checks and independent five-axis review/merge; later Stages require their own Issue/PR contract, independent review and applicable human Gate.
