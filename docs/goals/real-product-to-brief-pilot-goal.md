# Real Product-to-Brief Pilot Goal

> **Status on this branch: `ACTIVATION_PENDING` · P0 `NOT_STARTED`** — only after the Issue #339 documentation PR reaches `main` does this Goal become `ACTIVE` and P0 become `READY_NOT_STARTED`. The same event makes [MVP-0L](mvp0-local-ai-web-app-delivery-goal.md) `TERMINAL_INCOMPLETE_L5_FAILED`; no P0 execution is part of this branch.
>
> **Authority:** [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md) · [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md) · [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md) · [Session-010](../sessions/session-010-real-product-to-brief-pilot.md) · [Session-011](../sessions/session-011-mvp0l-terminal-rebaseline.md) · [Issue #339](https://github.com/JettxonHo/ai-ecommerce-agent/issues/339)
>
> **Current prerequisite truth:** [Issue #335](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335) / [PR #336](https://github.com/JettxonHo/ai-ecommerce-agent/pull/336) is terminal `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` at exact head `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`; the one-time authorization is consumed, no export exists and no further run is authorized. L6 is `NOT_EXECUTED`; Agent UI remains frozen.

## 1. Goal outcome

After DEC-087's rebaseline becomes effective on `main`, validate one bounded, real Product-to-Brief business loop with a small operator cohort. The Pilot turns permitted product material into a human-reviewed Marketing Brief or Xiaohongshu Brief output (a second adapter output is optional unless separately accepted), observes whether at least one output is adopted, and records evidence that another operator can use the reviewed local product.

This is a successor validation Goal, not a claim that the deterministic foundation or failed L5 attempt passed. The normative boundaries and acceptance calculation are in the [Pilot Contract](../product/real-product-to-brief-pilot-contract.md).

## 2. Activation and operating rule

- On this branch the Goal is `ACTIVATION_PENDING` and P0 is `NOT_STARTED`; MVP-0L is `REBASELINE_PENDING`.
- Only after the reviewed Issue #339 documentation PR reaches `main` does the owner-approved formal rebaseline make this Goal `ACTIVE` and P0 `READY_NOT_STARTED`.
- Issue #339 does not execute P0, register cohort data, use real inputs, resume #335 / PR #336 or call a Provider.
- Pilot stages run serially. Only one Stage may be active at a time, and one Issue/PR delivers one observable outcome.
- The implementer uses exact `luna-worker` for executable work; the independent reviewer is Sol `ORCHESTRATOR_REVIEWER`. No Terra or Kimi fallback is implied.

## 3. Frozen Stage order

The exact Pilot order is **P0 → P1 → P2 → P3 → P4 → P5 → P6**. A later Stage is not created or started until the prior Stage's independently reviewed PR reaches `main`.

Every Pilot Stage uses the frozen lifecycle **Plan → Implementation → Automated Verification → Runtime / Browser Evidence（适用时）→ Independent Review → Owner Gate（适用时）**. The lifecycle sequences the Stage plan, bounded implementation, checks, applicable runtime/browser evidence, independent review and any required owner decision; it does not itself authorize a Provider, Secret, product-runtime, platform-network or irreversible external behavior.

### P0 — Pilot readiness and permitted-input gate

Reconcile the active prerequisite and the Pilot Contract. Register the permitted 5–10 product cohort, at least two categories, participant roles, human approval points, evidence locations, metric definitions, the approved-export denominator/formula and stop conditions. The denominator is fixed before observation; P0 registers denominator/formula only, not a future numerator. P0 has no Provider call and no business acceptance.

### P1 — Minimal evidence readiness

Build or verify only the smallest provider-free evidence and acceptance harness needed by the Contract. The observed L5 post-confirm/no-export boundary is a required characterization target: characterize first and implement only for a proven gap under a later bounded contract. It is not an approved repair or Provider retry. Mock, fixture and fake evidence can exercise the harness but are excluded from business acceptance. No speculative Agent Runtime, generic RAG or platform action is introduced.

### P2 — First permitted real-product run

After the P0/P1 gates and the required authorization, run the first permitted real-product or permitted sanitized-real-product material through the complete bounded Product-to-Brief path. Preserve real Provider evidence, human Review, usable Markdown export evidence and failure evidence under the Contract. A failed attempt is terminal; no silent retry, repair, substitution or scope widening follows.

### P3 — Cohort and three-run stability

Complete the permitted **5–10 product** cohort across at least **two categories** and demonstrate **three consecutive end-to-end successes without production-code edits**. Measure approved-export completion using the denominator and formula fixed in P0; all P0-admitted product/attempt units, including a failure before export, remain in that denominator and no numerator is invented or revised after observation.

### P4 — Non-author clean-Mac acceptance

Have at least one non-author operator use the reviewed product on a clean/other Apple Silicon Mac with the same local safety, human Review and export boundaries. Record reproducible sanitized evidence and operator-visible limitations.

### P5 — Adoption and feedback

Record at least one adopted output and structured operator feedback about usefulness, limitations and blockers. Agent capability is considered only after an observed Pilot blocker and only through a new bounded contract with a real consumer; it is not a prerequisite and does not authorize an autonomous or multi-agent runtime.

### P6 — Evidence pack, demo and final review

Assemble the sanitized evidence pack, agreed metrics, a **2–4 minute** demo and the final Pilot Goal Review. The independent review decides whether every completion condition, including the 80% threshold, is satisfied; no single successful run can close the Goal.

## 4. Completion criteria

Pilot completion requires all of the following:

- 5–10 permitted products backed by permitted real product material or permitted sanitized real-product material, spanning at least two categories; the fictional “城市通勤双肩包” Anchor is engineering/L5 evidence only and never a Pilot business cohort;
- at least one non-author operator on a clean/other Apple Silicon Mac;
- real Provider evidence for the business runs and at least one adopted output;
- at least three consecutive end-to-end successes without production-code edits;
- at least **80% approved-export completion**, calculated from the denominator fixed in P0 across all admitted product/attempt units, including failures before export; the numerator is an admitted product/attempt yielding at least one human-approved immutable Marketing or Xiaohongshu export;
- metrics, sanitized evidence pack and a 2–4 minute demo;
- independent final Pilot Goal Review with no unresolved blocking evidence or boundary breach.

Deterministic, mock, fixture or fake results are characterization evidence only and never satisfy the real business acceptance criteria. An automated success and human usability judgment remain separate.

## 5. Product, data and runtime boundary

The Pilot uses the existing local single-user Action Workbench and its accepted Task / Review / Markdown export semantics. The only future real-AI contract is the official DeepSeek API with `deepseek-v4-pro`; each bounded paid execution or cohort needs a fresh exact-commit owner authorization specifying maximum tasks, calls, cost and stop rules. No authorization is inherited. Inputs are permitted real product material or permitted sanitized real-product material; the fictional Anchor is engineering/L5 evidence only and never a Pilot business cohort. Secrets and unapproved customer data are never acceptance evidence.

The Pilot does not authorize public deployment, login/RBAC/multi-user behavior, Intel support, native App/WebView, Spider_XHS reuse or publishing, model/provider substitution, generic RAG, long-term memory, distributed workers, or an autonomous Agent Runtime. No `.env` or Secret value is inspected by G0.

## 6. Human gates and stop conditions

Stop and return to the owner for: activation before the prerequisite is complete/rebaselined; a Provider or Secret action without its exact Gate; real data or platform behavior outside the Contract; a second active Stage or duplicate Issue for one outcome; evidence that is only mock/fixture/fake; an unbounded retry or repair; public-contract, migration, dependency or product-direction change; a cleanup/security breach; or inability to use exact `luna-worker`.

## 7. Relationships

- **Decisions:** [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md) · [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md)
- **Pilot Contract:** [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)
- **Sessions:** [Session-010](../sessions/session-010-real-product-to-brief-pilot.md) · [Session-011](../sessions/session-011-mvp0l-terminal-rebaseline.md)
- **Activation Issue:** [Issue #339](https://github.com/JettxonHo/ai-ecommerce-agent/issues/339)
- **Terminal prerequisite:** [MVP-0L Local AI Web App Delivery Goal](mvp0-local-ai-web-app-delivery-goal.md)
- **Terminal L5:** [Issue #335](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335) / [PR #336](https://github.com/JettxonHo/ai-ecommerce-agent/pull/336)
- **Prior Goal decision:** [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md)

## 8. Authorization boundary

Issue #339 authorizes only the docs-only activation transition. On this branch Pilot is `ACTIVATION_PENDING` and P0 `NOT_STARTED`; after merge Pilot is `ACTIVE` and P0 only `READY_NOT_STARTED`. It authorizes no business code, tests, configuration, dependency or lockfile changes, migrations, OpenAPI/public contracts, Web/runtime actions, Docker/PostgreSQL/browser launch, product-runtime, Provider/model/platform network calls or irreversible external behavior, `.env`/Secret access, external publishing or Agent capability. Ordinary Git/GitHub docs workflow transport remains allowed. Every P0–P6 Stage still requires its own contract and independent review.
