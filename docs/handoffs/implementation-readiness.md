# Implementation Readiness

> **Status: predecessor `MVP0P_GOAL_COMPLETE` is historical merge-effective truth after PR #315 · successor [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md) is `ACTIVE` after L0 PR #317 reached `main` · L1 Issue #318 is merged/current through PR #328 after independent five-axis review `PASS` and provider-free runtime acceptance · L2 Issue #329 / PR #330 is the active minimum persistence acceptance/reconciliation Stage with provider-free runtime `PASS`, independent five-axis `PASS` and fresh Required Checks `12/12` at code/test head `2c1c1d39c44b77803f587785f07f741f8374ef29`; PR #330 remains `OPEN`/unmerged during this reconciliation, so L2 is not merge-effective until reviewed closure reaches `main`; L3 remains gated · predecessor P0–P5 complete · OLD FAST LANE TERMINAL `GOAL_BLOCKED` · P5 `P5_REUSE_FROZEN`**
>
> **Authority:** [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md) · [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md) · [Session-009](../sessions/session-009-local-ai-web-app-goal-activation.md) · predecessor [DEC-083](../decisions/dec-083-local-action-workbench-productization-goal.md) · [DEC-078](../decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md) · [DEC-081](../decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) · [DEC-082](../decisions/dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md)
>
> **Current release boundary:** the deterministic local loop and one-command demo are completed predecessor foundation, not live Provider acceptance. The old Fast Lane record remains terminal `GOAL_BLOCKED`: its first authorized smoke completed five calls and failed before `awaiting_review`; the second under [Issue #281](https://github.com/JettxonHo/ai-ecommerce-agent/issues/281) failed safely after one `product_intake_v1 / v1` call before `awaiting_review`. Both authorizations are consumed; no further Provider run is authorized. [DEC-081](../decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) Phase A ended with `INSUFFICIENT_SANITIZED_EVIDENCE`, observational ambiguity across mapper/schema/domain-admission boundaries, no production repair and no Phase B contract. `rejection_disposition` remains a Proposal only. The predecessor P0–P5 chain is complete; PR #315 made `MVP0P_GOAL_COMPLETE` merge-effective. L0 is merged/current through PR #317. Issue #318 now provides the real browser-to-FastAPI Needs Input/Recovery vertical; its provider-free runtime acceptance passed the exact 6/6 backend and 4/4 browser gates, independent five-axis review is `PASS`, and PR #328 makes L1 merge-effective. Issue #329 / PR #330 records a bounded provider-free six-test persistence characterization on an isolated ephemeral scope at code/test head `2c1c1d39c44b77803f587785f07f741f8374ef29`; the blocking stale revision/idempotency finding was resolved test-only, the runtime passed `6/6` in `1.41s`, independent five-axis review is `PASS`, and fresh Required Checks are `12/12`. PR #330 remains `OPEN`/unmerged, so L2 is not merge-effective and L3 remains gated. P5 docs/research is complete and independently reviewed as `P5_REUSE_FROZEN`; direct Spider_XHS reuse and platform behavior remain frozen and unauthorized. The successor L0–L6 order is governed by [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md).

P2's bounded surface is Running, Review and Results with structured business groups, separate Marketing / Xiaohongshu views, safe Markdown preview/export, raw JSON behind technical disclosure, and responsive keyboard / focus / reduced-motion boundaries. It does not claim Provider acceptance.

## 1. Product readiness

The following are accepted and sufficient for the minimal demo:

- primary user: small ecommerce product/content operator;
- job: turn product information into positioning and usable Briefs;
- platform-neutral core with Xiaohongshu as the first adapter;
- deterministic workflow with bounded model calls and one human confirmation;
- one fixed local workspace, recent Tasks and stable deep links;
- Marketing Brief, Xiaohongshu Brief and Markdown export;
- one fictional “城市通勤双肩包” sufficient-input acceptance path;
- honest insufficient-input behavior;
- a retained opt-in direct DeepSeek official `deepseek-v4-pro` seam plus terminal evidence from the two controlled runs; neither is Provider acceptance and no further run is authorized;
- the completed bounded offline Phase A diagnosis at the exact first-stage boundary with terminal `INSUFFICIENT_SANITIZED_EVIDENCE`; no production repair was made and no Phase B contract exists.
- an accepted next productization direction: fixed local single-user Action Workbench with `/tasks` action home, a Chinese five-stage rail, one Active Workspace, a collapsible `320–360px` Context Rail, structured Review and action-oriented Marketing / Xiaohongshu Results.
- the predecessor Goal's serial order P0 → P1 → P2 → P3 → P4 → P5 is complete; Issue #303 / PR #304, Issue #305 / PR #306 and Issue #247 are merged/current P1–P3 deliveries. Issue #308 is merged/current P4A, and Issue #310 records independently reviewed provider-free `P4_LOCAL_RELEASE_ACCEPTED` P4B execution evidence, completing the accepted P4 local scope. P5 docs/research is complete and independently reviewed as `P5_REUSE_FROZEN`; direct reuse and platform behavior remain frozen and unauthorized. PR #315 made `MVP0P_GOAL_COMPLETE` merge-effective. The successor Goal's exact serial order is L0 → L1 → L2 → L3 → L4 → L5 → L6; L0 is active after PR #317, L1 is merged/current through PR #328, and Issue #329 / PR #330 is the active L2 Stage with provider-free runtime `PASS`, independent five-axis `PASS` and fresh Required Checks `12/12` at code/test head `2c1c1d39c44b77803f587785f07f741f8374ef29`. PR #330 remains `OPEN`/unmerged, so L2 is not merge-effective until reviewed closure reaches `main`, and L3 remains gated. The owner-confirmed MBL-first sequence remains L2 → L3 → L4 → L5 → Agent UI → L6.
- the human A+C verdict `HUMAN_SELECTED_AC_BASELINE`; PR #299 remains open / unmerged, while Issue #303 / PR #304 is the merged/current P1 implementation.

No further Persona, RFC, general architecture, retrieval or enterprise-security planning is required for the deterministic foundation. The two controlled DeepSeek runs are terminal failure evidence, not Provider acceptance; #281 is closed and no further Provider run is authorized. Phase A is complete with terminal `INSUFFICIENT_SANITIZED_EVIDENCE`, establishing observational ambiguity only; no production repair or Phase B contract exists, and `rejection_disposition` remains a Proposal only. Later deferred capabilities retain their separate gates.

## 2. Implemented foundation inherited by the productization Goal

Implemented or physically present:

- repository, Python package, TypeScript application and CI foundations;
- local PostgreSQL lifecycle and compatibility evidence;
- Task / Run / Stage and Source persistence components;
- bounded Durable Dispatch, checkpoint and runtime diagnostic seams;
- provider-neutral Model Runtime, scripted substitute, reviewed offline direct DeepSeek adapter and retained shared live-evidence seam; superseded OpenAI/Qwen provider-specific adapters are removed by the bounded cleanup;
- private output contracts for Facts, Insight, Positioning, Marketing Brief and Xiaohongshu mapping;
- Marketing / Xiaohongshu domain snapshots and safe Markdown renderer;
- authored OpenAPI and generated TypeScript client;
- FastAPI fixed-workspace foundation;
- Task gateway, recent/create/read routes, Task-scoped input/result/review/export routes and stable deep links;
- deterministic scripted Facts → Insight → Positioning → Marketing Brief → Xiaohongshu pipeline;
- Workbench projection and TaskWorkbench intake/progress/review/results/export UI;
- Issue #303 / PR #304's P1 Action Home / five-stage rail / Active Workspace / Context Rail shell, merged/current;
- Issue #305 / PR #306's P2 Running / Review / Results implementation, merged/current;
- Reconciled Issue #247's P3 private Needs Input gateway, Chinese-first bounded action workspace and failed/paused Recovery workspace, merged/current;
- Issue #318's real PostgreSQL Needs Input read/resolve boundary, current-request projection, bounded recovery reconciliation and one-page Intake consumer; its one-time provider-free runtime acceptance passed 6 backend and 4 browser cases with exact cleanup;
- Issue #329 / PR #330's bounded persistence characterization: the existing Task primary input, generated/confirmed Marketing and Xiaohongshu results, immutable Markdown export snapshots and stale revision/idempotency fences survive recomposition/replay and a materially newer fictional input; its one-time provider-free runtime passed all six integration tests in `1.41s` at code/test head `2c1c1d39c44b77803f587785f07f741f8374ef29` with exact ephemeral cleanup and no production change; independent five-axis review is `PASS` and fresh Required Checks are `12/12`, while PR #330 remains open/unmerged;
- the real-backend Chromium harness for sufficient/insufficient input, review, Markdown downloads and reload persistence; P4A reconciled its locators against the merged Chinese single-page UI and P4B records the historical predecessor rehearsal;
- private local-demo composition plus `scripts/mvp0/demo` foreground API/Web lifecycle and non-destructive PostgreSQL stale-container repair.

The DeepSeek offline implementation landed at `main@c12a9ab285eefee35c78342fd01180c1e47a83f0`. The release path still uses loopback only, keeps PostgreSQL separate from API/Web child cleanup, and does not select any live Provider runtime.

## 3. FL-1 and FL-2 status

FL-1 is complete on the deterministic scripted path:

- Task create → primary input → deterministic result → bounded review/confirmation → two Markdown exports is implemented;
- sufficient Anchor SKU input produces all required result groups;
- representative insufficient input remains honest and exposes no review/export actions;
- current Task/input/result state survives reload and stable deep-link return;
- the inherited real-backend Chromium harness is deterministic and provider-free; P4B records independently reviewed `P4_LOCAL_RELEASE_ACCEPTED` after the reviewed-main rehearsal, completing the accepted P4 local scope.

The superseded OpenAI and Qwen provider-specific offline seams, direct tests and live handoffs are removed by the bounded cleanup; `openai==2.53.0` remains because the current DeepSeek adapter consumes it. PR #271 adds the current direct DeepSeek official `deepseek-v4-pro` private adapter and opt-in Task-to-export smoke seam. The first authorized run at `main@1c7c2107ead332235d492ed063b67101784d35f1` completed five calls with `retry_count=0` / `recovery_count=0` and failed safely before `awaiting_review`; its fifth Xiaohongshu-v1 call recorded 12,288 output tokens and 136,622 ms latency against the historical 120 s timeout. The second authorized run under #281 at exact `main@ac4edfed6e8e216e9938affdc734298c8630d2de` stopped after one `product_intake_v1 / v1` call with fixed safe HTTP 500 before `awaiting_review`; safe metadata records input 2,353 / output 8,192 / total 10,545 tokens and 106,434 ms latency, retry/recovery 0/0, all behavior gates false and no stage 2～5 call. The 8,192 output equals the accepted first-stage ceiling, but this is only a diagnostic lead because evidence excludes raw content, reasoning, traceback, finish reason and internal error category. Cleanup completed after both bounded executions. No Provider acceptance is claimed; #281 authorization is consumed and closed, no further Provider run is authorized, and the historical Fast Lane Goal remains `GOAL_BLOCKED`.

DEC-081 Phase A is complete: its deterministic, red-capable offline diagnosis of the exact first-stage boundary produced `INSUFFICIENT_SANITIZED_EVIDENCE` because the retained safe signature was compatible with multiple actual mapper/schema/domain-admission rejection boundaries. It did not identify historical causation, did not modify production behavior and did not create a Phase B contract. Any future Phase B would require independent `ORCHESTRATOR_REVIEWER` review and a new exact bounded repair contract; `rejection_disposition` remains a Proposal only.

## 4. FL-3 release reconciliation

Issue #257 completed the smallest release/operator reconciliation:

- `./scripts/mvp0/demo` starts/reconciles only the fixed local PostgreSQL service, applies the existing Business Alembic head, and starts API/Web on `127.0.0.1:8000`/`127.0.0.1:5173`;
- Ctrl-C/TERM reaps only API/Web children; `./scripts/mvp0/down` stops PostgreSQL while preserving its named volume;
- current README, Web README, AGENTS and this handoff describe implemented code without claiming live-provider success;
- fresh-clone rehearsal records lockfile installs, host preflight, browser normal/insufficient/review/download/reload evidence and cleanup; P4A adds only the offline ephemeral lifecycle proof and preserves the prior terminal strict-mode rehearsal evidence.

No public HTTP/OpenAPI/Web behavior, migration/schema/dependency/Compose topology, Worker, Provider or deployment boundary was expanded by FL-3.

### P4A Issue #308

P4A is provider-free and merged/current. The reviewed lifecycle uses a repository-prefixed ephemeral Compose project and paired temporary Postgres volume while preserving the exact default project `ai-ecommerce-agent-mvp0` and persistent volume `ai-ecommerce-agent-mvp0-postgres-data`; offline fake-Docker lifecycle/static proofs cover fail-closed preflight, error/signal cleanup and default-volume protection. The real-backend spec was reconciled source-first to current semantic role/type locators, including `getByRole("textbox", { name: "粘贴文本" })`, with `/tasks/:taskId` query deep links preserved.

The single authorized terminal browser rehearsal before the P4A hard freeze ran one retained foreground demo session, reached the browser URL, and failed all three real-backend tests in strict mode because `getByLabel("粘贴文本")` matched both a radio and textarea. One Ctrl-C returned 130; owned containers/network/ephemeral volume were absent afterward, ports 8000/5173/55432 were free, and the protected default-volume identity was unchanged. The exact historical disposition is `BLOCKED_REAL_REHEARSAL_LOCATOR_STRICT_MODE`; P4B supersedes it for current reviewed-main acceptance.

### P4B Issue #310

P4B ran once from exact reviewed main and passed three fictional-data cases with exact ephemeral cleanup; its truthful predecessor result is independently reviewed `P4_LOCAL_RELEASE_ACCEPTED`, provider-free. Issue #318 is the separate L1 real Needs Input/Recovery acceptance; its exact 6/6 backend and 4/4 browser runtime gates passed and are recorded in [the L1 review](../reviews/mvp0l-l1-needs-input-backend.md), with independent five-axis review `PASS` and PR #328 merged/current. Issue #329 / PR #330 is the active L2 minimum persistence characterization; its one-time provider-free six-test runtime passed in `1.41s` on an isolated ephemeral scope at code/test head `2c1c1d39c44b77803f587785f07f741f8374ef29`, its independent five-axis review is `PASS`, and fresh Required Checks are `12/12`. PR #330 remains `OPEN`/unmerged, so L2 is not merge-effective and L3 remains gated. P5 docs/research is independently reviewed as `P5_REUSE_FROZEN`; direct reuse and platform behavior remain frozen and unauthorized. PR #315 made `MVP0P_GOAL_COMPLETE` merge-effective historical truth, and PR #317 made L0 current.

## 5. Deferred and non-blocking

The following are outside the current productization Stage unless a later Stage contract gives them a real consumer:

- unresolved old tracking parents or proposals that only govern deferred Source/Review lifecycle;
- Issue #190 completion participant and the complete distributed Commit Fence;
- full Worker lease/fencing, durable checkpoint recovery and seven-action reconciliation;
- JSON/CSV/PDF/image intake and full parser/fragment/retrieval/evidence runtime;
- Embedding, semantic/hybrid retrieval and retrieval evaluation;
- Source remove/replace, partial rerun and full cancellation/recovery UX;
- autosave/diff/stale-draft recovery and multiple Review outcomes;
- complete OpenAPI operation catalog when no productization UI consumes the operation;
- Login, RBAC, multi-tenancy, public deployment, generic compliance and telemetry platforms.

Accepted future designs remain available for a later Goal. They are not implementation prerequisites for this one.

DEC-082 supplies the accepted product and frontend baseline. DEC-083's P0–P5 predecessor execution is complete; PR #315 made `MVP0P_GOAL_COMPLETE` current historical truth. DEC-084 sequences the successor as L0 → L1 → L2 → L3 → L4 → L5 → L6; L0 is active after PR #317, L1 is merged/current through PR #328, and Issue #329 / PR #330 is the active L2 implementation/review Stage with code/test `PASS`, independent review `PASS` and checks `12/12`, while PR #330 remains open/unmerged. The owner-confirmed MBL-first sequence remains L2 → L3 → L4 → L5 → Agent UI → L6. Important frontend work uses applicable taste skills; local Kimi Code + Kimi K3 remains a narrow later exact-contract exception, not an L0/L2 call or Luna / Terra fallback. PR #299 is open / unmerged and is not production evidence.

## 6. Quality readiness

The project already has sufficient tools: Ruff, Pyright, Import Linter, pytest, OpenAPI validation, Prettier, ESLint, TypeScript, Vitest, Playwright Chromium, build checks, dependency audit and Secret scanning.

FL-1 uses them proportionally:

- affected tests and static checks locally;
- CI as the global regression safety net;
- one representative normal path, one primary recoverable error and one critical invariant per changed boundary;
- no new private-module AST scanner, exact file inventory or recursive every-field matrix without a reproduced risk;
- real PostgreSQL only when the vertical changes persistence;
- deterministic model substitute for ordinary PRs;
- bounded real-provider evidence only at FL-2; the two authorized runs are terminal failures and no further run is authorized;
- Phase A offline diagnosis uses synthetic / fictional sanitized fixtures only and cannot silently become a Provider test matrix.

See the concise [Testing Strategy](../development/testing-strategy.md).

## 7. Security readiness

Required boundaries are already decided: fixed workspace, loopback same-origin, external-input limits, Task scope, parameterized SQL, atomic current-result persistence, React/Markdown safety, mutation idempotency, Secret/provider-payload isolation and safe errors.

No authentication, RBAC, tenant or public-internet threat model is required for the local MVP. A future deployment Goal must reopen those boundaries.

## 8. Human gates and stop conditions

Stop and request user direction only for:

- a new user-visible product behavior outside the active L Stage contract;
- destructive migration or existing-data rewrite;
- public deployment, real user data, any future Provider call or irreversible external action;
- credible Secret exposure or loss of Task/scope/atomic-result guarantees;
- replacement of accepted PostgreSQL, current DeepSeek FL-2 Provider, React/Vite, FastAPI or `luna-worker` boundaries;
- an allegedly necessary infrastructure slice with no concrete Stage consumer;
- any Spider_XHS reuse, clone, install, Cookie/login, proxy, signature, platform request or publishing behavior; P5 is independently reviewed `P5_REUSE_FROZEN` and remains unauthorized;
- any expansion to Intel support (Deferred; excluded from the first release), native App/WebView, signing/notarization, login/RBAC/multi-user/public deployment, real product/customer data or macOS Keychain/Secret UI;

Reversible local implementation choices do not require a new Decision. Record them in the Issue or PR.

## 9. Execution status

```text
FL-0 Planning rebaseline: COMPLETE
FL-1 Deterministic vertical loop: COMPLETE (merged PRs #250/#252/#254)
FL-2 DeepSeek provider amendment: ACCEPTED (Issue #268 / PR #269)
FL-2 DeepSeek adapter/smoke seam: IMPLEMENTED_OFFLINE_NOT_LIVE_VERIFIED (Issue #270 / PR #271)
FL-2 DeepSeek live proof: TERMINAL GOAL_BLOCKED (first run failed after five calls; second #281 run failed after one Product Intake call; no further Provider run authorized)
FL-2 bounded repair: MERGED_OFFLINE (PR #280 / Issue #277 / DEC-080)
FL-2 first-stage offline diagnosis: COMPLETED_INSUFFICIENT_SANITIZED_EVIDENCE (DEC-081; observational ambiguity only; no production repair or Phase B contract)
FL-3 one-command local demo rehearsal: COMPLETE (Issue #257)
Post-FL-2 bounded legacy cleanup: COMPLETE (Issue #274; the historical Fast Lane Goal remains `GOAL_BLOCKED`)
Qwen Token Plan supplemental live: BLOCKED_BY_PROVIDER_TERMS (Issue #264)
Predecessor MVP0P Goal activation/current-truth reconciliation: COMPLETE (Issue #301; exact eight-file allowlist; historical)
P1 Action Home and A+C production shell: MERGED_CURRENT (Issue #303 / PR #304)
P2 Core TaskWorkbench states: MERGED_CURRENT (Issue #305 / PR #306)
P3 Needs Input and essential recovery: MERGED_CURRENT (Issue #247)
P4A local release lifecycle and harness reconciliation: MERGED_CURRENT (Issue #308; historical `BLOCKED_REAL_REHEARSAL_LOCATOR_STRICT_MODE` preserved)
P4B reviewed-main deterministic local release acceptance: P4_LOCAL_RELEASE_ACCEPTED (Issue #310; provider-free; independently reviewed; accepted P4 local scope complete; exact cleanup passed; no real Needs Input/Recovery backend claim)
P5 Spider_XHS feasibility Gate: `P5_REUSE_FROZEN` independently reviewed / P5 docs-research complete ([research report](../reviews/mvp0-spider-xhs-feasibility.md)); direct reuse/platform/publishing behavior remains frozen and unauthorized
Predecessor Final Goal Review: `FINAL_GOAL_REVIEW_PASS` merged in PR #315; `MVP0P_GOAL_COMPLETE` is current historical truth
Successor MVP-0L L0 activation: `ACTIVE` after PR #317 merged Issue #316's exact nine-path docs-only contract
Successor MVP-0L L1 Needs Input backend: `MERGED_CURRENT_REVIEW_PASS` (Issue #318 / PR #328; additive 0009 + existing Web consumer; 6/6 backend + 4/4 browser; no Provider/Secret)
Successor MVP-0L L2 minimum persistence: `REVIEW_PASS_PR_OPEN` (Issue #329 / PR #330; code/test head `2c1c1d39c44b77803f587785f07f741f8374ef29`; six-test provider-free runtime `6/6 in 1.41s`; stale revision/idempotency resolution test-only; independent five-axis `PASS`; fresh Required Checks `12/12`; PR open/unmerged; L2 not merge-effective until reviewed closure reaches `main`; L3 gated)
Successor Stage order: L0 → L1 → L2 → L3 → L4 → L5 → L6; only one active Stage; next Issue after prior independently reviewed PR reaches `main`
```
