# Session-013: Real Product-to-Brief Pilot P1 post-confirm/export characterization

## Metadata

- **Status:** `P1_CHARACTERIZATION_IN_PROGRESS` on this branch; merge-durable result is recorded below.
- **Date:** 2026-08-30
- **Issue:** [#343](https://github.com/JettxonHo/ai-ecommerce-agent/issues/343)
- **Base:** `origin/main@4429b6d28a7eb71ffcf26e07ca37de851cf87ebd`
- **Branch:** `codex/mbl-pilot-p1-post-confirm-no-export`
- **Implementer configuration:** `CONFIG_VERIFIED` — `/Users/ketchup/.codex/agents/luna-worker.toml` parsed with Python 3.12 as `luna-worker` / `gpt-5.6-luna` / `max`; runtime identity was not inferred.
- **Authority:** [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md) · [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md) · [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md) · [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md) · [P0 plan](../product/real-product-to-brief-pilot-p0-plan.md) · [Session-012](session-012-real-product-to-brief-pilot-p0.md)

## Context and authorization

### Facts

- Issue #341 / PR #342 is merge-effective: P01–P08 are `ADMITTED`, the denominator is exactly eight frozen product/attempt units, P0 is `P0_CONTRACT_FROZEN`, and the Pilot is `ACTIVE`.
- The P1 target is the observed `post-confirm / no-export blocker`. It is a provider-free characterization target, not an approved repair or a Provider retry.
- `PILOT_EXECUTION_AUTHORIZATION = NOT_AUTHORIZED`. No P01–P08 material, participant, business run, numerator, real input, Provider, Secret, browser, runtime, PostgreSQL or export artifact is authorized here.

### Direct PRE-EDIT checkpoint

Before the first file edit, the checkout was clean at exact
`HEAD=4429b6d28a7eb71ffcf26e07ca37de851cf87ebd`, equal to `origin/main`, on the
dedicated branch above. The seven-path allowlist was fixed: `AGENTS.md`,
`README.md`, the new characterization test, the Goal, this implementation
readiness handoff, the new review and this Session. No production source or
external resource would be changed or opened.

## Historical evidence and RED

### Facts

The sanitized L5 record at
`/private/tmp/ai-ecommerce-issue335-l5-final2.aodiRX/evidence.json` records five
ordered calls at exact run commit
`2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`, zero retry/recovery, validated
candidates and confirmed result true, both immutable-export gates false,
UTF-8/download false, and no export files. It intentionally has no raw
candidate, response, traceback, finish reason or failed checkpoint.

The legacy vector is therefore:

```text
validated_candidates = true
confirmed_result = true
marketing_export_immutable = false
xiaohongshu_export_immutable = false
downloads_utf8_no_bom_one_final_lf = false
```

### Observation — characterization RED

The first tests-only assertion (before the final driver) attempted to select one
failure from that vector and failed on unchanged production:

```text
uv run --offline --project apps/backend python -m pytest \
  apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py -q
1 failed in 0.01s
AssertionError: (True, True, False, False, False)
assert 7 == 1
```

The RED proves the historical aggregate is not a unique checkpoint attribution.

## Characterization method

### Facts

The final test-only driver injects interface-shaped fakes into the real FastAPI
HTTP adapter. It exercises exactly:

1. `POST /api/v1/tasks/{taskId}/commands/confirm-current-result`
2. `POST /api/v1/tasks/{taskId}/export-previews`
3. `POST /api/v1/export-snapshots`
4. `GET /api/v1/export-snapshots/{exportSnapshotId}/content`

It runs one normal provider-free path and one injected failure at each ordered
checkpoint:

```text
CONFIRM
PREVIEW_MARKETING
SNAPSHOT_MARKETING
DOWNLOAD_MARKETING
PREVIEW_XIAOHONGSHU
SNAPSHOT_XIAOHONGSHU
DOWNLOAD_XIAOHONGSHU
DISTINCT_SNAPSHOT_IDS
UTF8_VALIDATE_MARKETING
UTF8_VALIDATE_XIAOHONGSHU
OUTSIDE_REPO_PRESERVE
COMPLETE
```

For every failure the driver records only `failed_stage`, optional
`brief_kind`, `last_completed_stage`, ordered operation names and generic
status/problem metadata. Equality with the expected operation prefix proves no
later operation executes. UTF-8/BOM/final-line-feed and outside-repository
preservation remain harness checks after content download; the latter is not an
HTTP endpoint. No production helper is imported, and no content is retained in
the metadata record.

### Observation — final GREEN

```text
uv run --offline --project apps/backend python -m pytest \
  apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py -q
14 passed in 0.33s
```

The seven post-confirm preview/snapshot/download/distinct-ID failures produce
the exact historical vector; `CONFIRM` differs because confirmation is false,
and UTF-8/preservation failures happen after immutable gates have turned true.

## Result and interpretation

### Disposition: `INCONCLUSIVE`

The historical no-export occurrence is confirmed as a sanitized record, but its
exact root cause is unlocatable. Seven distinct post-confirm checkpoints are
compatible with the same legacy vector, while the normal public path passes.
No production defect is reproduced or excluded for future Provider output.

### Pilot impact

An admitted product/attempt that reaches the same condition can finish without
a qualifying approved immutable export and therefore remains in the fixed P0
denominator as `FAIL` or `BLOCKED` under the later exact outcome contract. This
Session performs no Pilot run, outcome classification or numerator calculation.

### Repair boundary

`REPAIR_REQUIRED = NO`. No production repair is justified or implemented.

**Proposal (not accepted):** a later owner-gated evidence-only Issue may add
sanitized `failed_stage`, optional `brief_kind`, `last_completed_stage` and
generic `problem_type` to a future run record. It must not retain raw Provider
payload, prompt, reasoning, Secret or personal data. This is an attribution
proposal, not a product-logic repair.

## Validation and archive result

The focused provider-free suites passed:

```text
73 passed — HTTP confirm, export preview/snapshot/download contracts, Markdown
renderer, export values and L5 control/preservation tests.

28 passed — HTTP/export architecture boundaries, import contracts and provider
SDK-consumer boundary checks.

0 errors, 0 warnings, 0 informations — Pyright for production source plus the
new characterization test.

Ruff format --check — one file already formatted.
Ruff check — all checks passed.
git diff --check — PASS.
```

The live smoke module and PostgreSQL integration path were inspected but not
selected. Existing persisted preview/snapshot/download tests supply the
provider-free persistence evidence; a fresh PostgreSQL run was not necessary
and would add no attribution signal. No retry, rerun, alternate scope, raw
Compose lifecycle, Provider or Secret action occurred.

Exactly seven paths are in scope; there is no eighth path. DEC-086/087, the
Pilot Contract, P0 plan and Session-012, production source, live smoke/evidence
schema, dependencies/locks, migrations/OpenAPI/generated client, Web code and
private artifacts remain byte-identical.

## Merge-durable statuses and next action

Before this PR reaches `main`:

```text
P1_CHARACTERIZATION_IN_PROGRESS
PILOT_EXECUTION_AUTHORIZATION = NOT_AUTHORIZED
```

If the independently reviewed PR reaches `main`, its exact disposition is
`INCONCLUSIVE`; P0 remains frozen, no Provider acceptance is inferred, and P2
still requires a separate exact-commit Owner authorization and Issue. The next
one action is independent Sol five-axis review plus fresh Required Checks for
this PR. The implementer does not review, approve or merge.

## Relationships

- [Issue #343](https://github.com/JettxonHo/ai-ecommerce-agent/issues/343)
- [P1 characterization review](../reviews/real-product-to-brief-pilot-p1-characterization.md)
- [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md)
- [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)
- [P0 plan](../product/real-product-to-brief-pilot-p0-plan.md)
- [Session-012](session-012-real-product-to-brief-pilot-p0.md)
