# Implementation Readiness

> **Status: READY FOR MVP-0 FAST LANE**
>
> **Authority:** [DEC-078](../decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md) · [MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md)
>
> **Activation:** the Fast Lane becomes the sole remaining MVP-0 execution path when the DEC-078 documentation PR merges. The first business-code action is a new FL-1 vertical Issue, not continuation of the old horizontal backlog.

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
- one opt-in real OpenAI smoke after deterministic acceptance.

No further Persona, RFC, general architecture, retrieval or enterprise-security planning is required before FL-1.

## 2. Implemented foundation at the DEC-078 accepted baseline

Implemented or physically present:

- repository, Python package, TypeScript application and CI foundations;
- local PostgreSQL lifecycle and compatibility evidence;
- Task / Run / Stage and Source persistence components;
- bounded Durable Dispatch, checkpoint and runtime diagnostic seams;
- provider-neutral Model Runtime, scripted substitute and OpenAI Responses transport pieces;
- private output contracts for Facts, Insight, Positioning, Marketing Brief and Xiaohongshu mapping;
- Marketing / Xiaohongshu domain snapshots and safe Markdown renderer;
- authored OpenAPI and generated TypeScript client;
- FastAPI fixed-workspace foundation;
- Task gateway, recent/create/read routes, stable deep links, Workbench projection and TaskWorkbench progress shell.

The accepted Fast Lane baseline is `main@371ea0c15546b91ee10fcde8622553b164e5740c`. Refresh `main` again before creating FL-1. A Web shell or projection does not count as a backend business loop.

## 3. Missing vertical path

The project is not yet an end-to-end product because:

- FastAPI registers no Task/input/workflow/review/export business routes;
- no user input endpoint persists pasted text or TXT/Markdown for the Fast Lane path;
- the five business outputs are contracts, not a composed deterministic workflow;
- no real backend result is consumed by Review and export UI;
- no browser E2E traverses real backend components from Task create to Markdown export;
- no accepted live-provider evidence exists for that completed path.

These missing links, rather than completion of every designed subsystem, define FL-1 and FL-2.

## 4. Authorized FL-1 scope

The first implementation may:

- add the minimal input contract, handler and Task-scoped persistence needed for one pasted text or one UTF-8 TXT/Markdown file up to 1 MiB;
- register real Task/read/input routes in the existing FastAPI composition root;
- compose existing contracts and the scripted runtime into one in-process deterministic pipeline;
- persist and project the current Marketing and Xiaohongshu results atomically;
- add one bounded review/correction/confirm interaction and Markdown download;
- adjust authored OpenAPI/generated client only for operations actually consumed by this path;
- use a small additive migration when required by the vertical, with normal migration review.

Prefer no more than three Issues: input/routes, pipeline/results, review/export.

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
- replacement of accepted PostgreSQL, OpenAI, React/Vite, FastAPI or `luna-worker` boundaries;
- an allegedly necessary infrastructure slice with no concrete Fast Lane consumer.

Reversible local implementation choices do not require a new Decision. Record them in the Issue or PR.

## 9. Execution status

```text
FL-0 Planning rebaseline: COMPLETE ON THIS DOCUMENTATION PR MERGE
FL-1 Deterministic vertical loop: NOT STARTED
FL-2 Real-provider proof: NOT STARTED
FL-3 Release reconciliation: NOT STARTED

Next authorized action after FL-0 merge:
create exactly one input + real backend routes vertical Issue from latest main
```
