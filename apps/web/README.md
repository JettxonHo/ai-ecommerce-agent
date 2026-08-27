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
is `ACTIVE` after L0 PR #317 reached `main`; Issue #318 is the active L1 Stage.
Its independent five-axis review is `PASS`, while the replacement PR and merge
remain pending. L1 becomes merge-effective only after that replacement PR reaches
`main`; L2 remains gated. Its exact order is L0 → L1 → L2 →
L3 → L4 → L5 → L6. L0 was docs-only; Issue #318 adds no Provider acceptance or
authorization. The
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
4 browser cases, including recomposition and reload; independent five-axis review
is `PASS`, while the replacement PR and merge remain pending. L1 becomes
merge-effective only after that replacement PR reaches `main`; L2 remains gated.
The later L3 lifecycle will
target Apple Silicon + user-installed Docker Desktop + system-default-browser
opening; no Provider/model or Secret access is part of this Stage.

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
evidence, and Issue #318's one-time local runtime acceptance is recorded in the
L1 review. L0 did not launch them. The reviewed direct DeepSeek
adapter and opt-in smoke seam are backend capabilities, not current Provider
acceptance. Both historical DeepSeek authorizations are consumed; no further
paid/provider run is authorized until a later L5 exact-commit human Gate. The
later project-root Git-ignored `.env` convention contains `DEEPSEEK_API_KEY`,
but L0 must not create, read or inspect it.
