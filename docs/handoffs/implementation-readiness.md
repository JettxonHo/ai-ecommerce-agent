# Implementation Readiness

> **Status: MVP-0 Fast Lane `GOAL_BLOCKED` · FL-1 FOUNDATION COMPLETE · PHASE A TERMINAL `INSUFFICIENT_SANITIZED_EVIDENCE` · NO PRODUCTION REPAIR OR PHASE B CONTRACT**
>
> **Authority:** [DEC-078](../decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md) · [DEC-079](../decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md) · [DEC-081](../decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) · [MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md)
>
> **Current release boundary:** the deterministic local loop and one-command demo are implemented as the accepted FL-1 foundation, not the complete Fast Lane MVP. [PR #271](https://github.com/JettxonHo/ai-ecommerce-agent/pull/271) completed the private DeepSeek adapter, local Schema / bounded Domain admission and opt-in smoke seam at merge commit `c12a9ab285eefee35c78342fd01180c1e47a83f0`; [PR #280](https://github.com/JettxonHo/ai-ecommerce-agent/pull/280) merged the DEC-080 Xiaohongshu v2 deadline-fence repair offline; [Issue #274](https://github.com/JettxonHo/ai-ecommerce-agent/issues/274) completed the single bounded post-FL-2 cleanup. The first smoke at `main@1c7c2107ead332235d492ed063b67101784d35f1` failed after five calls. The second smoke under [Issue #281](https://github.com/JettxonHo/ai-ecommerce-agent/issues/281) ran at exact `main@ac4edfed6e8e216e9938affdc734298c8630d2de` and failed safely after one `product_intake_v1 / v1` call, before `awaiting_review`; retry/recovery were 0/0, all behavior gates were false and no stage 2～5 call occurred. FL-2 is terminal `GOAL_BLOCKED`; #281 authorization is consumed and closed, with no further Provider run authorized. DEC-081 Phase A is complete with terminal disposition `INSUFFICIENT_SANITIZED_EVIDENCE`; its offline seam establishes observational ambiguity across actual mapper/schema/domain-admission boundaries and does not identify the historical cause. No production repair was made and no Phase B contract exists. `rejection_disposition` remains a Proposal only, not Accepted/current truth.

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

No further Persona, RFC, general architecture, retrieval or enterprise-security planning is required for the deterministic foundation. The two controlled DeepSeek runs are terminal failure evidence, not Provider acceptance; #281 is closed and no further Provider run is authorized. Phase A is complete with terminal `INSUFFICIENT_SANITIZED_EVIDENCE`, establishing observational ambiguity only; no production repair or Phase B contract exists, and `rejection_disposition` remains a Proposal only. Later deferred capabilities retain their separate gates.

## 2. Implemented foundation at the current Fast Lane baseline

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
- representative real-backend Chromium coverage for sufficient/insufficient input, review, Markdown downloads and reload persistence;
- private local-demo composition plus `scripts/mvp0/demo` foreground API/Web lifecycle and non-destructive PostgreSQL stale-container repair.

The DeepSeek offline implementation landed at `main@c12a9ab285eefee35c78342fd01180c1e47a83f0`. The release path still uses loopback only, keeps PostgreSQL separate from API/Web child cleanup, and does not select any live Provider runtime.

## 3. FL-1 and FL-2 status

FL-1 is complete on the deterministic scripted path:

- Task create → primary input → deterministic result → bounded review/confirmation → two Markdown exports is implemented;
- sufficient Anchor SKU input produces all required result groups;
- representative insufficient input remains honest and exposes no review/export actions;
- current Task/input/result state survives reload and stable deep-link return;
- real-backend Chromium evidence is deterministic and provider-free.

The superseded OpenAI and Qwen provider-specific offline seams, direct tests and live handoffs are removed by the bounded cleanup; `openai==2.53.0` remains because the current DeepSeek adapter consumes it. PR #271 adds the current direct DeepSeek official `deepseek-v4-pro` private adapter and opt-in Task-to-export smoke seam. The first authorized run at `main@1c7c2107ead332235d492ed063b67101784d35f1` completed five calls with `retry_count=0` / `recovery_count=0` and failed safely before `awaiting_review`; its fifth Xiaohongshu-v1 call recorded 12,288 output tokens and 136,622 ms latency against the historical 120 s timeout. The second authorized run under #281 at exact `main@ac4edfed6e8e216e9938affdc734298c8630d2de` stopped after one `product_intake_v1 / v1` call with fixed safe HTTP 500 before `awaiting_review`; safe metadata records input 2,353 / output 8,192 / total 10,545 tokens and 106,434 ms latency, retry/recovery 0/0, all behavior gates false and no stage 2～5 call. The 8,192 output equals the accepted first-stage ceiling, but this is only a diagnostic lead because evidence excludes raw content, reasoning, traceback, finish reason and internal error category. Cleanup completed after both bounded executions. No Provider acceptance is claimed; #281 authorization is consumed and closed, no further Provider run is authorized, and Goal remains `GOAL_BLOCKED`.

DEC-081 Phase A is complete: its deterministic, red-capable offline diagnosis of the exact first-stage boundary produced `INSUFFICIENT_SANITIZED_EVIDENCE` because the retained safe signature was compatible with multiple actual mapper/schema/domain-admission rejection boundaries. It did not identify historical causation, did not modify production behavior and did not create a Phase B contract. Any future Phase B would require independent `ORCHESTRATOR_REVIEWER` review and a new exact bounded repair contract; `rejection_disposition` remains a Proposal only.

## 4. FL-3 release reconciliation

Issue #257 completed the smallest release/operator reconciliation:

- `./scripts/mvp0/demo` starts/reconciles only the fixed local PostgreSQL service, applies the existing Business Alembic head, and starts API/Web on `127.0.0.1:8000`/`127.0.0.1:5173`;
- Ctrl-C/TERM reaps only API/Web children; `./scripts/mvp0/down` stops PostgreSQL while preserving its named volume;
- current README, Web README, AGENTS and this handoff describe implemented code without claiming live-provider success;
- fresh-clone rehearsal records lockfile installs, host preflight, browser normal/insufficient/review/download/reload evidence and cleanup.

No public HTTP/OpenAPI/Web behavior, migration/schema/dependency/Compose topology, Worker, Provider or deployment boundary was expanded by FL-3.

## 5. Deferred and non-blocking

The following do not block Fast Lane readiness:

- unresolved old tracking parents or proposals that only govern deferred Source/Review lifecycle;
- Issue #190 completion participant and the complete distributed Commit Fence;
- full Worker lease/fencing, durable checkpoint recovery and seven-action reconciliation;
- JSON/CSV/PDF/image intake and full parser/fragment/retrieval/evidence runtime;
- Embedding, semantic/hybrid retrieval and retrieval evaluation;
- Source remove/replace, partial rerun and full cancellation/recovery UX;
- autosave/diff/stale-draft recovery and multiple Review outcomes;
- complete OpenAPI operation catalog when no Fast Lane UI consumes the operation;
- Login, RBAC, multi-tenancy, public deployment, generic compliance and telemetry platforms.

Accepted future designs remain available for a later Goal. They are not implementation prerequisites for this one.

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

- a new user-visible product behavior outside the Fast Lane Goal;
- destructive migration or existing-data rewrite;
- public deployment, real user data, any future Provider call or irreversible external action;
- credible Secret exposure or loss of Task/scope/atomic-result guarantees;
- replacement of accepted PostgreSQL, current DeepSeek FL-2 Provider, React/Vite, FastAPI or `luna-worker` boundaries;
- an allegedly necessary infrastructure slice with no concrete Fast Lane consumer.

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
Post-FL-2 bounded legacy cleanup: COMPLETE (Issue #274; Goal remains GOAL_BLOCKED)
Qwen Token Plan supplemental live: BLOCKED_BY_PROVIDER_TERMS (Issue #264)
```
