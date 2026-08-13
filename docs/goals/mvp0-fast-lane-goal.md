# MVP-0 Fast Lane Goal

> **Status: ACTIVE — FL-2 TERMINAL RESULT `GOAL_BLOCKED`**
>
> **Accepted baseline:** `main@371ea0c15546b91ee10fcde8622553b164e5740c`
>
> **Accepted by the user on 2026-08-12:** adopt the vertical Fast Lane approach; narrow first-phase inputs to pasted text, TXT and Markdown; rebaseline planning before further implementation; accept the detailed Goal.
>
> **Activation:** [DEC-078](../decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md) records acceptance. PR #248 merged on 2026-08-12 and made this the sole active remaining MVP-0 Goal.
>
> **Accepted cleanup amendment on 2026-08-13:** legacy code and tests are simplified immediately only when they block the current vertical. Other non-blocking legacy work stays frozen until one bounded cleanup reconciliation after the Fast Lane execution result is known and before the final Goal decision.
>
> **Accepted Provider amendment on 2026-08-13:** [DEC-079](../decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md) replaces the remaining OpenAI live Gate with one direct DeepSeek official API proof using `deepseek-v4-pro`. The deterministic loop, text-only input, project Schema / Domain authority, Secret boundary, one Task / five calls limit and post-FL-2 cleanup sequencing remain mandatory.
>
> **FL-2 terminal results on 2026-08-13:** the first authorized run at exact reviewed `main@1c7c2107ead332235d492ed063b67101784d35f1` completed five calls with `retry_count=0` and `recovery_count=0`, then failed safely before `awaiting_review`; its fifth Xiaohongshu-v1 call reached 12,288 output tokens and recorded 136,622 ms latency against the historical 120 s timeout. After the DEC-080 offline repair and post-FL-2 cleanup, [Issue #281](https://github.com/JettxonHo/ai-ecommerce-agent/issues/281) executed a second smoke at exact `main@ac4edfed6e8e216e9938affdc734298c8630d2de`: one `product_intake_v1 / v1` call returned safe metadata with input 2,353 / output 8,192 / total 10,545 tokens and 106,434 ms latency, then generate-result failed with fixed safe HTTP 500 before `awaiting_review`. Retry/recovery remained 0/0, all behavior gates were false and stages 2～5 did not run. The 8,192 output equals the first-stage ceiling but is only a diagnostic lead, not a proven root cause, because evidence excludes finish reason, raw response and internal error category. #281 authorization is consumed and closed; no further Provider run is authorized. Live verification is not claimed and Goal remains `GOAL_BLOCKED`.
>
> **Accepted bounded repair on 2026-08-13:** [DEC-080](../decisions/dec-080-fl2-xiaohongshu-profile-v2-and-deadline-fence.md) authorized an offline-only `xiaohongshu_mapping_v1 / v2` repair at 16,384 `max_tokens` / 240 s plus a post-return application deadline fence. The other four profiles and all provider/security/retry boundaries remained unchanged. The repair was merged as [PR #280](https://github.com/JettxonHo/ai-ecommerce-agent/pull/280), and [Issue #274](https://github.com/JettxonHo/ai-ecommerce-agent/issues/274) completed the bounded legacy cleanup. The subsequent #281 run stopped at the unchanged first-stage v1 boundary, so it did not exercise stages 2～5 or establish live acceptance. Goal status remains `GOAL_BLOCKED`; any new repair, Provider call or product direction requires a new user Decision and separate contract.

## 1. Outcome

Deliver the smallest local AI Ecommerce Agent demo that proves one complete user job:

1. create a Task;
2. provide one product-information input by paste, TXT or Markdown;
3. run a deterministic Facts → Insight → Positioning → Brief pipeline;
4. review and confirm the result once;
5. view a Marketing Brief and Xiaohongshu Brief;
6. export the current result as Markdown;
7. repeat the same sufficient-input path once with DeepSeek official `deepseek-v4-pro` at Release Candidate time.

The Goal optimizes for the first working browser-to-backend-to-output loop. It does not optimize for the completeness of previously designed infrastructure.

## 2. Why this Goal exists

### Facts at the draft baseline

- The repository already contains substantial Task, Source, Durable Dispatch, Model Runtime, output-contract, Markdown-rendering and Web foundations.
- The Web application has a generated client, Task gateway, recent/create/read routes, a private Workbench projection and a TaskWorkbench progress shell.
- The FastAPI application factory still has no registered business routes, so the browser cannot complete a real backend workflow.
- Historical planning documents describe several already-merged Web capabilities as unimplemented and no longer provide reliable current status.
- Backend tests materially exceed backend production code, and architecture tests alone are close to the size of the production package.

### Accepted decision

The user accepted the vertical Fast Lane approach and this detailed Goal because continued horizontal contracts, exhaustive defensive tests and metadata-heavy reviews were slowing the first useful product loop.

### Governing principle

[DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md) is enforced literally: validation, security and review effort must be proportional to a realistic MVP risk. Representative evidence is sufficient after the core invariant is proven.

## 3. Active authority set after acceptance

An implementation task reads only the smallest relevant set:

1. [AGENTS.md](../../AGENTS.md);
2. this Goal;
3. [DEC-001](../decisions/dec-001-business-value-before-agent-complexity.md), [DEC-003](../decisions/dec-003-product-launch-positioning-and-marketing-brief.md) and [DEC-004](../decisions/dec-004-platform-neutral-core-xiaohongshu-demo.md);
4. [DEC-011](../decisions/dec-011-deterministic-workflow-with-constrained-llm-reasoning.md) and [DEC-020](../decisions/dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md);
5. [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md) and [DEC-048](../decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md);
6. [DEC-052](../decisions/dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md), [DEC-079](../decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md), [DEC-055](../decisions/dec-055-frontend-application-state-and-verification-foundation.md), [DEC-062](../decisions/dec-062-minimal-recent-task-index-and-stable-deep-links.md) and [DEC-065](../decisions/dec-065-immutable-brief-export-problem-and-fixed-workspace-api-boundary.md);
7. [DEC-071](../decisions/dec-071-luna-worker-exclusive-implementation-routing.md) and [DEC-072](../decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md);
8. the current Issue and the actual code/tests it changes.

Other Decisions and RFCs remain historical or future authority. They are read only when the current vertical slice directly touches their public or irreversible boundary. Historical Session files are not implementation prerequisites.

## 4. Product scope

### In scope

- One fixed local workspace with no login or tenant selector.
- Existing `/tasks` list, Task creation and stable Task deep link.
- One primary Task-scoped product input:
  - pasted nonblank text; or
  - one UTF-8 `.txt` or `.md` file;
  - proposed limit: 1 MiB.
- A single in-process deterministic coordinator for the four Core Skills and Xiaohongshu mapping.
- Existing scripted model substitute for ordinary development and E2E.
- One sufficient-input normal path and one honest insufficient-input result.
- A single review screen where the user can inspect, make a bounded text correction and confirm the result.
- Current Marketing Brief, current Xiaohongshu Brief and UTF-8 Markdown export.
- Existing PostgreSQL components where they reduce work; the implementation may use one minimal additive persistence participant rather than completing the whole designed persistence graph.
- One opt-in DeepSeek official `deepseek-v4-pro` happy-path smoke after the deterministic loop passes.

### Explicitly deferred to MVP-1 or a later Goal

- JSON, CSV, PDF, image, OCR and arbitrary office-file intake.
- Embedding, vector, semantic or hybrid retrieval; RRF; DatasetStatistic; full EvidencePackage lifecycle.
- Multi-worker dispatch, Lease, Heartbeat, fencing, supersession and distributed Commit Fence completion.
- Durable checkpoint recovery, seven-action reconciliation, partial rerun and complete cancellation matrices.
- Source replace/remove preview-confirm UX and physical deletion.
- Review autosave, semantic diff, stale-draft recovery and multiple review outcomes.
- Brief comparison, revision history browsing and non-current export operations.
- Full public API operation catalog when an operation has no Fast Lane UI consumer.
- Multi-provider, multi-agent, model routing, automatic publication, public deployment and platform operations.
- Login, RBAC, tenant management, internet exposure and enterprise security controls.
- General-purpose compliance, telemetry, analytics or performance platforms.

Deferred code already in the repository is not deleted merely because it is outside the Fast Lane. It is frozen unless the Fast Lane path must call it, it blocks a valid current vertical, or the bounded cleanup reconciliation below proves that it is safe and useful to remove.

### Legacy cleanup sequencing

- **During vertical delivery:** if an obsolete guard, redundant abstraction, dead adapter or over-defensive test blocks the current user path, remove or narrow it in that Issue and replace it with the smallest representative behavior or boundary evidence needed. Do not preserve obsolete structure just to keep an old structural test green.
- **While it does not block delivery:** freeze it. Do not spend Fast Lane time completing, refactoring, documenting or adding tests to unused advanced capabilities.
- **After FL-2 reaches a terminal result and before the final Goal decision:** create one bounded cleanup Issue. Use repository-wide consumer and dependency evidence to classify legacy code, tests and current-status documentation as `retain`, `freeze for later` or `remove now`.
- **Remove now** only when the item has no real current or accepted next-Goal consumer, is superseded or duplicated, and can be removed without weakening a required security/data boundary or destabilizing the demo.
- **Retain or freeze** capabilities whose removal is riskier than leaving them dormant. Cleanup is not a line-count target and does not require deleting every deferred implementation.
- Record what was removed, what remains frozen and why. Do not represent frozen capability as part of the working MVP.

## 5. Required security boundary

The following protections remain mandatory:

- external request and file-boundary validation;
- Task/fixed-workspace scope checks;
- parameterized SQL and atomic persistence of the user-visible result;
- React text rendering and safe Markdown projection;
- loopback/same-origin browser transport and closed cross-origin state changes;
- stable idempotency for Task creation and any user-triggered mutation that may be retried;
- Secret isolation and redaction of provider payloads, raw SDK objects and tracebacks;
- safe user-visible errors without internal identifiers or stack data;
- dependency vulnerability checks and Secret scanning at proportionate cadence.

The following are not Fast Lane security requirements:

- authentication or multi-tenant authorization for the local fixed workspace;
- a new AST security scanner for each private module;
- exhaustive alias, decorator, subclass, null, array and nested-path mutation matrices;
- exact private directory inventories or sole-consumer proofs;
- full-history Secret scanning on every pull request when a diff scan plus periodic full scan provides the same practical protection.

## 6. Delivery plan

### FL-0 — Planning rebaseline

Outcome: one short, reliable execution entry point.

- record the accepted Goal in DEC-078, which amends DEC-075 for MVP-0 execution priority;
- mark the old Goal as superseded for remaining MVP-0 execution, while preserving it as history;
- update README, AGENTS, Implementation Readiness and Testing Strategy;
- mark old unstarted infrastructure/backlog Issues deferred rather than automatically closing implemented work;
- do not create a business implementation Issue until this documentation change is merged.

Exit: the repository has one current status, one active Goal and no contradictory instruction to continue the old horizontal backlog.

### FL-1 — Deterministic vertical loop

Outcome: the browser completes the full local loop with the scripted model.

Prefer no more than three implementation Issues:

1. **Input and backend route vertical** — persist the minimal Task input and connect the existing generated client/UI to real Task read/create/input handlers.
2. **Pipeline and result vertical** — synchronously run Facts → Insight → Positioning → Marketing Brief → Xiaohongshu mapping and persist/project the current result.
3. **Review and export vertical** — one review/confirmation interaction, current result pages and real Markdown download.

Each Issue must include a real consumer. A contract, DTO, Protocol, facade or repository with no use in the same vertical or the immediately following vertical is not an acceptable standalone deliverable.

Exit:

- one Chromium E2E starts from `/tasks`, creates a Task, provides sufficient text, runs the pipeline, confirms the result and downloads Markdown;
- one representative insufficient-input test shows an honest limitation instead of fabricated facts;
- no real Provider or network is used.

### FL-2 — Real-provider proof

Outcome: prove the same completed path once with the accepted DeepSeek official provider.

- use the already-defined narrow runtime boundary and explicit opt-in `DEEPSEEK_API_KEY` loading;
- use `deepseek-v4-pro` Chat Completions JSON Mode, then require project Schema / Domain validation;
- run one sufficient-input Anchor SKU path;
- record pass/fail, model/version tuple, duration and known limitations without storing raw sensitive provider data;
- stop after any ambiguous or invalid result; the paid Gate is exactly one Task and five initial calls with no automatic retry or repair;
- do not build a live edge-case matrix.

Exit: one successful human-observed Task-to-export run, or `GOAL_BLOCKED` with the exact failing boundary.

### FL-3 — Release reconciliation

Outcome: a truthful, reproducible local demo.

- one fresh-environment start rehearsal;
- one concise operator path;
- after FL-2 has a terminal result, one bounded legacy cleanup Issue and PR using the classification rules above;
- one final five-axis review, with Security and Performance limited to relevant changes;
- update current-status documents and list deferred capabilities.

Exit: the demo remains reproducible, confirmed dead or obstructive legacy work is removed, retained deferred capability is explicitly frozen, and cleanup has not weakened the mandatory boundaries in section 5.

## 7. Test and review policy

### For each implementation PR

- Write tests first for the user-visible behavior or external boundary being changed.
- Use the smallest meaningful set: normal path, primary recoverable error and one critical invariant.
- Prefer tests through a deep public/application interface over tests of private implementation structure.
- Existing Required Checks remain until a separately reviewed CI change updates branch protection.
- Local verification runs affected tests and static checks; unrelated full suites may be left to CI.
- Do not add recursive every-field schema tests when OpenAPI/JSON Schema plus representative contract cases already prove the boundary.
- Do not add a new AST meta-test unless it prevents a reproduced architecture or security failure that simpler tooling cannot catch.
- Do not add exact file-inventory tests for private packages.

### Review

- Correctness, readability and architecture are reviewed for every PR.
- Security and performance are reviewed only where the diff creates or changes those risks.
- Findings are delivered in one concentrated review pass where practical.
- Re-review verifies the original findings and regression surface; it does not reopen unrelated low-risk stylistic variants.
- PR descriptions require problem, scope, evidence, risk and rollback intent. Exact SHA chains, reverse commit inventories, model-status slogans and manual LOC arithmetic are not acceptance gates because Git already records them.

### Release evidence

- deterministic browser normal path;
- representative insufficient-input behavior;
- backend/frontend build and relevant contract checks;
- one opt-in real-provider smoke;
- a short human usability result and a list of known limitations.

## 8. Issue policy

- Create one vertical Issue at a time unless file ownership is clearly disjoint.
- Default to changing the fewest existing modules needed to complete the user behavior.
- Do not split work only to satisfy a line-count target. Split when interfaces, ownership or reviewability genuinely improve.
- Do not create a new Decision for a reversible implementation choice.
- Do not introduce an abstraction until the vertical path has a real consumer; prefer an existing interface or direct implementation before a speculative seam.
- Stop adding defensive variants after the representative failure and invariant are proven.
- Remove a legacy guard or implementation in the current Issue when it materially blocks that Issue; otherwise defer cleanup to the single bounded reconciliation rather than opening opportunistic cleanup work.
- The cleanup Issue must use actual consumer/dependency evidence. Code size, aesthetics or a desire for a perfectly tidy architecture is not deletion evidence.
- A completed sub-agent is closed promptly unless it has an immediate bounded follow-up.

## 9. Stop conditions

Stop the affected Issue and request direction when:

- the user-visible Fast Lane path requires a new public product behavior not described here;
- a destructive migration or existing-data rewrite is required;
- the implementation requires public deployment, real user data or additional paid/external providers;
- a real Secret could be exposed;
- the chosen minimal persistence approach cannot preserve Task scope or atomic current results;
- a supposedly necessary contract or infrastructure slice has no concrete Fast Lane consumer;
- a change attempts to revive a deferred capability without separate user authorization;
- the exact `luna-worker` implementation agent is unavailable and no user-authorized substitute exists.

A need to bypass a previously designed advanced component is not by itself a stop condition when the alternative is local, reversible, preserves the mandatory security boundary and is documented in the Issue.

## 10. Goal completion criteria

This Goal is complete only when all are true:

- a fresh local environment can start the required database, backend and Web app;
- the browser completes Task create → input → deterministic pipeline → review → two Briefs → Markdown export;
- sufficient input produces all required result groups without fabricated evidence;
- insufficient input produces an honest limitation or blocking request;
- current result persistence survives page reload and stable deep-link return;
- the fixed-workspace, SQL, XSS/Markdown, idempotency and Secret boundaries above pass representative tests;
- one real DeepSeek V4 Pro direct happy-path smoke succeeds;
- the bounded legacy cleanup reconciliation is reviewed and merged, with retained deferred capability listed as frozen;
- no Critical or Blocking defect remains;
- deferred capabilities are documented without being represented as implemented;
- current project status matches actual code.

The completion decision is `GOAL_APPROVED`, `GOAL_APPROVED_WITH_FOLLOW_UPS`, `GOAL_BLOCKED` or `GOAL_REJECTED`.

## 11. Authorized activation changes

Acceptance of this detailed Goal authorizes this documentation-only rebaseline before implementation:

1. create DEC-078 to amend DEC-075 for the remaining MVP-0 execution;
2. update the old Goal status without deleting its history;
3. synchronize AGENTS, README, Implementation Readiness and Testing Strategy;
4. reconcile open Issues against the deferred list;
5. merge the documentation PR;
6. create only the first FL-1 vertical Issue and resume autonomous execution under DEC-072.

The documentation PR performs items 1～3. Issue reconciliation and FL-1 implementation begin only after that PR merges.
