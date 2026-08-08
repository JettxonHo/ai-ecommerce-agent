# Web foundation

This directory is the MVP-0 React / Vite browser foundation. It currently
mounts a semantic shell under React Router Declarative Mode and a TanStack
Query provider; it does not expose task routes, business UI, a generated
client, or API calls.

## Toolchain

- Node.js `24.18.0` and npm `11.16.0` (`.nvmrc` and `packageManager` are
  committed).
- React / React DOM `19.2.8`, Vite `8.2.1`, and React Router `8.3.0`.
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
```

The development server proxies `/api` to `http://127.0.0.1:8000` for later
typed-client work. The foundation shell does not call that proxy. The
contract smoke test fails if rendering starts a network request, and the
Chromium smoke fails on page or console errors.
