# MVP-0 Fast Lane Testing Strategy

> **Status: ACCEPTED VIA DEC-078**
>
> **Authority:** [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md) · [DEC-048](../decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md) · [DEC-078](../decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md) · [DEC-079](../decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md)
>
> This document supersedes the prior Testing Strategy for remaining MVP-0 work. Historical suites stay in the repository; Fast Lane does not require deleting them unless they block delivery.

## 1. What testing must prove

Testing answers five questions:

1. Can a user complete Task create → input → Brief review → Markdown export?
2. Does the system avoid fabricating facts when information is insufficient?
3. Are Task scope, persistence, idempotency and current results correct?
4. Are user/provider data and Secrets kept out of unsafe surfaces?
5. Can a fresh local environment reproduce the deterministic path?

Tests do not attempt to prove every internal implementation shape or every theoretically possible Python/TypeScript value.

## 2. Acceptance scenarios

### Required deterministic normal path

Use the fictional “城市通勤双肩包” sufficient-input material to prove:

- Task creation and stable deep link;
- pasted text or TXT/Markdown input acceptance;
- Facts, Insight and Positioning results;
- Marketing and Xiaohongshu Briefs;
- one review/correction/confirmation;
- Markdown export from the current result;
- page reload returns the same current Task result.

### Required insufficient-input path

Use one representative limited input to prove:

- the system identifies the missing basis;
- unsupported content is labeled as limitation/hypothesis instead of fact;
- no false Proof Point is created;
- the user sees a safe, actionable result or blocking request.

### Not required for Fast Lane

- conflict/mutation matrices from the former four-scenario package;
- Source replace/remove and partial-rerun E2E;
- distributed cancellation, fencing or seven-action recovery;
- semantic/hybrid retrieval evaluation;
- Browser or live-provider edge-case matrices.

These can return under a later Goal with a real consumer and risk statement.

## 3. Per-PR evidence

For a changed behavior or external boundary, start with:

1. one normal case;
2. one primary recoverable failure;
3. one critical invariant or regression case.

Add another case only when it represents a distinct realistic failure with meaningful impact. Do not multiply cases merely because a field can be null, subclassed, aliased, nested or reordered.

Each PR runs:

- tests for the changed module/vertical;
- formatter, linter and type checker for the changed application;
- contract or integration tests only when the corresponding boundary changed;
- build for the changed application;
- existing Required Checks in CI.

Local full-repository suites are optional for unrelated areas. CI is the global regression safety net.

## 4. Test layers

### Unit / module

Use unit tests for deterministic business rules, validation, mapping and state transitions. Prefer the deepest stable application interface. Do not bind tests to private helper structure.

### Contract

Use contract tests for:

- authored OpenAPI ↔ generated client compatibility;
- Model Runtime request/response safety;
- Markdown output safety;
- database/repository behavior actually used by the Fast Lane;
- problem/error mapping consumed by the UI.

Schema authority plus a valid golden and representative invalid cases is sufficient. Recursive every-object/every-array/every-null/every-property-order suites are not required.

### Architecture

Architecture evidence is limited to:

- Import Linter layer rules;
- public facade/export boundaries where external consumers depend on them;
- composition-root checks that prevent real import-time I/O or Secret resolution;
- absence of raw provider/client access outside the accepted adapter boundary.

Do not add package-specific AST frameworks for alias propagation, decorator arguments, exact file inventories, mutable globals or sole-consumer proofs unless a reproduced defect cannot be prevented by simpler tooling.

### Integration

Use real PostgreSQL when a change writes or reads persistent Fast Lane state. Cover the transaction's normal commit, primary failure rollback and idempotent replay where applicable. Do not rerun unrelated lease/fencing/recovery suites locally for a Web-only change.

### Browser E2E

Use Playwright Chromium and the scripted model substitute. Fast Lane requires:

- one complete sufficient-input browser path;
- one representative insufficient-input behavior;
- stable deep-link/reload behavior;
- basic keyboard focus and 320 CSS px reflow on the critical path.

Do not add Firefox/WebKit, visual-regression, device, recovery or combinatorial accessibility matrices for MVP-0.

## 5. Required security tests

Test only boundaries relevant to the local product:

- request/file type, nonblank content and 1 MiB limit;
- fixed-workspace/Task scope and cross-scope `404` behavior;
- parameterized SQL and atomic current-result writes;
- React text rendering and Markdown HTML/link safety;
- loopback same-origin handling for state changes;
- same-input idempotent replay and changed-input conflict for retryable mutations;
- provider Secret/payload/raw exception/traceback exclusion from logs, Problems and exports;
- safe unexpected-error response.

Do not build Login, Token, RBAC, Tenant, internet perimeter or general compliance suites for the fixed local workspace.

## 6. Model verification

Ordinary PRs use the scripted substitute and no network.

The deterministic pipeline verifies required output groups, evidence/limitation honesty and downstream mapping. It does not freeze complete prose or score model style mechanically.

At Release Candidate time, run one explicitly opted-in direct DeepSeek V4 Pro sufficient-input path. It is exactly one fictional Anchor Task and five initial Provider calls; automatic transport retry, repair, regeneration and a second Task are not part of this paid Gate. Record:

- pass/fail;
- model/profile/version tuple;
- duration;
- user-visible result and limitations;
- safe correlation/error reference if it fails.

Do not store the Secret, raw provider payload or reasoning content, and do not create a live edge-case matrix. JSON syntax from `response_format=json_object` is not sufficient acceptance: every stage must pass the existing project Schema / Pydantic and Domain Validator before its result can become downstream context.

## 7. CI policy

Current Required Checks remain active until a separate CI PR updates repository protection. Fast Lane may simplify them without reducing real coverage:

- remove duplicate execution when a full suite already includes unit/contract subsets;
- path-gate Web and Backend work where a stable no-op check preserves branch protection;
- scan PR diffs for Secrets and run full-history scans on main, scheduled or release workflows;
- keep dependency audit, but avoid repeating unchanged ecosystems unnecessarily;
- preserve formatter, linter, typecheck, build, contract and relevant E2E evidence.

A CI optimization must show old/new command coverage and an intentional rollback. It must not hide an existing failure.

## 8. Review policy

Every PR receives Correctness, Readability and Architecture review.

Security review is required when the diff touches input, SQL, scope, transport, rendering, provider data, Secret handling or dependencies. Performance review is required when it touches polling, lists, parsing, rendering, large input or repeated model/database work.

Deliver findings in one concentrated pass where practical. Re-review verifies the original findings and their regression surface. New unrelated low-risk hardening suggestions become follow-up notes, not repeated merge blockers.

## 9. Core commands

Backend commands are maintained in [apps/backend/README.md](../../apps/backend/README.md). A typical affected backend change runs:

```text
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run lint-imports
uv run pytest <affected tests>
uv build
```

Web commands are maintained in [apps/web/README.md](../../apps/web/README.md). A typical affected Web change runs:

```text
npm run format:check
npm run lint
npm run typecheck
npm run test:unit
npm run test:contract
npm run build
```

Run `npm run test:e2e` when the changed vertical affects the browser path. Live model calls never run in ordinary PR CI.

## 10. Goal exit evidence

MVP-0 Fast Lane exits only with:

- all current Required Checks green;
- deterministic sufficient-input Browser E2E green;
- representative insufficient-input behavior green;
- relevant PostgreSQL integration and idempotency evidence green;
- safe Markdown export verified;
- one fresh-environment rehearsal;
- one real direct DeepSeek V4 Pro happy-path smoke;
- Critical/Blocking findings at zero;
- a short list of known limitations and deferred capabilities.

Coverage percentages, test counts, line counts and rubric scores are diagnostic information, not automatic acceptance gates.
