# DEC-086：接受 Real Product-to-Brief Pilot 合同但暂不激活

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-29
- **Decision Type:** Product Delivery / Goal Governance / Pilot Acceptance / Human Gates
- **Source:** 用户于 2026-08-29 在 Codex conversation 中明确接受本 Goal、边界、80% completion threshold 与串行执行顺序；本决定由 [Issue #337](https://github.com/JettxonHo/ai-ecommerce-agent/issues/337) 持久记录
- **Decision Session:** [Session-010](../sessions/session-010-real-product-to-brief-pilot.md)
- **Successor Goal:** [Real Product-to-Brief Pilot](../goals/real-product-to-brief-pilot-goal.md)
- **Pilot Contract:** [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)
- **Amended by:** [DEC-087](dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md) — formal terminal rebaseline and merge-effective Pilot activation

> **Amendment trace:** The body below remains the historical accepted state at DEC-086 creation. [DEC-087](dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md) later amends only the inactive prerequisite: on the Issue #339 branch MVP-0L is `REBASELINE_PENDING`, the Pilot is `ACTIVATION_PENDING`, and P0 is `NOT_STARTED`; only after that reviewed PR reaches `main` do MVP-0L `TERMINAL_INCOMPLETE_L5_FAILED`, Pilot `ACTIVE`, and P0 `READY_NOT_STARTED` become effective. DEC-087 preserves the P0→P6 order and denominator and authorizes no P0 or Provider action.

## Context

### Facts

- [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md) remains the only active Goal and is `ACTIVE`.
- The current L5 boundary is [Issue #335](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335) / [PR #336](https://github.com/JettxonHo/ai-ecommerce-agent/pull/336), whose exact reviewed head is `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f` over `ef5ac0d4b372c1478ee2541ee3ec5318e72a1060`.
- The owner-authorized one-time L5 run has no Provider-request evidence on that head; its authorization remains **unconsumed**. This Decision does not resume, retry or alter #335 / #336.
- The existing deterministic pipeline, DeepSeek adapter, Task HTTP/Web boundaries and migrations 0007–0009 are existing implementation evidence only; G0 does not change them.

### Observations

- A real Product-to-Brief Pilot needs a bounded evidence contract that separates real-provider business evidence from deterministic or fixture evidence.
- Activating a successor before the current MVP-0L release is complete would create two competing execution entries and could be mistaken for permission to resume the held L5 work.

## Decision

### 1. Accepted successor, inactive state

Accept the successor Goal **Real Product-to-Brief Pilot** and its normative [Pilot Contract](../product/real-product-to-brief-pilot-contract.md) as `ACCEPTED / NOT ACTIVE`. Activation is blocked until the current MVP-0L Goal reaches `COMPLETE` or the owner explicitly accepts a formal rebaseline. MVP-0L remains the only `ACTIVE` Goal.

The current G0 delivery is governance formalization only. It does not activate Pilot P0, resume #335 / PR #336, consume the held L5 authorization, or call a Provider. G0 is recorded by [Issue #337](https://github.com/JettxonHo/ai-ecommerce-agent/issues/337) with exactly one Issue and one observable documentation outcome.

### 2. Frozen G0 and Pilot stage order

G0 is the Issue #337 docs-only entry gate. After the activation condition is met, Pilot stages execute serially as **P0 → P1 → P2 → P3 → P4 → P5 → P6**. Only one Stage may be active at a time, and each Stage has one independently reviewable Issue/PR for one observable outcome. Every Stage follows the frozen lifecycle **Plan → Implementation → Automated Verification → Runtime / Browser Evidence（适用时）→ Independent Review → Owner Gate（适用时）**; the lifecycle does not itself authorize a Provider, Secret, product-runtime, platform-network or irreversible external behavior.

1. **P0 — Pilot readiness and permitted-input gate:** reconcile current truth, confirm the prerequisite MVP-0L completion or formal rebaseline, register permitted product/category/participant boundaries, human gates, evidence destinations and stop conditions. No Pilot run or Provider call is authorized by P0 itself.
2. **P1 — Minimal evidence readiness:** establish the smallest provider-free evidence and acceptance harness needed by the Contract. Characterize first; implement only a proven gap. Mock, fixture and fake evidence remain excluded from business acceptance.
3. **P2 — First permitted real-product run:** after P0/P1 review and any required human Gate, execute the first bounded permitted real-product or permitted sanitized-real-product run with real Provider evidence, one Task at a time, human Review and usable Markdown export. A failure is terminal for that attempt; no silent repair or retry is implied.
4. **P3 — Cohort and stability:** run the permitted **5–10 products** spanning at least **two categories**, and demonstrate at least **three consecutive end-to-end successes without production-code edits**. Use the P0-fixed approved-export denominator and the **80% approved-export completion** formula without inventing missing outcomes.
5. **P4 — Non-author clean-Mac acceptance:** have at least one non-author operator use the reviewed product on a clean/other Apple Silicon Mac, with the same local safety, human Review and export boundaries. The evidence must be reproducible and sanitized.
6. **P5 — Adoption and feedback:** obtain at least one adopted output and record operator feedback, limitations and observed blockers. Agent capability is permitted only after an observed Pilot blocker and only through a new bounded contract; it is not an autonomous-runtime or multi-agent prerequisite.
7. **P6 — Evidence pack, demo and final review:** assemble the sanitized evidence pack, defined metrics, a **2–4 minute** demo and the final Pilot Goal Review. The independent review decides whether the completion threshold is met; no automatic completion is inferred from a single run.

### 3. Pilot completion threshold

Pilot completion requires all Contract conditions: 5–10 permitted products backed by permitted real product material or permitted sanitized real-product material, at least two categories, at least one non-author operator, real Provider evidence, at least one adopted output, three consecutive end-to-end successes without production-code edits, **at least 80% approved-export completion**, clean/other Apple Silicon evidence, metrics, a sanitized evidence pack and a 2–4 minute demo. Before observation, P0 fixes the denominator as all P0-admitted product/attempt units, including a failure before export, and registers the formula only; the numerator is an admitted product/attempt yielding at least one human-approved immutable Marketing or Xiaohongshu export. No admitted unit is removed, reclassified or retried after observation to improve the ratio.

The threshold is a Goal completion criterion, not current evidence. Deterministic, mock, fixture or fake outputs may support harness characterization but never satisfy the business acceptance threshold.

### 4. Preserved boundaries and human gates

- The official DeepSeek API with model `deepseek-v4-pro` remains the only future real-AI contract. Each bounded paid execution or cohort needs a fresh exact-commit owner authorization specifying maximum tasks, calls, cost and stop rules; no authorization is inherited, and no G0 call is permitted.
- Acceptance uses permitted real product material or permitted sanitized real-product material only. The fictional “城市通勤双肩包” Anchor is engineering/L5 evidence only and never a Pilot business cohort. Real customer secrets, unapproved production data, platform actions, automatic publishing, Spider_XHS reuse, public deployment, login/RBAC/multi-user behavior and generic Agent Runtime remain out of scope.
- Agent capability may be considered only after an observed Pilot blocker, with a bounded Stage contract, an explicit consumer, independent review and no expansion to autonomous or multi-agent control.
- Stop for a scope expansion, a second active Stage, a second Issue for one outcome, a missing human Gate, evidence that is only mock/fixture/fake, a cleanup or Secret breach, a public-contract/migration/dependency change, or inability to use exact `luna-worker` for executable work.

## Reason

The owner-approved Pilot separates a future real-business validation from the still-active MVP-0L delivery and the held L5 authorization. A serial, evidence-first contract makes real adoption measurable while preserving deterministic foundation evidence as non-acceptance evidence.

## Impact

- The repository gains one durable successor Goal and one normative Pilot Contract with a truthful `ACCEPTED / NOT ACTIVE` state.
- MVP-0L, #335 and #336 remain the current execution truth; no prior authorization is resumed or consumed.
- Future Pilot Issues must identify a real consumer, one Stage, one observable outcome, evidence, human gates, rollback and stop conditions.
- No code, test, migration, public contract, dependency, runtime, Provider or Secret behavior is changed by G0.

## Relationships

- **Current active Goal:** [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md)
- **Successor Goal:** [Real Product-to-Brief Pilot](../goals/real-product-to-brief-pilot-goal.md)
- **Pilot Contract:** [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)
- **Session:** [Session-010](../sessions/session-010-real-product-to-brief-pilot.md)
- **Prior Decision:** [DEC-084](dec-084-apple-silicon-local-ai-web-app-goal.md)
- **L3 Decision:** [DEC-085](dec-085-docker-only-local-web-lifecycle.md)
- **Issue:** [#337](https://github.com/JettxonHo/ai-ecommerce-agent/issues/337)
- **Current L5:** [Issue #335](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335) / [PR #336](https://github.com/JettxonHo/ai-ecommerce-agent/pull/336)

## Amends / Preserves

- **Amends:** None.
- **Does not amend or supersede:** [DEC-084](dec-084-apple-silicon-local-ai-web-app-goal.md). Its accepted MVP-0L successor direction, L0→L6 order and local/Provider boundaries remain unchanged.
- **Preserves:** [DEC-039](dec-039-proportional-validation-and-review-governance.md), [DEC-071](dec-071-luna-worker-exclusive-implementation-routing.md), [DEC-072](dec-072-long-running-autonomy-and-agent-identity-governance.md), [DEC-081](dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md), [DEC-082](dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md), [DEC-084](dec-084-apple-silicon-local-ai-web-app-goal.md), [DEC-085](dec-085-docker-only-local-web-lifecycle.md), the terminal Fast Lane `GOAL_BLOCKED` record and `P5_REUSE_FROZEN`.

## Authorization Boundary

This Decision authorizes only the documentation formalization in Issue #337. It does not authorize Pilot P0, any product-runtime, Provider/model/platform network call or irreversible external behavior, `.env` or Secret access, real data ingestion, Docker/API/PostgreSQL/Web/browser runtime, code/tests/configuration/dependencies/lockfiles/migrations/OpenAPI, platform behavior, publishing, Agent capability or a change to the current MVP-0L / #335 / #336 execution state. Ordinary Git/GitHub docs workflow transport remains allowed. Later Pilot work requires the inactive-to-active Gate, an exact Stage contract and independent review.
