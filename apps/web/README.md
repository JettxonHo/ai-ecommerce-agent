# Web Local Action Workbench

This directory contains the MVP-0 React / Vite browser workbench. It uses
React Router Declarative Mode for `/tasks`, `/tasks/new` and stable
`/tasks/:taskId` deep links, TanStack Query for remote Task state, and the
generated OpenAPI client through a private Task gateway.

The predecessor P0 → P1 → P2 → P3 → P4 → P5 Action Workbench chain is complete
and historical `MVP0P_GOAL_COMPLETE` after PR #315 reached `main`. Its P3 UI and
deterministic gateway remain evidence only: the current FastAPI task resource
still projects `needsInputRequest: null` and does not implement the Needs Input
read/resolve operations. The predecessor P4B result remains
`P4_LOCAL_RELEASE_ACCEPTED`; P5 docs/research remains independently reviewed as
`P5_REUSE_FROZEN`, with direct Spider_XHS reuse and platform behavior frozen and
unauthorized.

The successor [MVP-0L Local AI Web App Delivery Goal](../../docs/goals/mvp0-local-ai-web-app-delivery-goal.md)
is `ACTIVATION_PENDING` on the Issue #316 branch and becomes `ACTIVE` only when
its L0 PR reaches `main`. Its exact order is L0 → L1 → L2 → L3 → L4 → L5 → L6.
L0 is docs-only; no Provider acceptance or authorization is created here. The
eventual real-AI contract is official DeepSeek `deepseek-v4-pro` for fictional
or sanitized acceptance material. Apple Silicon is the first-release boundary;
Docker Desktop is user-installed; the product remains a local Web App opened in
the system default browser. Native App/WebView, signing/notarization, Intel,
login/RBAC/multi-user/public deployment and Keychain/Secret UI are Deferred.

The completed deterministic loop consumes the real local API: create a Task,
save pasted/TXT/Markdown input, run the scripted Facts → Insight → Positioning
→ Marketing Brief → Xiaohongshu Brief pipeline, make the bounded review
correction, confirm once, and download both current Markdown exports. This is
historical predecessor evidence, not the L0 activation result. Real FastAPI
Needs Input/Recovery is still absent (`needsInputRequest: null`) and is the L1
starting gap. The later L3 lifecycle will target Apple Silicon + user-installed
Docker Desktop + system-default-browser opening; L0 does not launch the local
stack, install dependencies, or inspect environment/Secret state.

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
predecessor local stack and Chromium harness are retained as historical,
provider-free evidence. L0 does not launch them. The reviewed direct DeepSeek
adapter and opt-in smoke seam are backend capabilities, not current Provider
acceptance. Both historical DeepSeek authorizations are consumed; no further
paid/provider run is authorized until a later L5 exact-commit human Gate. The
later project-root Git-ignored `.env` convention contains `DEEPSEEK_API_KEY`,
but L0 must not create, read or inspect it.
