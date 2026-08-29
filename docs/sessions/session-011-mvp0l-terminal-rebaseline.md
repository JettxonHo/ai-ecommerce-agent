# Session-011：MVP-0L 终止重基线与 Pilot 激活

## Metadata

- **Status:** Concluded
- **Date:** 2026-08-29
- **Topic:** 记录 MVP-0L terminal incomplete rebaseline、Real Product-to-Brief Pilot merge-effective activation 与 P0 未执行边界
- **Issue:** [#339](https://github.com/JettxonHo/ai-ecommerce-agent/issues/339)
- **Base / branch:** `origin/main@2546efcbbc698a8ba276f6f2049c6c0c041d9af8` / `codex/mbl-pilot-rb0-rebaseline`
- **Decision:** [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md)
- **MVP-0L Goal:** [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md)
- **Pilot Goal:** [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md)
- **Pilot Contract:** [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)
- **Routing:** requested dispatch configuration `gpt-5.6-sol` / `xhigh`; logical role `SOL_DOCS_IMPLEMENTER`; no separate runtime identity inferred; owner amendment is limited to Issue #339's docs-only 13-path scope

## Facts

- PR #336 is merged and Issue #335 is closed.
- L0–L4 accepted evidence is preserved. L5 is terminal `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` at `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`: five ordered `deepseek-v4-pro` calls, retry/recovery `0/0`, validated candidates and confirmed result true, export gates false, UTF-8/download false and no export file.
- The L5 authorization is consumed and no further Provider run is authorized.
- L6 is `NOT_EXECUTED`; Agent UI remains frozen.
- The owner explicitly approved a formal rebaseline and explicitly directed that MVP0L not be repaired further and Agent UI not be started.
- DEC-086 already accepted the Pilot, exact P0→P6 order and approved-export denominator, but kept it inactive until MVP-0L completion or formal rebaseline.

## Observation

The repository must distinguish branch-pending documentation from merge-effective Goal state. It must also preserve the historical held/unconsumed wording in Session-010 as history while removing it from current-truth surfaces.

## Accepted Decision

[DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md) records the owner's accepted rebaseline:

- on this branch: MVP-0L `REBASELINE_PENDING`, Pilot `ACTIVATION_PENDING`, P0 `NOT_STARTED`;
- only after this PR reaches `main`: MVP-0L `TERMINAL_INCOMPLETE_L5_FAILED`, Pilot `ACTIVE`, P0 `READY_NOT_STARTED`;
- preserve L0–L4 and exact L5 failure/no-export evidence;
- leave L6 `NOT_EXECUTED`, Agent UI frozen and Provider authorization absent;
- carry the post-confirm/no-export blocker into future P1 as a provider-free characterization target, not an approved repair;
- preserve the exact P0→P6 order and denominator semantics.

## Rejected Approaches

- Continue repairing or retrying MVP-0L L5.
- Mark MVP-0L `COMPLETE` or execute L6.
- Start Agent UI before a real Pilot blocker identifies a bounded consumer.
- Execute P0, register cohort data or use real inputs in Issue #339.
- Treat the observed no-export result as proof of a specific cause or pre-approve a production repair.

## Exact Documentation Contract

Issue #339 changes exactly these 13 tracked paths:

1. `AGENTS.md`
2. `README.md`
3. `apps/web/README.md`
4. `docs/decisions/dec-086-real-product-to-brief-pilot.md`
5. `docs/decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md`
6. `docs/decisions/decision-log.md`
7. `docs/goals/README.md`
8. `docs/goals/mvp0-local-ai-web-app-delivery-goal.md`
9. `docs/goals/real-product-to-brief-pilot-goal.md`
10. `docs/product/mvp-scope.md`
11. `docs/product/real-product-to-brief-pilot-contract.md`
12. `docs/handoffs/implementation-readiness.md`
13. `docs/sessions/session-011-mvp0l-terminal-rebaseline.md`

Historical [Session-010](session-010-real-product-to-brief-pilot.md) and the [L5 terminal review](../reviews/mvp0l-l5-deepseek-live-acceptance.md) remain byte-identical. No code, test, configuration, dependency/lock, migration, OpenAPI/generated file or runtime path changes.

## Pilot Contract Preservation

The exact order remains **P0 → P1 → P2 → P3 → P4 → P5 → P6**. Before observation, P0 fixes all P0-admitted product/attempt units, including a failure before export, and registers the denominator/formula only. The numerator requires at least one human-approved immutable Marketing or Xiaohongshu Markdown export from an admitted unit; both exports are not required unless separately accepted, and yielding both still counts once. No admitted unit is removed, reclassified or retried after observation to improve the ratio. The threshold remains at least 80% plus every other Contract condition.

## Archive Result

- **Branch status:** MVP-0L `REBASELINE_PENDING`; Pilot `ACTIVATION_PENDING`; P0 `NOT_STARTED`.
- **Merge-effective status:** only after the PR reaches `main`, MVP-0L `TERMINAL_INCOMPLETE_L5_FAILED`; Pilot `ACTIVE`; P0 `READY_NOT_STARTED`.
- **Execution:** no P0, cohort, real input, Provider, Secret, runtime, L6 or Agent UI action.
- **Traceability:** DEC-087 amends DEC-084's unfinished continuation and DEC-086's inactive prerequisite without rewriting the historical decisions or sessions.

## Relationships

- **Decision:** [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md)
- **Prior Decisions:** [DEC-084](../decisions/dec-084-apple-silicon-local-ai-web-app-goal.md) · [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md)
- **MVP-0L Goal:** [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md)
- **Pilot Goal:** [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md)
- **Pilot Contract:** [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)
- **L5 Review:** [MVP-0L L5 DeepSeek live acceptance](../reviews/mvp0l-l5-deepseek-live-acceptance.md)
- **Issue:** [#339](https://github.com/JettxonHo/ai-ecommerce-agent/issues/339)
