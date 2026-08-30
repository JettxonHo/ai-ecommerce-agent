# Real Product-to-Brief Pilot P1 characterization

> **Issue:** [#343](https://github.com/JettxonHo/ai-ecommerce-agent/issues/343)<br>
> **Branch:** `codex/mbl-pilot-p1-post-confirm-no-export`<br>
> **Base / reviewed head before edits:** `origin/main@4429b6d28a7eb71ffcf26e07ca37de851cf87ebd`<br>
> **Branch status:** `P1_CHARACTERIZATION_IN_PROGRESS`<br>
> **Merge-durable disposition:** `INCONCLUSIVE` becomes current truth only if this reviewed PR reaches `main`.

## Disposition

`INCONCLUSIVE`

The provider-free public seam has one passing normal path and deterministic
attribution for every injected checkpoint. The historical sanitized L5 record,
however, contains no failed checkpoint, safe problem type or traceback. Its
five-gate vector is compatible with seven different post-confirm checkpoints,
so this characterization cannot identify or exclude the historical first
failure. The historical no-export occurrence is confirmed as a recorded event;
its exact root cause is **not confirmed**.

This is a characterization result, not a production defect claim. No production
source, HTTP contract, generated client, migration, dependency or lockfile was
changed.

## Authorization and scope

Issue #341 / PR #342 is already merge-effective: P01–P08 are `ADMITTED`, the
denominator is exactly eight frozen product/attempt units, and P0 is
`P0_CONTRACT_FROZEN`. This Issue #343 branch is the single P1 outcome and is
`P1_CHARACTERIZATION_IN_PROGRESS` until merge.

The exact seven changed paths are:

1. `AGENTS.md`
2. `README.md`
3. `apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py`
4. `docs/goals/real-product-to-brief-pilot-goal.md`
5. `docs/handoffs/implementation-readiness.md`
6. `docs/reviews/real-product-to-brief-pilot-p1-characterization.md`
7. `docs/sessions/session-013-real-product-to-brief-pilot-p1.md`

`PILOT_EXECUTION_AUTHORIZATION = NOT_AUTHORIZED` remains true. This work used
no P01–P08 material, Pilot observation, numerator, participant, Provider,
Secret, runtime, browser, PostgreSQL, public deployment or export artifact.
The protected DEC-086/087, Pilot Contract, P0 plan/Session-012, historical
live smoke/evidence schema, production source, dependencies/locks,
migrations/OpenAPI/generated client, Web code and private material remain
unchanged.

## Historical evidence boundary

The sanitized record at
`/private/tmp/ai-ecommerce-issue335-l5-final2.aodiRX/evidence.json` records the
single L5 run at exact commit
`2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`:

- five ordered calls, `retry_count = 0`, `recovery_count = 0`;
- `validated_candidates = true` and `confirmed_result = true`;
- `marketing_export_immutable = false`;
  `xiaohongshu_export_immutable = false`;
  `downloads_utf8_no_bom_one_final_lf = false`;
- no export directory or Markdown file;
- no raw candidate, response, traceback, finish reason or exact checkpoint.

The resulting legacy gate vector is therefore:

```text
validated_candidates = true
confirmed_result = true
marketing_export_immutable = false
xiaohongshu_export_immutable = false
downloads_utf8_no_bom_one_final_lf = false
```

The record localizes the failure only to the interval after confirmation and
before the later gates complete. It does not distinguish preview, snapshot,
download, response shape or duplicate snapshot ID.

## Characterization seam

The test-only driver uses the real FastAPI public adapter with
interface-shaped fakes injected at its application boundaries. It does not
import or call a production test helper. The ordered HTTP path is:

1. `POST /api/v1/tasks/{taskId}/commands/confirm-current-result`
2. `POST /api/v1/tasks/{taskId}/export-previews`
3. `POST /api/v1/export-snapshots`
4. `GET /api/v1/export-snapshots/{exportSnapshotId}/content`

Marketing and Xiaohongshu each traverse preview → snapshot → download. The
driver then performs the harness-only `DISTINCT_SNAPSHOT_IDS`, UTF-8/BOM/final
line-feed checks and `OUTSIDE_REPO_PRESERVE` boundary. Outside-repository
preservation is not a product endpoint.

Only sanitized metadata is returned: `failed_stage`, optional `brief_kind`,
`last_completed_stage`, ordered stage names, and generic HTTP/checkpoint
problem metadata (`status`, `type`, `title`). Content is never retained in the
result record.

## Tests-first evidence

### Required characterization RED

Before the final driver existed, a tests-only assertion against the unchanged
production tree attempted to select one failure from the historical vector:

```text
uv run --offline --project apps/backend python -m pytest \
  apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py -q
1 failed in 0.01s
AssertionError: (True, True, False, False, False)
assert 7 == 1
```

The seven compatible checkpoints were already visible in that RED; no
production path or external resource was invoked.

### Final provider-free driver

```text
uv run --offline --project apps/backend python -m pytest \
  apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py -q
14 passed in 0.33s
```

The normal case reaches `COMPLETE` with all five gates true. The parameterized
matrix injects one failure at each checkpoint and asserts that the operation
list is exactly the ordered prefix ending at that checkpoint; no later step is
executed.

| Injected checkpoint | `brief_kind` | `last_completed_stage` | Historical vector compatible? |
|---|---|---|---|
| `CONFIRM` | — | — | No (`confirmed_result = false`) |
| `PREVIEW_MARKETING` | `marketing` | `CONFIRM` | Yes |
| `SNAPSHOT_MARKETING` | `marketing` | `PREVIEW_MARKETING` | Yes |
| `DOWNLOAD_MARKETING` | `marketing` | `SNAPSHOT_MARKETING` | Yes |
| `PREVIEW_XIAOHONGSHU` | `xiaohongshu` | `DOWNLOAD_MARKETING` | Yes |
| `SNAPSHOT_XIAOHONGSHU` | `xiaohongshu` | `PREVIEW_XIAOHONGSHU` | Yes |
| `DOWNLOAD_XIAOHONGSHU` | `xiaohongshu` | `SNAPSHOT_XIAOHONGSHU` | Yes |
| `DISTINCT_SNAPSHOT_IDS` | — | `DOWNLOAD_XIAOHONGSHU` | Yes |
| `UTF8_VALIDATE_MARKETING` | `marketing` | `DISTINCT_SNAPSHOT_IDS` | No (immutable gates already true) |
| `UTF8_VALIDATE_XIAOHONGSHU` | `xiaohongshu` | `UTF8_VALIDATE_MARKETING` | No (immutable gates already true) |
| `OUTSIDE_REPO_PRESERVE` | — | `UTF8_VALIDATE_XIAOHONGSHU` | No (all gates true) |
| `COMPLETE` | — | `COMPLETE` | No (all gates true) |

The legacy collapse assertion returns exactly these seven compatible stages:

```text
PREVIEW_MARKETING
SNAPSHOT_MARKETING
DOWNLOAD_MARKETING
PREVIEW_XIAOHONGSHU
SNAPSHOT_XIAOHONGSHU
DOWNLOAD_XIAOHONGSHU
DISTINCT_SNAPSHOT_IDS
```

This proves that the old aggregate cannot select one unique post-confirm
failure point.

## Reconciled existing evidence

The following provider-free suites passed without starting a product runtime:

```text
uv run --offline --project apps/backend python -m pytest \
  apps/backend/tests/contract/test_task_http_routes.py \
  apps/backend/tests/contract/test_export_delivery_public_contract.py \
  apps/backend/tests/contract/test_export_markdown_renderer_contract.py \
  apps/backend/tests/unit/test_export_delivery_values.py \
  apps/backend/tests/unit/test_export_markdown_renderer.py \
  apps/backend/tests/unit/test_fl2_live_controls.py -q
73 passed in 5.04s

uv run --offline --project apps/backend python -m pytest \
  apps/backend/tests/architecture/test_http_foundation_boundaries.py \
  apps/backend/tests/architecture/test_export_delivery_boundaries.py \
  apps/backend/tests/architecture/test_import_contracts.py \
  apps/backend/tests/architecture/test_provider_sdk_consumer_boundaries.py -q
28 passed in 1.32s

uv run --offline --project apps/backend pyright \
  apps/backend/src \
  apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py
0 errors, 0 warnings, 0 informations

uv run --offline --project apps/backend ruff format --check \
  apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py
1 file already formatted

uv run --offline --project apps/backend ruff check \
  apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py
All checks passed!

git diff --check
PASS
```

The opt-in live smoke module and PostgreSQL integration path were inspected but
not selected. A fresh PostgreSQL run was unnecessary: the public HTTP seam is
covered by the injected fake driver, while the existing persisted preview /
snapshot / download tests remain the authoritative provider-free persistence
coverage. No retry, alternate scope or raw Compose lifecycle was used.

## Root cause and Pilot impact

**Root cause:** not confirmed. The historical occurrence is confirmed by its
sanitized evidence, but the evidence cannot identify the first failed
checkpoint. The normal path and all injected failures exercise the expected
HTTP/application boundary; they neither reproduce nor disprove a future
Provider-specific failure.

**Pilot impact:** if an admitted product/attempt reaches the same post-confirm
no-export condition, it can yield no qualifying approved immutable export and
therefore remains in the fixed denominator as `FAIL` or `BLOCKED` under the
later exact Pilot outcome contract. This Issue runs no admitted sample and
records no numerator or classification.

`REPAIR_REQUIRED = NO` — no deterministic production defect was reproduced, so
no product repair is justified or implemented here.

**One minimal proposal (not accepted or implemented):** if a later owner-gated
evidence issue is opened, extend only the sanitized run record with
`failed_stage`, optional `brief_kind`, `last_completed_stage` and generic
`problem_type`; retain no raw Provider payload, prompt, reasoning, Secret or
personal data. This proposal targets attribution evidence, not product logic.

**Next one action:** obtain the independent Sol five-axis review and fresh
Required Checks for this exact seven-path PR. If it reaches `main`, stop P1 and
wait for a separate Owner-gated P2 contract; do not infer Provider acceptance
or authorize a retry.

## Merge-durable status and rollback

Before this PR reaches `main`, the branch remains:

```text
P1_CHARACTERIZATION_IN_PROGRESS
PILOT_EXECUTION_AUTHORIZATION = NOT_AUTHORIZED
```

If the reviewed PR reaches `main`, the exact disposition becomes
`INCONCLUSIVE`; P1 is then complete only as provider-free characterization,
while P0 remains frozen and no P2 action is authorized. Rollback is a revert of
this PR; no runtime, data, dependency or migration state is changed.

The implementer does not independently review, approve or merge this PR.
