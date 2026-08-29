# Real Product-to-Brief Pilot Contract

> **Status: ACCEPTED / NOT ACTIVE**
>
> This is the normative contract for the future [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md). It is authorized by [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md), recorded in [Session-010](../sessions/session-010-real-product-to-brief-pilot.md), and formalized by [Issue #337](https://github.com/JettxonHo/ai-ecommerce-agent/issues/337). It cannot be executed until the current [MVP-0L Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md) is `COMPLETE` or formally rebaselined by the owner.

## 1. Purpose and contract state

The Pilot validates a bounded real Product-to-Brief loop for a small ecommerce operator: permitted product material enters the existing local workbench, a real Provider produces the bounded stage outputs, a human reviews them, and at least one usable Marketing or Xiaohongshu Markdown export is available for adoption.

The contract is accepted but inactive. G0 is documentation-only and does not run P0, resume the held MVP-0L L5 work, consume the one-time authorization for [Issue #335](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335) / [PR #336](https://github.com/JettxonHo/ai-ecommerce-agent/pull/336), or call a Provider. The current #335 / #336 reviewed head is `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f` over `ef5ac0d4b372c1478ee2541ee3ec5318e72a1060`, and its authorization remains unconsumed because no Provider request has been made.

## 2. Admission and permitted material

- The cohort contains **5–10 permitted products backed by permitted real product material or permitted sanitized real-product material** and at least **two categories**. P0 records the exact admitted set before any cohort run.
- Acceptance material is permitted real product material or permitted sanitized real-product material that preserves the business task without exposing secrets or unapproved customer data. The fictional “城市通勤双肩包” Anchor is engineering/L5 evidence only and never a Pilot business cohort. Real customer credentials, cookies, account data and uncontrolled production material are not permitted.
- At least one operator is not the author/implementer. A non-author must complete the clean/other Apple Silicon Mac acceptance in P4.
- Each product has one bounded Task, one human Review decision and the existing Markdown export boundary. No unbounded matrix, second Task per attempt or automatic publishing is implied.

## 3. Required evidence and completion threshold

The Pilot cannot complete unless the evidence pack shows every condition below:

1. the admitted 5–10 products span at least two categories;
2. at least one non-author operator used the reviewed product on a clean/other Apple Silicon Mac;
3. business runs contain real Provider evidence under the exact approved Provider/model contract;
4. at least one Marketing or Xiaohongshu output was adopted by an operator, with the adoption context recorded;
5. at least three consecutive end-to-end successes occurred without production-code edits between those runs;
6. at least **80% approved-export completion** was achieved; and
7. the evidence includes defined metrics, a sanitized evidence pack, and a 2–4 minute demo, followed by independent final Goal Review.

### Approved-export calculation

Before observation begins, P0 fixes and registers the denominator and formula only: all P0-admitted product/attempt units, including any failure before export. P0 does not register or count a future numerator. The numerator counts an admitted product/attempt when it yields at least one human-approved immutable Marketing or Xiaohongshu Markdown export; both exports are not required unless separately accepted, and yielding both still counts once. The ratio is `qualifying admitted product/attempts / all P0-admitted product/attempts`, and it must be at least 80%. An admitted product/attempt may not be removed, reclassified or retried solely to improve the ratio. Missing, failed or ambiguous outcomes remain visible as denominator failures in the sanitized evidence.

Automated checks and human usability judgment are separate. Deterministic, mock, fixture or fake outputs may prove a harness seam but are excluded from the business numerator and denominator.

## 4. Frozen serial Stage contract

The exact order is **P0 → P1 → P2 → P3 → P4 → P5 → P6**. Only one Stage may be active at a time. One Issue/PR owns one observable outcome, and the next Stage waits for an independently reviewed prior PR to reach `main`.

### Frozen Stage lifecycle

Every Pilot Stage follows this exact lifecycle: **Plan → Implementation → Automated Verification → Runtime / Browser Evidence（适用时）→ Independent Review → Owner Gate（适用时）**. The Stage plan fixes scope and evidence; implementation stays within that plan; automated verification records checks; runtime/browser evidence is collected only when the Stage contract requires it; an independent reviewer evaluates the result; and an Owner Gate is required whenever the contract marks it applicable. A Stage does not advance on a missing step, and this lifecycle does not authorize a Provider, Secret, product-runtime, platform-network or irreversible external behavior by itself.

### P0 — Pilot readiness and permitted-input gate

Reconcile the current MVP-0L status or owner-approved formal rebaseline; register the cohort, categories, participants, evidence paths, metrics, approved-export denominator/formula and human/Provider gates. The denominator is fixed before observation; P0 registers denominator/formula only, not a future numerator. P0 performs no business run and no Provider call.

### P1 — Minimal evidence readiness

Use tests-first, provider-free characterization to establish the smallest evidence and acceptance harness. Implement only a proven gap. Mock/fixture/fake material is allowed for harness behavior but is never business acceptance evidence.

### P2 — First permitted real-product run

After P0/P1 review and the fresh exact-commit owner authorization, run one admitted permitted real-product or permitted sanitized-real-product product through the complete bounded Product-to-Brief path with real Provider evidence, human Review and Markdown export. Provider/access/timeout/transport/empty/invalid/schema/domain/export failure is terminal for that attempt; no retry, repair, substitution or top-up is implied.

### P3 — Cohort and three-run stability

Complete the 5–10 product, two-category cohort and prove three consecutive end-to-end successes without production-code edits. Capture every P0-admitted product/attempt outcome, including failures before export, and the registered 80% approved-export calculation.

### P4 — Non-author clean-Mac acceptance

Repeat a representative task with at least one non-author operator on a clean/other Apple Silicon Mac. Preserve only sanitized evidence and verify the same local safety, Review and export semantics.

### P5 — Adoption and feedback

Record at least one adopted output and structured operator feedback, including limitations and observed blockers. Agent capability may be proposed only after an observed Pilot blocker, with a new bounded contract and real consumer; it is not a prerequisite and does not authorize an autonomous or multi-agent runtime.

### P6 — Evidence pack, demo and final review

Produce the sanitized evidence pack, metrics, 2–4 minute demo and final independent Pilot Goal Review. The reviewer decides completion; no automated or single-run result closes the Goal.

## 5. Runtime, Provider and human gates

- The only future real-AI contract is the official DeepSeek API with model `deepseek-v4-pro`. Each bounded paid execution or cohort needs a fresh exact-commit owner authorization specifying maximum tasks, calls, cost and stop rules; no authorization is inherited from MVP-0L or G0.
- Secrets use only the later project-root Git-ignored `.env` convention, checked under a separately approved Gate. Values are never printed, measured, hashed, persisted, sent to the browser, or included in evidence.
- The existing fixed local single-user Workbench, Task scope, human Review, safe Markdown and loopback boundaries remain authoritative.
- No Provider/model substitution, fallback, unbounded retry, public deployment, platform request, automatic publishing, Spider_XHS reuse, Intel support, native App/WebView, login/RBAC/multi-user behavior, generic RAG, long-term memory, distributed Worker or autonomous Agent Runtime is part of this Contract.

## 6. Stop conditions

Stop and return to the owner if: the prerequisite is not complete/rebaselined; a human Gate is missing; a Secret or real data boundary is unclear; a provider outcome is ambiguous; the approved-export denominator would be changed after observation; a second active Stage or duplicate Issue appears; a mock/fixture/fake result is proposed as business evidence; a production-code edit occurs during the three-run stability window; cleanup fails; or the work needs a public contract, migration, dependency, product-direction, platform or Agent Runtime expansion.

## 7. Relationships

- **Decision:** [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md)
- **Goal:** [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md)
- **Session:** [Session-010](../sessions/session-010-real-product-to-brief-pilot.md)
- **Activation Issue:** [Issue #337](https://github.com/JettxonHo/ai-ecommerce-agent/issues/337)
- **Current active prerequisite:** [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md)
- **Current held L5:** [Issue #335](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335) / [PR #336](https://github.com/JettxonHo/ai-ecommerce-agent/pull/336)

## 8. Authorization boundary

This contract records an accepted future Pilot and does not itself authorize execution. Issue #337 authorizes only the eleven-path documentation change. Any P0–P6 implementation, product-runtime, Provider/model/platform network call or irreversible external behavior, Secret access, real-data handling, runtime launch, code/test/configuration/dependency/migration/public-contract change or Agent capability requires the inactive-to-active prerequisite and its own exact Stage contract and human/independent Review gates. Ordinary Git/GitHub docs workflow transport remains allowed.
