# Web Local Action Workbench

This directory contains the MVP-0 React / Vite browser workbench. It uses
React Router Declarative Mode for `/tasks`, `/tasks/new` and stable
`/tasks/:taskId` deep links, TanStack Query for remote Task state, and the
generated OpenAPI client through a private Task gateway.

The predecessor P0 → P1 → P2 → P3 → P4 → P5 Action Workbench chain is complete
and historical `MVP0P_GOAL_COMPLETE` after PR #315 reached `main`. Its P3 UI and
deterministic gateway remain evidence only. Issue #318 adds the real
PostgreSQL-backed FastAPI Needs Input read/resolve boundary and bounded recovery
projection consumed by this existing Workbench; OpenAPI and generated types
remain unchanged. The predecessor P4B result remains
`P4_LOCAL_RELEASE_ACCEPTED`; P5 docs/research remains independently reviewed as
`P5_REUSE_FROZEN`, with direct Spider_XHS reuse and platform behavior frozen and
unauthorized.

The successor [MVP-0L Local AI Web App Delivery Goal](../../docs/goals/mvp0-local-ai-web-app-delivery-goal.md)
is `ACTIVE` after L0 PR #317 reached `main`; Issue #318 is merged/current through
PR #328 after its independent five-axis review `PASS`. Issue #329 / PR #330 is the
completed L2 minimum persistence acceptance/reconciliation Stage from exact base
`dbccacacc54cb21c393987a8612dfc6aa825093b`; its provider-free runtime,
independent five-axis review and fresh Required Checks are `PASS`/`12/12`, PR #330
is merged/current and Issue #329 is closed. Issue #331 is the active L3
Docker-only lifecycle contract; its offline evidence is green on an isolated
branch, its first provider-free runtime is historical `HOLD` at the
image-build-only `uv==0.12.8` failure, and its single corrected-pin runtime
passed health, browser and cleanup. Independent five-axis review is `PASS` at
`f831519`, fresh Required Checks are `12/12`, and Ready PR #332 is `OPEN`/unmerged;
L3 becomes merge-effective/current only when this reviewed record reaches `main`.
L4 is gated and not started.
Its exact order is L0 → L1 → L2 → L3 → L4 → L5 → L6, with the owner-confirmed
MBL-first sequence L2 → L3 → L4 → L5 → Agent UI → L6. L0 was docs-only; the
existing Issue #318 adds no Provider acceptance or authorization. Issue #329's test-only
follow-up restores stale revision/idempotency rejections before and after
recomposition; it adds no production behavior or public-contract change. The
eventual real-AI contract is official DeepSeek `deepseek-v4-pro` for fictional
or sanitized acceptance material. Apple Silicon is the first-release boundary;
Docker Desktop is user-installed; the product remains a local Web App opened in
the system default browser. Native App/WebView, signing/notarization,
login/RBAC/multi-user/public deployment and Keychain/Secret UI are Deferred.
Intel support is Deferred; excluded from the first release.

The completed deterministic loop consumes the real local API: create a Task,
save pasted/TXT/Markdown input, run the scripted Facts → Insight → Positioning
→ Marketing Brief → Xiaohongshu Brief pipeline, make the bounded review
correction, confirm once, and download both current Markdown exports. Issue #318
extends this existing page with an authority-first Chinese Needs Input panel on
the selected Intake view, followed by the same editor/save/regenerate controls;
the blocker remains authoritative until a sufficient generation clears it. The
one-time provider-free runtime acceptance passed 6 backend integration cases and
4 browser cases, including recomposition and reload; PR #328 makes L1
merge-effective with independent five-axis review `PASS`. Issue #329 / PR #330's
one-time provider-free L2 runtime acceptance passed the six-test backend
characterization in `1.41s` on an isolated ephemeral scope at the exact
merge-effective base
`dbccacacc54cb21c393987a8612dfc6aa825093b`; the blocking stale
revision/idempotency finding was resolved by test-only assertions, independent
five-axis review is `PASS`, fresh Required Checks are `12/12`, PR #330 is
merged/current and Issue #329 is closed. The characterization proves Task
primary input, generated/confirmed Marketing/Xiaohongshu results and immutable
Markdown export snapshots across recomposition/replay and a materially newer
fictional input. Issue #331 is the active L3 lifecycle implementation: its
Docker-only Apple Silicon stack and bounded default-browser entry are offline
GREEN on an isolated branch. The ORCHESTRATOR_REVIEWER bounded repair/runtime
ruling under the owner's standing serial-order instruction records the first
attempt as image-build-only `HOLD` because `uv==0.12.8` was unpublished; no
service, health, browser or product-behavior result was produced and guarded
cleanup passed. Tests first required `uv==0.12.6`, and the one new provider-free
attempt built both images, passed PostgreSQL/API/Web health, opened the browser
after health, and passed one bounded `/tasks` read (title “商品上新行动工作台”,
heading “行动首页”) and exact cleanup (Ctrl-C 130). Independent five-axis review
is `PASS` at `f831519`, fresh Required Checks are `12/12`, and Ready PR #332 is
`OPEN`/unmerged; L3 becomes merge-effective/current only when this reviewed
record reaches `main`. L4 is gated and not started. No further runtime,
Provider/model or Secret access is authorized; Agent UI production is not part
of this Stage.

## Toolchain

- Node.js `24.18.0` and npm `11.16.0` (`.nvmrc` and `packageManager` are
  committed).
- React / React DOM `19.2.8`, Vite `8.2.1`, and React Router `8.3.0`.
- `openapi-typescript` `7.13.0` generates the committed API types, and
  `openapi-fetch` `0.17.0` is consumed only by the private client adapter.
- TypeScript `5.9.3`, Vitest `4.1.10`, jsdom `30.0.1`, Testing Library React
  `16.3.2`, user-event `14.6.3`, and Playwright `1.62.1`.

Install exactly from the lockfile:

```bash
npm ci
```

## Local commands

```bash
npm run dev           # http://127.0.0.1:5173 (strict port)
npm run preview       # http://127.0.0.1:4173 (strict port)
npm run format:check
npm run lint
npm run typecheck
npm run test:unit
npm run test:contract
npm run test:e2e
npm run build
npm run api:generate
npm run api:check
```

`src/api/generated/schema.d.ts` is generated from the repository OpenAPI
authority and must remain byte-identical after `npm run api:check`.

The development server proxies `/api` to `http://127.0.0.1:8000`; the
predecessor local stack and Chromium harness are retained as provider-free
evidence, Issue #318's one-time local runtime acceptance is recorded in the
L1 review, and Issue #329 / PR #330's one-time backend persistence acceptance,
independent five-axis `PASS` and fresh checks `12/12` are recorded in the
[L2 review](../../docs/reviews/mvp0l-l2-minimum-persistence.md) at the exact
merge-effective base `dbccacacc54cb21c393987a8612dfc6aa825093b`; PR #330 is
merged/current and Issue #329 is closed. For Issue #331, run the tracked
[AI Ecommerce Agent.command](../../AI%20Ecommerce%20Agent.command) to invoke
the Docker-only local-Web lifecycle; it performs bounded Apple Silicon and
Docker Desktop preflight, renders the `local-web` profile, waits for API/Web
health, then opens the system default browser. `--ephemeral` uses an isolated
project and paired volume and removes both on exit; default stop preserves the
named database volume. For Issue #331, the first runtime is historical
`HOLD` before service creation and the corrected-pin second runtime is
`PASS` with images/health/browser/`/tasks` title+heading/Ctrl-C 130 and exact
ephemeral cleanup. Independent five-axis review is `PASS` at `f831519`, fresh
Required Checks are `12/12`, and Ready PR #332 is `OPEN`/unmerged; L3 becomes
merge-effective/current only when this reviewed record reaches `main`. L4 is
gated and not started. L0 did not launch them. The reviewed direct DeepSeek
adapter and opt-in smoke seam are backend capabilities, not current Provider
acceptance. Both historical DeepSeek authorizations are consumed; no further
paid/provider run is authorized until a later L5 exact-commit human Gate. The
later project-root Git-ignored `.env` convention contains `DEEPSEEK_API_KEY`,
but L0 must not create, read or inspect it.
