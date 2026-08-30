# Session-012：Real Product-to-Brief Pilot P0 Admission and Contract Freeze

## Metadata

- **Status:** Concluded
- **Date:** 2026-08-30
- **Topic:** Freeze the exact P0 cohort, denominator, participant role, human-review schema and private evidence boundary before any Pilot observation
- **Issue:** [#341](https://github.com/JettxonHo/ai-ecommerce-agent/issues/341)
- **Decisions:** [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md) · [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md)
- **Goal:** [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md)
- **Pilot Contract:** [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)
- **P0 plan:** [Real Product-to-Brief Pilot P0 Plan](../product/real-product-to-brief-pilot-p0-plan.md)
- **Base / branch:** `origin/main@c4abd604347b3033b6bb9f6dbfc1272e7ff635ac` / `codex/mbl-pilot-p0-contract-freeze`
- **Configuration evidence:** `CONFIG_VERIFIED` — `/Users/ketchup/.codex/agents/luna-worker.toml` parsed with Python 3.12 as `luna-worker` / `gpt-5.6-luna` / `max`; runtime identity was not inferred

## Context and authorization

Issue #341 is the single P0 admission/contract-freeze Issue. The Owner supplied the required evidence and workflow authorization in comments [5462712363](https://github.com/JettxonHo/ai-ecommerce-agent/issues/341#issuecomment-5462712363), [5462825047](https://github.com/JettxonHo/ai-ecommerce-agent/issues/341#issuecomment-5462825047), [5467295279](https://github.com/JettxonHo/ai-ecommerce-agent/issues/341#issuecomment-5467295279), and [5467339162](https://github.com/JettxonHo/ai-ecommerce-agent/issues/341#issuecomment-5467339162). The authorization covers the exact seven-path P0 admission/denominator/contract-freeze docs workflow and conditional merge. It does not authorize Pilot execution.

The Owner-authorized private artifacts were read only for structural admission validation:

- `/Users/ketchup/Private/ai-ecommerce-pilot/inputs/p0-admission-manifest-draft.yaml`
- `/Users/ketchup/Private/ai-ecommerce-pilot/inputs/p0-source-index.md`

No private directory was created, no other private artifact was read, and no protected image, long marketing passage, credential, cookie, Secret, personal data or raw Provider payload entered the repository.

## Facts

- The merge-effective prerequisite state from DEC-087 is current: MVP-0L is `TERMINAL_INCOMPLETE_L5_FAILED`, the Pilot is `ACTIVE`, and P0 is ready for a separately bounded contract.
- The exact Owner-selected cohort is P01–P08, split into Category A consumer electronics / digital accessories (P01–P04) and Category B daily consumer goods / lifestyle goods (P05–P08), four each.
- The eight identities and variant designations are frozen in the [P0 plan](../product/real-product-to-brief-pilot-p0-plan.md): Anker A1259 Black Stone `42733233766550`; Sony WF-1000XM5 Black/US `WF1000XM5/B`; IKEA BERGENES `104.579.99`; Apple MXK83LL/A US English/Black Keys; Zojirushi SU-BA48-BM Midnight Black; IKEA SAMLA composite `694.407.61`; IKEA KNALLA `602.823.32`; and The North Face Borealis 28L `NF0A52SE / 4HF / OS`.
- F1–F9 are structurally present for all eight samples. The 22 unique source IDs referenced by F4/F7/F8 all resolve in the private source index.
- F5 and F6 are owner-approved in comment 5467295279. The per-sample permission basis is owner-approved; `sanitization_status = NOT_REQUIRED` is valid only for approved public facts, paraphrased text and structured fields.
- Every explicit `UNVERIFIED` field remains restricted by `UNVERIFIED -> CLAIM NOT ALLOWED`; it is not silently inferred or promoted to a marketing claim.
- `non_author_trial_operator_01 = CONFIRMED_AND_CONSENTED` is confirmed in comment 5467339162. Only the sanitized role/status is retained; no name, contact information or PII is recorded.

## Observation

Before this workflow, the repository had no P0 plan or Session-012 and its current-truth surfaces did not claim frozen P0 admission, an exact eight-unit denominator, `P0_CONTRACT_FROZEN`, or the cleared non-author participant. This was captured as the required documentation RED on unchanged `c4abd604` before any edit.

## Accepted P0 freeze

The [P0 plan](../product/real-product-to-brief-pilot-p0-plan.md) is the normative sanitized record for this Issue. It freezes:

1. exact `N = 8`, two categories at 4+4, eight product/attempt units and one score-bearing outcome per unit;
2. the approved-export formula with an `>= 80%` threshold, count-once semantics and no numerator during P0 (`7/8 = 87.5%` is the smallest passing count; `6/8 = 75%` does not pass);
3. `PASS`, `FAIL`, `BLOCKED` and pre-observation-only `EXCLUDED` meanings, including `BLOCKED` remaining in the denominator;
4. no outcome-driven replacement, removal, retry or reclassification after denominator lock;
5. the complete reviewed/sanitized F5/F6 content, per-sample source references/counts, permission/sanitization status and `UNVERIFIED` restrictions;
6. the author/operator and confirmed non-author role;
7. seven human-review dimensions plus reviewer metadata, automated-evidence separation and per-sample evidence fields;
8. the private roots `/Users/ketchup/Private/ai-ecommerce-pilot/{inputs,evidence,reviews,exports,summary}/`, all outside Git, with no directories created by this workflow;
9. the sole P1 handoff `post-confirm / no-export blocker` as a provider-free characterization target.

The accepted Pilot Contract, DEC-086, DEC-087, Session-010, Session-011 and the L5 review are preserved byte-for-byte. No product code, tests, Provider, Secret, runtime, observation, numerator, export, participant test, P1/P2, MVP0L repair/L5 retry, L6, Agent UI or platform action is performed or authorized.

## Merge-durable statuses

The text is written as a state transition so it remains truthful after merge:

| Location of this record | P01–P08 | Denominator | P0 | Pilot | P1 |
|---|---|---|---|---|---|
| Before this PR reaches `main` | `ADMISSION_PENDING_REVIEW` | `FREEZE_PENDING_REVIEW` | `CONTRACT_FREEZE_PENDING` | `ACTIVE` | not started |
| Once this record is present on `main` | `ADMITTED` | exact eight frozen | `P0_CONTRACT_FROZEN` | `ACTIVE` | `READY_NOT_STARTED` |

`PILOT_EXECUTION_AUTHORIZATION` remains `NOT_AUTHORIZED` in both states. The merge does not start a business run.

## Validation and archive result

- Exact seven-path scope: `AGENTS.md`, `README.md`, `docs/goals/README.md`, `docs/goals/real-product-to-brief-pilot-goal.md`, `docs/product/real-product-to-brief-pilot-p0-plan.md`, `docs/handoffs/implementation-readiness.md`, and this Session-012 only.
- Documentation RED was captured first on the clean unchanged base; the plan and this session then supplied the minimal GREEN current-truth record.
- Cohort uniqueness, category counts, F1–F9 completeness, 22-source resolution, F5/F6 approval integrity, denominator/order/threshold semantics, participant role, links, headings, fences, stale-wording checks and `git diff --check` are required merge evidence.
- The implementer does not independently review, approve or merge. A fresh Required Checks run and an independent review remain required before the record becomes merge-effective.

## Relationships

- **Decisions:** [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md) · [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md)
- **Goal:** [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md)
- **Pilot Contract:** [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)
- **Issue:** [#341](https://github.com/JettxonHo/ai-ecommerce-agent/issues/341)
