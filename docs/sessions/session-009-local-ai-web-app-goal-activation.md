# Session-009：激活 Apple Silicon 本地 AI Web App Goal

## Metadata

- **Date:** 2026-08-24
- **Issue:** [#316](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316)
- **Base:** `origin/main@c5dc2ae9d6e56c6da35f823df838cab4518830f0`
- **Branch:** `codex/mvp0l-l0-local-ai-goal-activation`
- **Decision:** [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md)
- **Successor Goal:** [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md)
- **Predecessor Goal:** [MVP-0P Local Action Workbench Productization Goal](../goals/mvp0-local-action-workbench-productization-goal.md)
- **Configuration evidence:** `CONFIG_VERIFIED` — `luna-worker` / `gpt-5.6-luna` / `max` from `/Users/ketchup/.codex/agents/luna-worker.toml` parsed with Python 3.12
- **Runtime identity:** `UNVERIFIED_RUNTIME_MODEL` — the runtime instance did not independently expose model metadata

## 1. Context and facts

- The predecessor MVP-0P final Goal Review reached `FINAL_GOAL_REVIEW_PASS` and merged in PR [#315](https://github.com/JettxonHo/ai-ecommerce-agent/pull/315). Its merge-effective current status is historical `MVP0P_GOAL_COMPLETE`.
- The predecessor's terminal Fast Lane history remains intact: two failed DeepSeek runs, terminal `GOAL_BLOCKED`, `INSUFFICIENT_SANITIZED_EVIDENCE`, observational ambiguity, no Provider acceptance, no production repair or Phase B contract, and no inherited live authorization.
- The independently reviewed P5 result remains `P5_REUSE_FROZEN`; Spider_XHS reuse and platform behavior are frozen and unauthorized.
- The current FastAPI task resource still projects `needsInputRequest: null`; a real Needs Input read/resolve resource and bounded Recovery are not yet accepted.

## 2. Owner-accepted direction

The owner explicitly accepted the successor direction in Issue #316:

- first release: Apple Silicon Mac only;
- Docker Desktop: user-installed prerequisite;
- product surface: local Web App opened in the system default browser;
- native macOS App/WebView, signing and notarization: Deferred;
- eventual real AI: official DeepSeek API, model `deepseek-v4-pro`;
- later Secret convention: project-root Git-ignored `.env` containing `DEEPSEEK_API_KEY`, with no macOS Keychain or Secret UI;
- acceptance material: fictional or sanitized only;
- login, RBAC, multi-user and public deployment: Deferred;
- one Stage per Issue/PR, with the next Stage only after the prior independently reviewed PR reaches `main`.

These are `Accepted Decision` inputs to DEC-084. They are not inferred from existing code, screenshots, tests or prior Provider evidence.

## 3. Activation record

DEC-084 is recorded as `Accepted` solely from the owner's explicit Issue #316 direction. The predecessor Goal is historical `MVP0P_GOAL_COMPLETE`. The successor Goal is `ACTIVATION_PENDING` on this branch and becomes `ACTIVE` only when the L0 PR reaches `main`; neither this branch nor this Session may claim merge-effective `ACTIVE` earlier.

The exact successor Stage order is **L0 → L1 → L2 → L3 → L4 → L5 → L6**, with only one active Stage at a time:

1. **L0 — Governance activation:** this docs-only Issue and exact nine-path allowlist.
2. **L1 — Real Needs Input backend:** real FastAPI read/resolve and bounded Recovery; begin from the explicit `needsInputRequest: null` gap.
3. **L2 — Minimum Source/Brief persistence:** reconcile tracking parents #81/#82 and create only immediately required bounded child Issues.
4. **L3 — Local Web lifecycle:** Apple Silicon + user-installed Docker Desktop, one reliable command, preflight/health/stop and default-browser opening.
5. **L4 — DeepSeek offline diagnosis/repair:** official base/model and `.env` boundary preserved; no paid/live call.
6. **L5 — Real DeepSeek acceptance:** one separately reviewed exact-commit paid acceptance after L4; no previous authorization carries.
7. **L6 — Clean-Mac acceptance and final Goal Review:** another clean Apple Silicon Mac and an independent completion decision.

The next Issue is created only after the previous Stage's independently reviewed PR reaches `main`. Same-Stage reversible follow-up fixes are batched; no speculative parallel Stage work is authorized.

## 4. L0 document contract

The exact tracked allowlist is:

1. `AGENTS.md`
2. `README.md`
3. `apps/web/README.md`
4. `docs/decisions/dec-084-apple-silicon-local-ai-web-app-goal.md`
5. `docs/decisions/decision-log.md`
6. `docs/goals/mvp0-local-ai-web-app-delivery-goal.md`
7. `docs/goals/mvp0-local-action-workbench-productization-goal.md`
8. `docs/handoffs/implementation-readiness.md`
9. `docs/sessions/session-009-local-ai-web-app-goal-activation.md`

L0 creates no code, tests, configuration, dependencies, lockfiles, migrations, OpenAPI/generated clients, Web implementation, Docker/API/PostgreSQL runtime, environment or Secret access, Provider/model/live call, Kimi/Terra action, native App, public deployment or Spider_XHS action. Stop before a tenth tracked path.

The later `.env` convention is a `Deferred` implementation boundary: L0 must not create, read, inspect, print, measure, hash or load `.env`, environment variables or Secret values. The L5 live call remains a separate human Gate.

## 5. Validation and archive result

L0 validation is documentation-only and proportional under [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md): exact-nine audit, bidirectional relative links, decision-log sequence/status, predecessor-complete vs successor-pending truth, stale/conflict scan, Markdown heading/fence/link checks and `git diff --check`. The delivery is one Ready non-draft PR closing Issue #316; the implementer does not approve, merge or self-review it, and fresh Required Checks must be terminal green before handoff.

### Archive Result

- **Accepted Decision:** DEC-084 is recorded as Accepted from the owner's explicit Issue #316 direction only.
- **Historical predecessor:** MVP0P is `MVP0P_GOAL_COMPLETE`; Fast Lane is terminal `GOAL_BLOCKED`; `P5_REUSE_FROZEN` and `needsInputRequest: null` remain explicit.
- **Successor state:** MVP-0L is `ACTIVATION_PENDING` on the branch and merge-effective `ACTIVE` only after the L0 PR reaches `main`.
- **Deferred / Out of Scope:** Intel, native App/WebView/signing/notarization, login/RBAC/multi-user/public deployment, Keychain/Secret UI, real acceptance material, Spider_XHS behavior and all L0 runtime/provider actions remain excluded.

## 6. Relationships

- **Decision:** [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md)
- **Successor Goal:** [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md)
- **Predecessor Goal:** [MVP-0P Local Action Workbench Productization Goal](../goals/mvp0-local-action-workbench-productization-goal.md)
- **Historical Fast Lane:** [MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md)
- **Issue:** [#316](https://github.com/JettxonHo/ai-ecommerce-agent/issues/316)
