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
is `TERMINAL_INCOMPLETE_L5_FAILED` after the merge-effective DEC-087 rebaseline;
L0–L3 are merged/current through PRs #317, #328, #330 and #332 at exact
`origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`. Issue #333 records the L4
offline qualification as `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`, with
production diff zero and no Phase-B amendment. Issue #335 records terminal
`L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` at exact head
`2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`; its one-time authorization is
consumed and no further run is authorized. L6 is `NOT_EXECUTED`, and Agent UI
remains frozen. Issue #345 / PR #346's response-key harness repair is
merge-effective at base `8c43068038d4c3859383d68263f0ab0336480f6a`. Issue #347 is
`P2_READINESS_IMPLEMENTATION_IN_PROGRESS`; only a reviewed PR reaching `main`
may set `P2_READINESS_IMPLEMENTED = YES`. The real P01 Grant and Pilot execution
remain `NOT_AUTHORIZED`; this Web README records no business outcome.
L0 was docs-only; the
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
fictional input. Issue #331 / PR #332 is the merged/current L3 lifecycle at exact
`origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`; its historical build-only
`HOLD`, corrected-pin provider-free `PASS`, independent review and fresh checks
remain recorded. Issue #333's provider-free offline qualification confirms the
current DeepSeek seams and official contract are coherent; the sanitized
signature remains ambiguous and no production behavior changed. No further
runtime, Provider/model or Secret access was authorized within L4; Agent UI
production remains frozen. Future Pilot P1 carries the post-confirm/no-export
boundary as a provider-free characterization target, not an approved repair.

## P2 readiness boundary

Issue #347 is currently `P2_READINESS_IMPLEMENTATION_IN_PROGRESS` on this
branch. The accepted base is
`8c43068038d4c3859383d68263f0ab0336480f6a`; Issue #345 / PR #346 is already
merge-effective. P2 readiness evidence is provider-free implementation and
composition evidence only. It does not authorize a real P01 run, participant
execution, Secret or Provider access, numerator, ratio or business outcome.
Only a reviewed Issue #347 PR reaching `main` may set
`P2_READINESS_IMPLEMENTED = YES`. The fixed reservation, immutable
PilotAttemptArtifacts, explicit Human Review and qualifying-export rules stay
separate from this frontend foundation. The five allowlisted PostgreSQL/FastAPI
composition paths are reused byte-identically, not changed; no migration,
local-demo, public API or default-composition change is implied.

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
evidence. L0–L3 are merged/current through PRs #317, #328, #330 and #332 at
exact `origin/main@2124a9bb20d6b7b327c828331bdc8293ec76577e`; Issue #333 and the
[L4 qualification review](../../docs/reviews/mvp0l-l4-deepseek-offline-qualification.md)
record provider-free offline evidence and disposition
`L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`. The reviewed direct DeepSeek adapter
and opt-in smoke seam are backend capabilities, not Provider acceptance. Issue
#335's Phase-A harness remains preserved as preparation evidence; the single
authorized L5 run is terminal `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` with no
export files and no Provider acceptance. Both historical DeepSeek authorizations
and the #335 authorization are consumed; no further run is authorized. The
later project-root Git-ignored `.env` convention contains `DEEPSEEK_API_KEY`;
outside the single owner-authorized L5 run, no Stage may create, read or inspect
it.
