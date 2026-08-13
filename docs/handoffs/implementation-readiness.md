# Implementation Readiness

> **Status: FL-1 COMPLETE · FL-3 COMPLETE · FL-2 DEEPSEEK IMPLEMENTATION/PROOF PENDING**
>
> **Authority:** [DEC-078](../decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md) · [DEC-079](../decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md) · [MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md)
>
> **Current release boundary:** the deterministic local loop and one-command demo are implemented. Issue #268 owns the documentation-first provider amendment; the subsequent implementation Issue must add the private DeepSeek seam before a separately authorized one-Task/five-call smoke. Issue #255 is superseded after this amendment merges. Issue #264 is `BLOCKED_BY_PROVIDER_TERMS` and must not run.

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
- one opt-in direct DeepSeek official `deepseek-v4-pro` smoke after deterministic acceptance and independent adapter review.

No further Persona, RFC, general architecture, retrieval or enterprise-security planning is required for the deterministic Fast Lane release; FL-2 live proof and later deferred capabilities retain their separate gates.

## 2. Implemented foundation at the current Fast Lane baseline

Implemented or physically present:

- repository, Python package, TypeScript application and CI foundations;
- local PostgreSQL lifecycle and compatibility evidence;
- Task / Run / Stage and Source persistence components;
- bounded Durable Dispatch, checkpoint and runtime diagnostic seams;
- provider-neutral Model Runtime, scripted substitute, OpenAI Responses transport pieces and an offline-only Qwen Token Plan adapter;
- private output contracts for Facts, Insight, Positioning, Marketing Brief and Xiaohongshu mapping;
- Marketing / Xiaohongshu domain snapshots and safe Markdown renderer;
- authored OpenAPI and generated TypeScript client;
- FastAPI fixed-workspace foundation;
- Task gateway, recent/create/read routes, Task-scoped input/result/review/export routes and stable deep links;
- deterministic scripted Facts → Insight → Positioning → Marketing Brief → Xiaohongshu pipeline;
- Workbench projection and TaskWorkbench intake/progress/review/results/export UI;
- representative real-backend Chromium coverage for sufficient/insufficient input, review, Markdown downloads and reload persistence;
- private local-demo composition plus `scripts/mvp0/demo` foreground API/Web lifecycle and non-destructive PostgreSQL stale-container repair.

The current provider-amendment baseline is `main@1469eefe6db75ceee949b2c7431df5ac06a25f40`. The release path still uses loopback only, keeps PostgreSQL separate from API/Web child cleanup, and does not select any live Provider runtime.

## 3. FL-1 and FL-2 status

FL-1 is complete on the deterministic scripted path:

- Task create → primary input → deterministic result → bounded review/confirmation → two Markdown exports is implemented;
- sufficient Anchor SKU input produces all required result groups;
- representative insufficient input remains honest and exposes no review/export actions;
- current Task/input/result state survives reload and stable deep-link return;
- real-backend Chromium evidence is deterministic and provider-free.

The former OpenAI FL-2 runtime/smoke seam and the supplemental Qwen offline seam are merged, but no OpenAI, Qwen or DeepSeek call, Secret-backed run or live acceptance result is claimed. DEC-079 replaces the remaining OpenAI Gate with direct DeepSeek official `deepseek-v4-pro`. The DeepSeek adapter/smoke seam is not yet implemented; the live Gate remains separately blocked on exact-head review and user authorization.

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
- one real-provider smoke only at FL-2.

See the concise [Testing Strategy](../development/testing-strategy.md).

## 7. Security readiness

Required boundaries are already decided: fixed workspace, loopback same-origin, external-input limits, Task scope, parameterized SQL, atomic current-result persistence, React/Markdown safety, mutation idempotency, Secret/provider-payload isolation and safe errors.

No authentication, RBAC, tenant or public-internet threat model is required for the local MVP. A future deployment Goal must reopen those boundaries.

## 8. Human gates and stop conditions

Stop and request user direction only for:

- a new user-visible product behavior outside the Fast Lane Goal;
- destructive migration or existing-data rewrite;
- public deployment, real user data, additional paid provider or irreversible external action;
- credible Secret exposure or loss of Task/scope/atomic-result guarantees;
- replacement of accepted PostgreSQL, current DeepSeek FL-2 Provider, React/Vite, FastAPI or `luna-worker` boundaries;
- an allegedly necessary infrastructure slice with no concrete Fast Lane consumer.

Reversible local implementation choices do not require a new Decision. Record them in the Issue or PR.

## 9. Execution status

```text
FL-0 Planning rebaseline: COMPLETE
FL-1 Deterministic vertical loop: COMPLETE (merged PRs #250/#252/#254)
FL-2 DeepSeek provider amendment: ACCEPTED; documentation sync ACTIVE (Issue #268)
FL-2 DeepSeek adapter/smoke seam: NOT STARTED; live proof PENDING SEPARATE HUMAN GATE
FL-3 Release reconciliation: COMPLETE (Issue #257)
Qwen Token Plan supplemental live: BLOCKED_BY_PROVIDER_TERMS (Issue #264)
```
