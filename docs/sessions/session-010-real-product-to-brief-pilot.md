# Session-010：Real Product-to-Brief Pilot 合同归档

## Metadata

- **Status:** Concluded
- **Date:** 2026-08-29
- **Topic:** 记录一个接受但暂不激活的 Real Product-to-Brief Pilot successor Goal、G0 docs-only 边界与 P0→P6 串行合同
- **Issue:** [#337](https://github.com/JettxonHo/ai-ecommerce-agent/issues/337)
- **Decision:** [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md)
- **Goal:** [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md)
- **Pilot Contract:** [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)
- **Current active Goal:** [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md)
- **Current held L5:** [Issue #335](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335) / [PR #336](https://github.com/JettxonHo/ai-ecommerce-agent/pull/336)
- **Base / branch:** `origin/main@ef5ac0d4b372c1478ee2541ee3ec5318e72a1060` / `codex/real-product-to-brief-pilot-g0`
- **Configuration evidence:** `CONFIG_VERIFIED` — exact `luna-worker` / `gpt-5.6-luna` / `max` from `/Users/ketchup/.codex/agents/luna-worker.toml` parsed with Python 3.12; runtime metadata was not exposed, so no runtime identity is inferred.

## Context

### Facts

- MVP-0L remains `ACTIVE` and is the only active Goal. Its accepted order is L0 → L1 → L2 → L3 → L4 → L5 → L6.
- The current L5 boundary is #335 / PR #336 at exact reviewed head `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f` over base `ef5ac0d4b372c1478ee2541ee3ec5318e72a1060`. The owner authorization exists, but no Provider request has been made; the one-time authorization is unconsumed.
- DEC-084 and DEC-085 remain Accepted. This Session does not amend or supersede either Decision.
- The repository already has deterministic pipeline, DeepSeek, Task HTTP/Web and migrations 0007–0009 implementation surfaces. G0 changes none of them.
- On 2026-08-29 the owner explicitly approved the proposed Pilot Goal, boundaries, non-goals, 80% approved-export completion threshold and serial execution order.

### Observations

- A future real-business validation needs a separate evidence and adoption contract so deterministic foundation evidence cannot be mistaken for real-provider acceptance.
- Starting the Pilot while MVP-0L is incomplete would create competing execution entries and could be read as permission to resume the held L5 work.

### Assumptions

- The permitted cohort, participant identities and approved-export denominator will be registered before any future Pilot run in P0. This is a contract requirement, not current evidence.
- Any future real Provider result can be retained only through the sanitized evidence and export boundaries approved by its exact Stage contract.

## Goal

Archive the owner-approved successor Pilot as `ACCEPTED / NOT ACTIVE`, keep MVP-0L as the sole active Goal, and define an evidence-first P0→P6 path that can later measure real Product-to-Brief usefulness and adoption.

## Non-goals

- No activation of Pilot P0 while MVP-0L is `ACTIVE` and incomplete; no resumption or consumption of #335 / PR #336 authorization.
- No business code, tests, configuration, dependency/lockfile, migration, OpenAPI/public-contract or Web/UI change.
- No product-runtime, Provider/model/platform network call or irreversible external behavior, Docker/API/PostgreSQL/browser runtime, `.env` or Secret access, real-data ingestion, external platform action or publishing. Ordinary Git/GitHub docs workflow transport remains allowed.
- No autonomous Agent Runtime, Multi-Agent Runtime, generic RAG, long-term memory, model routing or speculative infrastructure.
- No Terra or Kimi fallback, and no amendment or rewrite of DEC-084/085 or historical Fast Lane/L4 facts.

## Existing Constraints

- Only one Goal may be `ACTIVE`; this Pilot remains inactive until MVP-0L is `COMPLETE` or formally rebaselined by the owner.
- Only one Stage may be active at a time, and one Issue/PR must deliver one observable outcome with independent review before the next Stage.
- Every Pilot Stage follows the frozen lifecycle **Plan → Implementation → Automated Verification → Runtime / Browser Evidence（适用时）→ Independent Review → Owner Gate（适用时）**; the sequence does not itself authorize product-runtime, Provider, Secret, platform-network or irreversible external behavior.
- The future real-AI contract is official DeepSeek `deepseek-v4-pro`; each bounded paid execution or cohort needs a fresh exact-commit owner authorization specifying maximum tasks, calls, cost and stop rules, with no inherited authorization.
- Pilot business acceptance requires 5–10 permitted products backed by permitted real product material or permitted sanitized real-product material across at least two categories, a non-author operator, real Provider evidence, at least one adopted output, three consecutive end-to-end successes without production-code edits, at least 80% approved-export completion, clean/other Apple Silicon evidence, metrics, a sanitized evidence pack and a 2–4 minute demo. P0 fixes the denominator before observation across all P0-admitted product/attempt units, including a failure before export; the numerator is an admitted product/attempt yielding at least one human-approved immutable Marketing or Xiaohongshu export. The fictional Anchor is engineering/L5 evidence only and never a Pilot business cohort.
- Mock, fixture and fake evidence may characterize a harness but is excluded from business acceptance.

## Questions to Resolve

- P0 must register the exact permitted product cohort, participant roles, evidence locations, metric definitions and approved-export denominator/formula before activation; the denominator covers all P0-admitted product/attempt units and is fixed before observation, while P0 registers no future numerator.
- P1 must determine whether a real harness gap exists; implementation is allowed only for a proven gap under a new Stage contract.
- P5 must record observed blockers before any bounded Agent capability proposal; no capability is presumed.

## Discussion

### Proposals

- **Proposal:** accept a successor Real Product-to-Brief Pilot Goal and normative Contract, but mark both `ACCEPTED / NOT ACTIVE` until MVP-0L completion or formal rebaseline.
- **Proposal:** use G0 as docs-only formalization, then execute P0→P6 serially with evidence and human gates separating characterization, provider runs, adoption and final review.

### Alternatives

1. Activate the Pilot immediately and pause MVP-0L: rejected; it violates the single-active-Goal rule and risks consuming the held L5 authorization.
2. Treat deterministic or fixture outputs as Pilot business acceptance: rejected; they cannot establish real Provider evidence or adoption.
3. Resume #335 / PR #336 from G0: rejected; G0 does not alter its exact contract or one-time authorization state.
4. Add an autonomous Agent Runtime before observing a blocker: rejected; capability is allowed only after an observed Pilot blocker and a new bounded contract.

### Trade-offs

- Deferring activation keeps the current release and L5 truth unambiguous, at the cost of postponing Pilot evidence.
- A small cohort and 80% threshold make adoption measurable without implying a broad production claim; the denominator must be fixed before observation.
- Serial Issues reduce parallel scope drift but require each Stage to earn its next contract through independent review.

### Risks

- A stale summary could call the Pilot `ACTIVE` or call MVP-0L complete; all Current Truth updates must retain the explicit inactive state.
- Provider, Secret, real-data or platform actions could be inferred from a future Pilot label; each remains a separate human Gate.
- A late denominator change, production-code edit during stability runs or mock evidence presented as business evidence would invalidate the completion claim.

## Proposed Decisions

- [Proposed] Create DEC-086, the `ACCEPTED / NOT ACTIVE` Real Product-to-Brief Pilot Goal and its normative Contract with P0→P6 semantics — submitted for owner confirmation on 2026-08-29.

## Accepted Decisions

- [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md) — owner accepted the successor Pilot, boundaries, 80% approved-export threshold and P0→P6 serial order on 2026-08-29.
- [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md) — `ACCEPTED / NOT ACTIVE`; activation waits for MVP-0L `COMPLETE` or formal owner-approved rebaseline.
- [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md) — normative future contract; G0 does not execute it.
- MVP-0L remains the only `ACTIVE` Goal; #335 / PR #336 remains current held L5 at `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`, with one-time authorization unconsumed.

## Rejected Approaches

- Immediate Pilot activation before MVP-0L completion.
- Reopening the held L5 run or treating G0 as inherited Provider authorization.
- Calling deterministic, mock, fixture or fake output real business evidence.
- Pre-creating or parallelizing P0–P6 Issues without a reviewed prior Stage and a real consumer.

## Open Questions

- The exact cohort, participants, denominator and metric collection locations remain to be registered in P0.
- Whether an Agent capability is needed remains unknown until a blocker is observed; no capability is authorized now.
- Any future provider pricing, call count, or data-retention detail must be accepted in the relevant exact Stage contract; G0 does not infer it.

## Deferred Topics

- Pilot activation and all P0–P6 execution.
- Any Agent capability, broader cohort, production deployment, platform action or autonomous runtime.

## Documentation Updates

The owner-approved decision is synchronized across exactly the Issue #337 allowlist: `AGENTS.md`, `README.md`, [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md), the [Decision Log](../decisions/decision-log.md), [Goals README](../goals/README.md), the [MVP-0L Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md), the [Pilot Goal](../goals/real-product-to-brief-pilot-goal.md), [MVP Scope](../product/mvp-scope.md), [Implementation Readiness](../handoffs/implementation-readiness.md), this Session, and the [Pilot Contract](../product/real-product-to-brief-pilot-contract.md). No production or runtime path is changed.

## Synchronization Checklist

- [x] Facts, Observations, Assumptions, Proposals, Alternatives, Trade-offs, Risks, Open Questions and Deferred Topics are separated.
- [x] DEC-086 records the owner's explicit 2026-08-29 approval and is registered once in the Decision Log.
- [x] The Pilot Goal and Contract are `ACCEPTED / NOT ACTIVE`; MVP-0L remains the only `ACTIVE` Goal.
- [x] #335 / PR #336 exact head and unconsumed one-time authorization are preserved; G0 does not resume it.
- [x] P0→P6 order, one-active-Stage and one-Issue-per-observable-outcome rules are recorded.
- [x] The 5–10 products / two categories / non-author / real Provider / adopted output / three-run / 80% / clean-Mac / metrics / evidence-pack / demo criteria are recorded.
- [x] Mock, fixture and fake evidence are excluded from business acceptance; Agent capability is gated on an observed blocker.
- [x] Relative Decision ↔ Goal ↔ Contract ↔ Session ↔ current MVP0L links are retained.
- [x] No product-runtime, Provider/model/platform network or irreversible external behavior was performed; ordinary Git/GitHub docs workflow transport is allowed.
