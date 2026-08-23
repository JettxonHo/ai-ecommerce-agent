# MVP-0P Local Action Workbench Productization Goal

> **Status: ACTIVE — P0 complete; Issue #303 / PR #304 P1 shell merged/current; Issue #305 / PR #306 P2 merged/current; reconciled Issue #247 P3 implementation active and merge-conditional; P4 gated**
>
> **Decision authority:** [DEC-083](../decisions/dec-083-local-action-workbench-productization-goal.md) · [Session-008](../sessions/session-008-local-productization-goal-activation.md) · [Issue #301](https://github.com/JettxonHo/ai-ecommerce-agent/issues/301)
>
> **Successor of:** [MVP-0 Fast Lane Goal](mvp0-fast-lane-goal.md), which remains a terminal `GOAL_BLOCKED` historical record. Its two DeepSeek failures, [DEC-081](../decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) ambiguity and no-Provider-acceptance truth are preserved.

## 1. Goal outcome

Turn the accepted deterministic local foundation into one understandable, recoverable and exportable single-user Action Workbench for a small ecommerce operator. The product remains a fixed local workspace with no login, tenant selector or public deployment. The productization Goal does not require Provider acceptance and does not reopen the terminal DeepSeek Gate.

The accepted human A+C selection is the design baseline. `HUMAN_SELECTED_AC_BASELINE` means that the product should expose Chinese task identity and stable business/status reading order, a wide-desktop horizontal five-stage rail, one dominant current action, progressive disclosure and a Context Rail, while retaining the four business states, 1024/320 reflow, focus/reduced-motion behavior and raw JSON behind technical details. [PR #299](https://github.com/JettxonHo/ai-ecommerce-agent/pull/299) remains open and unmerged; Issue #303 / [PR #304](https://github.com/JettxonHo/ai-ecommerce-agent/pull/304) is the merged/current P1 shell. Issue #305 / [PR #306](https://github.com/JettxonHo/ai-ecommerce-agent/pull/306) is the merged/current P2 implementation. Reconciled Issue #247 carries the P3 implementation and is repository-current only with its eventual merge commit. No ignored prototype is promoted by this Goal.

## 2. Frozen Stage order and operating rule

The exact Stage order is **P0 → P1 → P2 → P3 → P4 → P5**.

- Only one implementation Stage may be active at a time.
- P1 became current when Issue #303 / PR #304 was independently reviewed and merged. Issue #305 / PR #306 is independently reviewed and merged/current as P2.
- Reconciled [Issue #247](https://github.com/JettxonHo/ai-ecommerce-agent/issues/247) is the single P3 implementation record; its product result is repository-current only in a checkout containing the eventual merge commit.
- P4 remains gated until P3 is independently reviewed and merged; no P4 implementation or real-backend Needs Input claim is authorized by this record.
- Create the next implementation Issue only after the previous Stage's PR is independently reviewed and merged.
- Do not create all implementation Issues up front; each Issue must have a real, immediately observable consumer.
- Ordinary reversible local repository, test, branch and PR work is standing-authorized inside the active Issue contract. That access does not override Secret / Provider / platform gates, destructive-action controls, public-contract or migration gates, independent Review, or the exact implementation-agent rule.

## 3. Stages

### P0 — Goal activation and current-truth reconciliation

**Owner / result:** Issue #301, docs-only. The result is one current productization entry point and a truthful historical Fast Lane record.

The P0 allowlist is exactly:

1. `AGENTS.md`
2. `README.md`
3. `docs/decisions/dec-083-local-action-workbench-productization-goal.md`
4. `docs/decisions/decision-log.md`
5. `docs/goals/mvp0-fast-lane-goal.md`
6. `docs/goals/mvp0-local-action-workbench-productization-goal.md`
7. `docs/handoffs/implementation-readiness.md`
8. `docs/sessions/session-008-local-productization-goal-activation.md`

P0 changes no code, test, configuration, dependency, lockfile, migration, OpenAPI, Web implementation, Provider, model, Secret or platform behavior. It records [DEC-083](../decisions/dec-083-local-action-workbench-productization-goal.md) as Accepted, marks this Goal as the successor active productization entry after merge, marks the old Fast Lane Goal terminal `GOAL_BLOCKED`, and links Decision ↔ Goal ↔ Session in both directions.

### P1 — Action Home and A+C production shell

Implement the Chinese-first `/tasks` Action Home, Task identity / header, wide-desktop horizontal five-stage rail, one Active Workspace and responsive `320–360px` Context Rail. Around 1024px the rail becomes in-flow disclosure; true 320 CSS-px reflow must not create page-level horizontal overflow. Preserve current generated client, Task gateway and data behavior. No backend or public-contract change is in scope.

Material frontend work uses the applicable taste skills and carries representative visual / accessibility evidence. The human A+C choice guides the implementation but does not waive the exact Stage contract or independent Review.

### P2 — Core TaskWorkbench states

Productize the current backend behavior into three product states: Running, Review and Results. Use structured business groups and one dominant action; keep Marketing and Xiaohongshu Results as separate views; provide safe Markdown preview / export and progressive technical disclosure for raw JSON. Preserve focus, reduced motion and 1280 / 1024 / 320 reflow boundaries.

### P3 — Needs Input and essential recovery

Reconcile and reuse [Issue #247](https://github.com/JettxonHo/ai-ecommerce-agent/issues/247); do not create a duplicate Needs Input Issue. The reconciled delivery is one private generated-client/deterministic gateway, one Chinese-first bounded action workspace and one bounded failed/paused Recovery workspace. P3 is repository-current only with the eventual independently reviewed merge commit. The current FastAPI task resource still projects `needsInputRequest: null` and does not implement the Needs Input read/resolve resource, so this P3 frontend/deterministic evidence does not claim real browser-to-FastAPI completion. Public-contract, persistence or migration changes remain stop conditions unless separately accepted.

### P4 — Deterministic local release acceptance

Run the real browser → FastAPI → PostgreSQL deterministic path with fictional data, the one-command local demo, current exports and representative recovery. Complete the independent correctness / readability / architecture / security / performance Review and Goal Review. P4 does not call a live model, Provider, Xiaohongshu platform or external publishing service; the accepted scripted substitute and existing local evidence remain the boundary.

### P5 — Spider_XHS conditional feasibility Gate

P5 is a conditional feasibility candidate and begins as docs / research only. Audit an exact upstream commit, license and commercial-use permission, the Xiaohongshu platform terms and risk, Cookie / Secret handling, dependencies / security and a proposed narrow read-only research seam. The candidate's audited tree currently has no detected LICENSE while its README has conflicting MIT-badge and non-commercial wording; no reuse permission is inferred.

Until a separate positive Gate exists, P5 prohibits code copying or reuse, clone, vendoring or dependency installation, Cookie / login, proxy, fingerprint / signature execution, Xiaohongshu requests, scraping and publishing. If the Gate is rejected or frozen, the local product Goal may still complete. Publishing is outside this Goal.

## 4. Product boundary

### In scope

- Fixed local single-user workspace with `/tasks` as an action home, not a Dashboard.
- Existing Task creation, stable deep links, deterministic pipeline, Review, Results and Markdown export, expressed through the A+C workbench hierarchy.
- Existing Current Truth, generated client, same-origin transport, safe Markdown projection, Task scope, idempotency and local persistence boundaries.
- A readable Chinese five-stage progress rail: 资料整理 → 用户洞察 → 商品定位 → 营销 Brief → 小红书 Brief.
- Context, evidence, limits, risk and technical details behind progressive disclosure rather than raw JSON as the primary surface.

### Explicitly out of scope

- Any new Provider, model, live call, Secret access, platform request or automatic publishing.
- Login, RBAC, tenant switching, public deployment, Dashboard charts, global search, advanced filters, bulk operations, sales / order / logistics / payment modules or a mobile-specific product.
- Public API, OpenAPI, migration, database topology, dependency / lockfile change or backend behavior change in P0 / P1 unless a later accepted Stage contract explicitly permits it.
- Reopening DeepSeek diagnosis, `rejection_disposition`, DEC-081 Phase B, the two consumed smoke authorizations or any production repair inferred from their token metadata.
- Open Dependabot work and unrelated historical Issues; they are not staged productization work.

## 5. Evidence and acceptance

Each Stage PR must state its Problem, Solution, Scope, Validation, Risk, Rollback and documentation impact, then receive independent review. Evidence is proportional under [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md): representative normal behavior, the primary recoverable path and critical invariants, with Required Checks as the global regression gate.

The Goal is complete only when:

- P0 has merged and the repository has one active productization entry plus one terminal Fast Lane history;
- P1–P3 have independently reviewed and merged their observable local product results;
- P4 demonstrates the deterministic local browser-to-export path and completes Goal Review without any live Provider call;
- P5 has an explicit feasibility disposition (accepted narrow research seam, or rejected / frozen with reasons and no reuse); and
- no Critical or Blocking defect remains within the accepted local scope, while Provider acceptance is still not claimed.

## 6. Agent routing and human gates

The main development session coordinates this Goal. Executable code is routed to the exact custom `luna-worker` under [DEC-071](../decisions/dec-071-luna-worker-exclusive-implementation-routing.md) and [DEC-072](../decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md), with configuration evidence and runtime identity recorded separately. The implementation Agent cannot approve or merge its own PR.

The DEC-082 Kimi Code + Kimi K3 exception remains limited to a later user-accepted exact frontend contract; this P0 Goal activation does not call Kimi. Terra is not an automatic fallback. Provider, platform, Secret, destructive, public-contract, migration, dependency and product-direction gates remain human-controlled.

## 7. Current limitations and risks

- The deterministic foundation is useful local evidence, not live Provider acceptance.
- Human selection of A+C is a design baseline; Issue #303 / PR #304 is the merged/current P1 implementation. Issue #305 / PR #306 is the merged/current P2 implementation. Issue #247 is the reconciled P3 implementation record and is merge-conditional; P4 remains gated on independent P3 review/merge.
- Spider_XHS licensing and platform behavior are unresolved and intentionally isolated to P5.
- Staged execution may leave later work pending; that is preferable to manufacturing parallel Issues without a consumer or bypassing a gate.

## 8. Related records

- Decision: [DEC-083](../decisions/dec-083-local-action-workbench-productization-goal.md)
- Historical Goal: [MVP-0 Fast Lane Goal](mvp0-fast-lane-goal.md)
- Session: [Session-008](../sessions/session-008-local-productization-goal-activation.md)
- Human A+C verdict: [Issue #300 comment 5386010673](https://github.com/JettxonHo/ai-ecommerce-agent/issues/300#issuecomment-5386010673)
- Activation Issue: [Issue #301](https://github.com/JettxonHo/ai-ecommerce-agent/issues/301)
- Reconciled P3 implementation record: [Issue #247](https://github.com/JettxonHo/ai-ecommerce-agent/issues/247)
