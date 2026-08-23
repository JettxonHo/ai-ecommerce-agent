# MVP-0 P4A local-release acceptance review

> **Status: P4A merge-conditional — `P4_ACCEPTANCE_PENDING_REVIEWED_MAIN`**
>
> **Issue:** [#308](https://github.com/JettxonHo/ai-ecommerce-agent/issues/308) · **Amendment:** [comment 5387405359](https://github.com/JettxonHo/ai-ecommerce-agent/issues/308#issuecomment-5387405359)

## Scope and current truth

This is the P4A result from exact base `0b92728e1f9050c58dc6db7cc4ae8ef06e1e983a` on branch `codex/mvp0-p4-local-release-acceptance`. P0, P1, P2 and P3 are merged/current. P4A preserves the safe `scripts/mvp0/demo --ephemeral` lifecycle and reconciles the real-backend acceptance harness to the current Chinese-first, single-page TaskWorkbench. It does not claim a passing real browser rehearsal, complete P4, Goal completion or Provider acceptance. A separate reviewed-main P4B Issue is required for the next single fictional-data rehearsal.

The only changed paths are:

- `compose.yaml`
- `scripts/mvp0/lib.sh`
- `scripts/mvp0/demo`
- `scripts/mvp0/test-lifecycle`
- `apps/web/tests/e2e/real-backend.spec.ts`
- this review document
- `AGENTS.md`, `README.md`, `apps/web/README.md`, the successor Goal and `docs/handoffs/implementation-readiness.md`

No application production/backend route, OpenAPI/generated client, migration, dependency/lockfile, Provider, Secret, platform or public deployment behavior changed.

## Agent and repository evidence

- Configuration: fresh Python 3.12 TOML parse of `/Users/ketchup/.codex/agents/luna-worker.toml` returned `name=luna-worker`, `model=gpt-5.6-luna`, `model_reasoning_effort=max` (`CONFIG_VERIFIED`). Runtime instance metadata was not exposed (`UNVERIFIED_RUNTIME_MODEL`).
- Base and protected state: `HEAD=origin/main=0b92728e1f9050c58dc6db7cc4ae8ef06e1e983a` before P4A edits; the persistent default volume remained `ai-ecommerce-agent-mvp0-postgres-data`, project label `ai-ecommerce-agent-mvp0`, Compose volume label `postgres-data`, created `2026-08-08T13:19:22Z`.
- The dirty inventory was kept inside the exact Issue allowlist; `git diff --check` passed.

## Lifecycle result

The pre-edit lifecycle assertion produced the required TRUE RED at the original base: `scripts/mvp0/demo --ephemeral` exited 2 with `ERROR: unknown option --ephemeral`, while the default fake lifecycle path remained protected. The offline implementation then passed `./scripts/mvp0/test-lifecycle` and `./scripts/mvp0/test-static` with fake Docker/host processes only. The tests cover invalid pinned tools, occupied-port fail-closed behavior before `up`, default project/volume preservation without `down --volumes`, ephemeral error and signal cleanup, distinct repository-prefixed scopes, and exact project/paired temporary-volume ownership.

The P4A offline runs recorded these generated scopes and did not create host resources:

```text
error:  ai-ecommerce-agent-mvp0-ephemeral-260823173047-92631-17100
        ai-ecommerce-agent-mvp0-ephemeral-260823173047-92631-17100-pg
signal: ai-ecommerce-agent-mvp0-ephemeral-260823173054-93204-19808
        ai-ecommerce-agent-mvp0-ephemeral-260823173054-93204-19808-pg
default: ai-ecommerce-agent-mvp0
        ai-ecommerce-agent-mvp0-postgres-data
```

The Compose volume name is parameterized only through the repository-prefixed, validated pair. The default project and persistent volume remain exact and are rejected if an unmatched scope is supplied. Ephemeral cleanup uses only the generated Compose project with `down --volumes --remove-orphans`; the default path never performs that operation.

## Terminal real-rehearsal evidence (preserved, not a pass)

The one authorized real rehearsal was run before this P4A amendment against one retained foreground PTY session:

```text
command: PATH=/opt/homebrew/opt/node@24/bin:$PATH ./scripts/mvp0/demo --ephemeral
session: 15469
project: ai-ecommerce-agent-mvp0-ephemeral-260823172531-87462-02709
volume:  ai-ecommerce-agent-mvp0-ephemeral-260823172531-87462-02709-pg
browser: http://127.0.0.1:5173/tasks
```

The single command `PATH=/opt/homebrew/opt/node@24/bin:$PATH MVP0_RUN_REAL_BACKEND_E2E=1 npm run test:e2e -- tests/e2e/real-backend.spec.ts` ran three tests with one worker and failed all three at the same stale harness locator: `getByLabel("粘贴文本")` matched both the source-kind radio and the textarea. No repair or rerun occurred. One Ctrl-C returned 130; the exact ephemeral container, network and volume were absent afterward, ports 8000/5173/55432 were free, and the protected default volume identity above was unchanged. The terminal disposition is `BLOCKED_REAL_REHEARSAL_LOCATOR_STRICT_MODE`, not a product-path PASS.

## Harness reconciliation

### Scan

The Web stack is React 19 + Vite with CSS Modules and one `TaskWorkbench` route at `/tasks/:taskId`; panel query state keeps Intake, Review, Results and evidence on that same route. The merged UI is Chinese-first for the action home and workbench. The New Task form intentionally retains its current English labels (`Task name`, `Product category`, `Promotion goal`, `Create task`), while the workbench exposes Chinese labels (`粘贴文本`, `保存商品资料`, `生成结果`, `资料输入`, `结果`) and the literal panel name `Review`.

### Diagnose

The terminal failure was selector ambiguity, not a backend or product behavior failure: a radio and its textarea intentionally share the visible label `粘贴文本`. The stale English panel selectors were also inconsistent with the merged navigation. No real Needs Input/Recovery backend claim can be made because FastAPI still projects `needsInputRequest: null` and has no public read/resolve resource.

### Fix

The three ambiguous source-entry locators now use the stable semantic textbox role and name:

```ts
page.getByRole("textbox", { name: "粘贴文本" })
```

The full remaining locator scan was reconciled against the current source: English New Task form controls, Chinese workbench controls and status headings, the literal `Review` panel, and scoped Markdown technical-detail assertions. Query deep links remain within `/tasks/:taskId`; no disconnected route or second workspace was introduced. The real-backend spec was not rerun after this fix because the P4A hard freeze prohibits starting Vite or another stack.

## CI follow-up (12th-path amendment)

PR #309's initial 12-check matrix is accepted RED evidence: 11 checks passed and `web / chromium` reported 9 passed / 3 skipped, one flaky and one failed. The two failures were existing asynchronous assertions in `apps/web/tests/e2e/shell.spec.ts` at lines 1202 and 1317; each called `expect(page.getByText(...)).toHaveCount(0)` without `await`, producing `Received: undefined` and a session-closed retry error. `real-backend.spec.ts` did not run. The exact 12th-path repair adds `await` to those two assertions only; no timeout, fixture, product code or other assertion changed. Local shell E2E remains `NOT_RERUN_DUE_EXPLICIT_NO_VITE`, and the follow-up CI job must provide the fresh 12/12 result.

## Offline validation

Lockfile-only hydration used existing caches (`npm ci --offline --no-audit --no-fund`, `uv sync --locked --offline`); `apps/web/package-lock.json` and `apps/backend/uv.lock` remained byte-identical. The canonical local tuple was Node `24.18.0`, npm `11.16.0`, Python `3.13.14`, uv `0.12.0`, Docker Compose `2.39.1-desktop.1`, Vite `8.2.1`.

| Command | Result |
| --- | --- |
| `./scripts/mvp0/test-lifecycle` | PASS (offline fake lifecycle) |
| `./scripts/mvp0/test-static` | PASS |
| `cd apps/web && npm run format:check` | PASS |
| `cd apps/web && npm run lint` | PASS |
| `cd apps/web && npm run typecheck` | PASS |
| `cd apps/web && npm run test:unit` | PASS — 8 files / 119 tests |
| `cd apps/web && npm run test:contract` | PASS — 10 files / 50 tests |
| `cd apps/web && npm run api:check` | PASS |
| `cd apps/web && npm run build` | PASS |
| `apps/web/tests/e2e/shell.spec.ts` | `NOT_RERUN_DUE_EXPLICIT_NO_VITE` (Playwright config auto-starts Vite; P4A hard freeze forbids it) |
| `apps/web/tests/e2e/real-backend.spec.ts` | `NOT_RERUN_DUE_TERMINAL_REHEARSAL_AND_NO_VITE` |

## Five-axis Review input

- **Correctness:** offline lifecycle GREEN covers default protection, bounded ephemeral ownership, fail-closed preflight and cleanup; the source-level locator repair matches current roles. The only real-stack evidence remains the terminal strict-mode failure, so P4 acceptance is pending reviewed-main evidence.
- **Readability:** changes are narrow and comments name the default/ephemeral safety contract. The review records the stale harness mismatch without relabeling it as a product RED.
- **Architecture:** Compose parameterization is limited to the project/volume pair; no backend, public contract, generated client, migration or new module/seam was added. The single TaskWorkbench route and query-state deep links remain intact.
- **Security:** default volume is guarded by exact identity, ephemeral names are repository-prefixed and paired, cleanup is scoped to the generated project, and no Secret/provider payload/platform action was used. Existing input, Markdown and same-origin boundaries remain unchanged.
- **Performance:** no production runtime path changed; the added lifecycle checks use bounded fake processes and no network or model calls. Browser dimensions and the representative shell evidence remain governed by existing tests.

## Gate and limitations

`P4_ACCEPTANCE_PENDING_REVIEWED_MAIN` is the current result. The old Fast Lane Goal remains terminal `GOAL_BLOCKED`; no Provider acceptance exists and no Provider run is authorized. P3 is merged/current. P5 remains a gated docs/research feasibility candidate with no Spider_XHS reuse or platform action. The Productization Goal is not complete: P4B and final independent ORCHESTRATOR Goal Review remain pending.
