# MVP-0L L1 Needs Input Backend Review

## Disposition

**Fact:** Issue [#318](https://github.com/JettxonHo/ai-ecommerce-agent/issues/318) is the active L1 Stage after L0 PR #317 reached `main`. This review records the implementation branch against the exact reviewed base `origin/main@8c67eb571c54bdb77538c9bb79f1035150eec4d5`.

**Fact:** The implementation and one-time provider-free runtime acceptance are complete on branch `codex/mvp0l-l1-needs-input-backend`. Independent `ORCHESTRATOR_REVIEWER` review, merge and fresh CI checks remain required; this document does not approve or merge the change.

**Fact:** The durable runtime disposition is [`L1_RUNTIME_ACCEPTANCE_PASS`](https://github.com/JettxonHo/ai-ecommerce-agent/issues/318#issuecomment-5436381488). No credentials, database URLs, provider/model payloads, Secret values or `.env` contents are recorded here.

## Changed boundary and ownership

**Fact:** The change stays within Issue #318's allowlist:

- one additive Alembic revision, `0009_needs_input.py`, creating the single Task-owned Needs Input table and bounded indexes;
- the private `modules/needs_input/**` domain/application/infrastructure module, PostgreSQL composition, and dedicated FastAPI route module;
- the minimum existing result/local-demo/app/task-route composition changes needed to publish and project the current request atomically;
- proportional backend migration, contract, architecture, unit and PostgreSQL integration tests;
- the existing `TaskWorkbench.tsx`, its tests, and the existing real-backend browser harness required by the accepted one-page recovery amendment;
- the six current-truth documents allowed by the Issue: `AGENTS.md`, `README.md`, `apps/web/README.md`, this Goal, the implementation-readiness handoff, and this review.

**Fact:** `contracts/openapi/openapi.yaml`, `apps/web/src/api/generated/schema.d.ts`, `apps/web/package.json`, `apps/web/package-lock.json`, CSS, Compose topology and dependency declarations are unchanged.

## Behavioral evidence

**Fact — backend:** The real PostgreSQL integration proves one bounded lifecycle with fictional input: an insufficient result publishes a Task-scoped request; a materially newer still-insufficient save/generate uses a distinct idempotency key and result revision, leaves the newer request `OPEN/current`, and marks the first request `SUPERSEDED` with a successor revision of `0`; a fresh composition re-reads both requests and the current result; sufficient save/generate marks the newer request `SUPERSEDED` with `supersededBy = null` and clears `TaskOverview.needsInputRequest`; a final composition observes the same current truth. The resolution path also proves ownership, revision, bounded resolution and same-key replay after recomposition.

**Fact — browser:** The existing Chromium harness proves the fictional insufficient path, Chinese Needs Input reason and affected stage, Review/export unavailability before recovery, and the selected Intake one-page order where the authoritative Needs Input reason/actions precede the existing editor. It saves sufficient fictional Anchor SKU input without resolving/cancelling the blocker, observes that the blocker remains authoritative after save, generates Results, and reloads to the recovered state. The runtime run passed all four existing real-backend cases.

**Observation:** Needs Input remains a bounded action-request surface, not a generic recovery dispatcher, questionnaire, Source platform, Review Draft flow or Provider runtime. The UI does not invent a resolution or hide the blocker while input is still insufficient.

## RED → GREEN chronology

**Fact:** The accepted Web tests-only RED was captured before the production Workbench edit: the canonical direct Vitest run had one intended missing-Intake-control failure and 32 passing tests, with `TaskWorkbench.tsx` unchanged. The minimal production edit then made the selected Intake authority-first path GREEN while preserving the other Workbench modes and safe rendering boundaries.

**Fact:** The backend integration expectation was corrected before final acceptance so the first request's final `supersededBy.revision` is `1`, while the earlier replacement assertion remains revision `0` and the final second request is `SUPERSEDED` at revision `1` with no successor. The canonical integration file then passed all six tests in the one-time runtime.

## Validation and runtime evidence

**Fact:** Proportional offline checks passed for the changed boundaries: backend Ruff format (`488 files already formatted`), Ruff lint (`All checks passed!`), Pyright (`0 errors, 0 warnings, 0 informations`), Import Linter (`10 kept, 0 broken`), targeted backend tests (`46 passed, 4 skipped`), integration collection (`6 tests collected`), Web Prettier, ESLint, TypeScript, Web unit (`8 files / 120 tests passed`), Web contract (`10 files / 50 tests passed`), production build and `api:check`. `git diff --check` and changed-document link/fence checks also pass. No dependency installation/update or network package action was used.

**Observation:** The broader backend unit/contract/migration/architecture command currently reports `1 failed, 2056 passed, 5 skipped` at `test_scripted_facade_has_exact_order_and_identity`, because `openai_responses` leaks into the scripted facade after another test imports it. The same broad command on a fresh exact-base clone (`fe431693070bfa5a5bbe936b41556fbea8027ab2`) reports the identical failure (`1 failed, 2032 passed, 1 skipped`), while the isolated test passes on both base and current. This pre-existing order/leakage issue is outside the Issue #318 allowlist and is not changed here.

**Fact:** The exact one-time local runtime used Node `v24.18.0` and the retained foreground command `PATH=/opt/homebrew/opt/node@24/bin:$PATH ./scripts/mvp0/demo --ephemeral`. It emitted the sanitized project `ai-ecommerce-agent-mvp0-ephemeral-260827082159-20436-22350`, paired volume `ai-ecommerce-agent-mvp0-ephemeral-260827082159-20436-22350-pg`, and Browser URL `http://127.0.0.1:5173/tasks`.

**Fact:** From the repository root, the exact backend command passed `6 passed in 1.41s`:

```text
MVP0_RUN_TASK_HTTP_POSTGRES=1 uv run --project apps/backend --locked pytest -q apps/backend/tests/integration/test_task_http_postgres.py
```

**Fact:** From `apps/web`, the exact browser command passed `4 passed (7.8s)`:

```text
CI= MVP0_RUN_REAL_BACKEND_E2E=1 PATH=/opt/homebrew/opt/node@24/bin:$PATH npm run test:e2e -- tests/e2e/real-backend.spec.ts
```

**Fact:** Cleanup sent exactly one Ctrl-C to the retained demo PTY and waited for guarded cleanup. The emitted project, paired volume and network were absent afterward; ports `8000`, `5173`, `55432` and `55433` were free; the protected default resources were absent; the sole prior surviving volume and exact preservation-copy metadata were unchanged; Docker remained active because it was initially active; and the Git inventory remained unchanged by runtime.

## Security, performance and rollback posture

**Fact:** Task ownership, fixed workspace, same-origin writes, revision fencing, opaque bounded idempotency keys, UTF-8 byte bounds, parameterized SQL, safe RFC 9457 errors and atomic current-result/request reconciliation are enforced at their existing boundaries. User/provider-like text is bounded and is not interpolated into SQL or error detail.

**Fact:** Migration `0009_needs_input` is additive and forward-only. Its downgrade rejects destructive rollback; any future repair must be a new forward revision. No existing table, column, constraint, row or public DTO is rewritten.

**Risk:** The runtime evidence is local, fictional-data, provider-free evidence and does not establish live Provider acceptance, public deployment readiness, multi-user security or later L2–L6 completion.

## Current-truth impact and remaining gate

**Fact:** L0 is merged/current through PR #317 and the successor Goal is `ACTIVE`. Issue #318's L1 implementation and exact one-time runtime acceptance are recorded here and in the durable Issue comment above. L2 remains gated until an independently reviewed L1 PR reaches `main`.

**Proposal:** The `ORCHESTRATOR_REVIEWER` should perform the required correctness, readability, architecture, security and proportional performance review, verify the fresh Required Checks, and decide whether the single Ready non-draft PR may be merged. The implementer does not approve or merge.
