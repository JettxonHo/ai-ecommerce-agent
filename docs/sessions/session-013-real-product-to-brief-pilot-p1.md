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
HTTP adapter. Its normal case is explicitly an injected HTTP-adapter fake path,
not a fresh PostgreSQL or product-runtime run; existing provider-free suites
cover the persisted path. It exercises exactly:

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
HTTP endpoint. The normal case uses an absolute `tmp_path` outside the
repository, exclusive `xb` writes of exactly `marketing-brief.md` and
`xiaohongshu-brief.md`, and byte-for-byte rereads. `OUTSIDE_REPO_PRESERVE`
fails before directory creation and no later stage runs. No production helper is
imported, and no content is retained in the metadata record.

### Observation — final GREEN

```text
uv run --offline --project apps/backend python -m pytest \
  apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py -q
15 passed in 0.33s
```

The seven post-confirm preview/snapshot/download/distinct-ID failures produce
the exact historical vector; `CONFIRM` differs because confirmation is false,
and UTF-8/preservation failures happen after immutable gates have turned true.

### Observation — preservation follow-up RED

Independent review found that the first callback was in-memory only. Before the
follow-up implementation, a temporary tests-only assertion against unchanged
production failed:

```text
uv run --offline --project apps/backend python -m pytest \
  apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py::test_preservation_red_shows_in_memory_driver_writes_no_export_directory -q
1 failed in 0.16s
AssertionError: assert False
```

That temporary RED-only assertion was removed after the driver gained guarded
outside-repository `tmp_path` preservation; the final focused run remains
`15 passed`.

### Observation — confirmed response-shape blocker

The current public HTTP snapshot projection returns `exportSnapshotId`, while
the retained live smoke expects `snapshotId`. A provider-free regression drives
the same public projection, receives a successful snapshot response, then
applies the historical lookup and gets `KeyError` before download or any later
operation. The exact code remains unchanged in this Issue; the mismatch existed
at the historical run commit as well.

```text
uv run --offline --project apps/backend python -m pytest \
  apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py::test_historical_snapshot_id_key_mismatch_stops_before_download -q
1 passed in 0.16s
```

This confirms a live-harness consumer defect. It does not prove the historical
L5 run reached this lookup: an earlier preview or snapshot conversion/commit
failure remains compatible with the sanitized five-gate vector.

## Result and interpretation

### Disposition: `CONFIRMED`

The response-shape blocker is confirmed: the live harness reads `snapshotId`,
but the public projection emits `exportSnapshotId`, so a successful snapshot
response raises `KeyError` before download. The seven injected post-confirm
checkpoints remain compatible with the historical legacy vector, and the exact
historical first-failure attribution remains `INCONCLUSIVE` because an earlier
preview/snapshot failure could have occurred. The normal path is an injected
HTTP-adapter fake path, not fresh PostgreSQL or product-runtime evidence.

The response-key mismatch is one concrete `SNAPSHOT_MARKETING`-boundary variant
within the seven compatible post-confirm checkpoints; it occurs after a
successful snapshot response and before the download lookup.

### Pilot impact

An admitted product/attempt that reaches the same condition can finish without
a qualifying approved immutable export and therefore remains in the fixed P0
denominator as `FAIL` or `BLOCKED` under the later exact outcome contract. This
Session performs no Pilot run, outcome classification or numerator calculation.

### Repair boundary

`REPAIR_REQUIRED = YES` for the retained live-harness consumer; no repair is
implemented in Issue #343.

`MUST_FIX_BEFORE_PILOT_EXECUTION = YES` because the harness must be repaired
before it can support a later Pilot attempt. The split is explicit:
`PRODUCTION_FIX_REQUIRED_BEFORE_PILOT_EXECUTION = NO` (no product export logic
defect was reproduced) and `HARNESS_FIX_REQUIRED_BEFORE_PILOT_EXECUTION = YES`
(the response-key consumer is broken). The unresolved historical first-failure
attribution remains a known risk and must be disclosed at any fresh exact-commit
Owner Gate; this PR does not authorize P2, retries or substitutions.

**Proposal (not accepted):** create one separate bounded provider-free
harness-repair Issue that changes only the retained live-smoke response lookup
from `snapshotId` to the public `exportSnapshotId` and adds a regression for the
response shape. Do not alter product export logic, public contracts, evidence
schema or raw-material retention.

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
`CONFIRMED` for the harness blocker (historical first-failure attribution
remains `INCONCLUSIVE`); P0 remains frozen, no Provider acceptance is inferred,
and P2 still requires a separate exact-commit Owner authorization and Issue.
The pre-merge next action is independent Sol five-axis review plus fresh
Required Checks for this PR. After merge, the single next action is
`OWNER_AUTHORIZES_ONE_BOUNDED_PROVIDER_FREE_HARNESS_REPAIR_ISSUE`; that Owner
authorization does not auto-start the repair or P2. The implementer does not
review, approve or merge.

## Relationships

- [Issue #343](https://github.com/JettxonHo/ai-ecommerce-agent/issues/343)
- [P1 characterization review](../reviews/real-product-to-brief-pilot-p1-characterization.md)
- [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md)
- [Real Product-to-Brief Pilot Contract](../product/real-product-to-brief-pilot-contract.md)
- [P0 plan](../product/real-product-to-brief-pilot-p0-plan.md)
- [Session-012](session-012-real-product-to-brief-pilot-p0.md)
