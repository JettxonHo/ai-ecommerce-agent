# DEC-087：终止重基线 MVP-0L 并激活 Real Product-to-Brief Pilot

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-29
- **Decision Type:** Product Delivery / Goal Governance / Terminal Rebaseline / Pilot Activation
- **Source:** 用户明确决定“批准建立上述 Rebaseline Issue；不要继续修补 MVP0L，也不要启动 Agent UI”，并由 [Issue #339](https://github.com/JettxonHo/ai-ecommerce-agent/issues/339) 持久记录本决定的精确状态、范围与 merge-effective Gate
- **Decision Session:** [Session-011](../sessions/session-011-mvp0l-terminal-rebaseline.md)
- **Amends:** [DEC-084](dec-084-apple-silicon-local-ai-web-app-goal.md) 的未完成 L5→L6 continuation；[DEC-086](dec-086-real-product-to-brief-pilot.md) 的 inactive prerequisite
- **Goals:** [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md) · [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md)
- **Pilot Contract:** [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)

## Context

### Facts

- Exact base for the docs-only rebaseline is `origin/main@2546efcbbc698a8ba276f6f2049c6c0c041d9af8`; PR #336 is merged and Issue #335 is closed.
- MVP-0L L0–L4 evidence remains accepted and unchanged. L4 remains `L4_OFFLINE_QUALIFIED_NO_JUSTIFIED_REPAIR`, with production diff zero and no Phase-B amendment.
- The single owner-authorized L5 run at exact head `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f` has terminal disposition `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS`. It made five ordered `deepseek-v4-pro` calls with retry/recovery `0/0`; validated candidates and the confirmed result passed, both immutable export gates failed, the UTF-8/download gate failed, and no export directory or Markdown file existed. No human usability judgment was possible.
- The L5 authorization is consumed. No retry, repair, substitution, top-up or further Provider run is authorized.
- L6 is `NOT_EXECUTED`. MVP-0L therefore cannot truthfully be marked `COMPLETE`.
- [DEC-086](dec-086-real-product-to-brief-pilot.md) already accepted the Pilot and its P0→P6 Contract, while requiring MVP-0L completion or an owner-approved formal rebaseline before activation.

### Observation

Continuing the unfinished L5→L6 path would treat a terminal no-export result as a repair backlog and delay validation of the actual business loop. Starting Agent UI would add a new product surface before real Product-to-Brief usefulness is established.

## Decision

### 1. Branch-pending and merge-effective states

On the Issue #339 implementation branch, the only truthful statuses are:

- MVP-0L: `REBASELINE_PENDING`;
- Real Product-to-Brief Pilot: `ACTIVATION_PENDING`;
- Pilot P0: `NOT_STARTED`.

Only after this reviewed documentation PR reaches `main` do the following states become effective:

- MVP-0L: `TERMINAL_INCOMPLETE_L5_FAILED`;
- Real Product-to-Brief Pilot: `ACTIVE`;
- Pilot P0: `READY_NOT_STARTED`.

The branch does not claim merge, Issue closure, P0 execution, cohort admission or business acceptance.

### 2. Terminal MVP-0L rebaseline

Amend DEC-084's unfinished L5→L6 continuation. Preserve all accepted L0–L4 evidence and the complete L5 terminal record, but do not continue repairing MVP-0L and do not describe it as `COMPLETE`. L6 remains `NOT_EXECUTED`; Agent UI remains frozen and unauthorized. No new Provider authorization is created.

### 3. Pilot activation without P0 execution

Amend DEC-086's inactive prerequisite through the owner-approved formal rebaseline. After this PR reaches `main`, the Pilot becomes the only `ACTIVE` Goal and P0 becomes `READY_NOT_STARTED`. Issue #339 does not execute P0, register products, categories, participants, evidence destinations, metrics or an approved-export denominator, and does not use real or sanitized-real product material.

The exact Pilot order remains **P0 → P1 → P2 → P3 → P4 → P5 → P6**. Only one Stage may be active at a time, and every later Stage retains its own Issue/PR, independent review and applicable human Gate.

### 4. Preserved acceptance denominator

The Pilot completion denominator is unchanged: before observation, P0 fixes all P0-admitted product/attempt units, including a failure before export, and registers the denominator/formula only. The numerator counts an admitted product/attempt only when it yields at least one human-approved immutable Marketing or Xiaohongshu Markdown export; both exports are not required unless separately accepted, and yielding both still counts once. No admitted unit may be removed, reclassified or retried after observation to improve the ratio. Completion still requires at least **80% approved-export completion** together with every other DEC-086/Contract condition.

### 5. P1 characterization target, not repair approval

Future P1 must carry the observed L5 post-confirm/no-export boundary as a provider-free characterization target. It is not an approved repair. P1 may establish whether a reproducible harness or product gap exists; it does not inherit a production-code change, Provider call, Secret access or retry. Any implementation waits for a proven gap and its own bounded contract.

## Alternatives Considered

### Continue repairing MVP-0L

Rejected. The single authorized L5 attempt is terminal and consumed; Issue #339 grants no retry or repair authorization.

### Mark MVP-0L complete and continue to L6

Rejected. The export and human-usability gates failed, and L6 was not executed.

### Start Agent UI before the Pilot

Rejected. Agent UI remains frozen until real business-loop evidence establishes a bounded consumer and a later explicit contract.

### Silently retry or top up L5

Rejected. It would violate the one-time Provider contract and hide the terminal failure.

## Consequences

- MVP-0L becomes a truthful terminal incomplete historical Goal only when this PR reaches `main`; its accepted foundation evidence remains usable without becoming a completion claim.
- The accepted Pilot becomes the sole active execution Goal only at that same merge-effective event; P0 is ready to receive a later contract but has not started.
- The no-export blocker remains visible as future provider-free characterization work, not a preselected cause or repair.
- Agent UI, L6, Provider/Secret actions, real inputs, cohort admission and Pilot evidence collection remain outside Issue #339.

## Relationships

- **Decision amended:** [DEC-084](dec-084-apple-silicon-local-ai-web-app-goal.md)
- **Decision amended:** [DEC-086](dec-086-real-product-to-brief-pilot.md)
- **Terminal Goal:** [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md)
- **Activated-after-merge Goal:** [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md)
- **Pilot Contract:** [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)
- **Session:** [Session-011](../sessions/session-011-mvp0l-terminal-rebaseline.md)
- **Terminal L5 Review:** [MVP-0L L5 DeepSeek live acceptance](../reviews/mvp0l-l5-deepseek-live-acceptance.md)
- **Issue:** [#339](https://github.com/JettxonHo/ai-ecommerce-agent/issues/339)

## Authorization Boundary

This Decision authorizes only Issue #339's exact 13-path documentation rebaseline and ordinary Git/GitHub workflow. It authorizes no code, tests, configuration, dependency or lockfile change, migration, OpenAPI/generated client, Docker/API/PostgreSQL/Web/browser runtime, Provider/model/platform network call, `.env` or Secret access, P0 execution, cohort data, real inputs, L6, Agent UI, publishing or irreversible external behavior. Future P0–P6 work requires its own exact Stage contract and independent review; Provider or Secret action also requires a new exact owner Gate.
