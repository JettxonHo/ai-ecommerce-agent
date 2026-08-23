# Web Local Action Workbench

This directory contains the MVP-0 React / Vite browser workbench. It uses
React Router Declarative Mode for `/tasks`, `/tasks/new` and stable
`/tasks/:taskId` deep links, TanStack Query for remote Task state, and the
generated OpenAPI client through a private Task gateway.

P0 is complete and Issue #303 / [PR #304](https://github.com/JettxonHo/ai-ecommerce-agent/pull/304)
is the merged/current P1 shell. Issue #305 / [PR #306](https://github.com/JettxonHo/ai-ecommerce-agent/pull/306)
carries the P2 Running, Review and Results implementation and is merged/current.
Reconciled [Issue #247](https://github.com/JettxonHo/ai-ecommerce-agent/issues/247)
carries the P3 private Needs Input gateway, Chinese-first bounded action
workspace and Recovery workspace and is merged/current. P2 keeps structured business groups,
separate Marketing / Xiaohongshu views, safe Markdown preview/export, raw JSON
behind technical disclosure, and responsive keyboard / focus / reduced-motion
boundaries. The current FastAPI task resource still projects
`needsInputRequest: null` and does not implement the Needs Input read/resolve
operations, so this frontend/deterministic P3 evidence does not claim a real
browser-to-FastAPI completion. Issue #308 P4A reconciles the real-backend
locators with the merged Chinese single-page TaskWorkbench and adds no
production UI or public contract. Issue #310 P4B records
`P4_LOCAL_RELEASE_ACCEPTED` after one reviewed-main rehearsal passed and its
generated resources were cleaned up without touching the protected default
volume. The accepted provider-free P4 local scope is complete and independently
reviewed. P5 is NEXT as a docs/research-only conditional feasibility Gate;
final Goal Review and its disposition remain pending, so the Productization
Goal stays ACTIVE. No Provider acceptance or authorization was created.

The current deterministic loop consumes the real local API: create a Task,
save pasted/TXT/Markdown input, run the scripted Facts → Insight → Positioning
→ Marketing Brief → Xiaohongshu Brief pipeline, make the bounded review
correction, confirm once, and download both current Markdown exports. The
Workbench also renders honest `insufficient_input` results and reloads saved
Task/input/result state. The representative real-backend Chromium harness is
opt-in with `MVP0_RUN_REAL_BACKEND_E2E=1` and never calls a provider; P4B ran
the existing three fictional-data cases once and all passed. Real FastAPI
Needs Input/Recovery is still absent (`needsInputRequest: null`).

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

The development server proxies `/api` to `http://127.0.0.1:8000`; start the
complete local stack from the repository root with `./scripts/mvp0/demo`, or
run `npm run dev` here when an API is already listening. The contract tests
use an injected transport and the Chromium tests fail on page or console
errors. The reviewed direct DeepSeek adapter and opt-in smoke seam are backend
capabilities. Issue #308 P4A's `./scripts/mvp0/demo --ephemeral` path is an
isolated, repository-prefixed project/temporary-volume option; the default
project and persistent volume remain unchanged. Issue #310 P4B used exactly
one retained foreground ephemeral demo and one real-backend command, then
removed the generated project/network/volume on Ctrl-C. The one authorized one-Task/five-call proof
ran at exact reviewed
`main@1c7c2107ead332235d492ed063b67101784d35f1`, completed five calls with zero
retries, and failed safely before `awaiting_review`; FL-2 is `GOAL_BLOCKED`, not
live verified. Any second paid run requires new explicit authorization.
