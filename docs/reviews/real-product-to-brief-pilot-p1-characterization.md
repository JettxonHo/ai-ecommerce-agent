# Real Product-to-Brief Pilot P1 characterization

> **Issue:** [#343](https://github.com/JettxonHo/ai-ecommerce-agent/issues/343)<br>
> **Branch:** `codex/mbl-pilot-p1-post-confirm-no-export`<br>
> **Base / reviewed head before edits:** `origin/main@4429b6d28a7eb71ffcf26e07ca37de851cf87ebd`<br>
> **Branch status:** `P1_CHARACTERIZATION_IN_PROGRESS`<br>
> **Merge-durable disposition:** `CONFIRMED` becomes current truth only if this reviewed PR reaches `main`; exact historical first-failure attribution remains `INCONCLUSIVE`.

## Disposition

`CONFIRMED`

The injected HTTP-adapter/interface-shaped fake normal path passes, and the
same driver deterministically attributes every injected checkpoint. This is not
a fresh PostgreSQL or product-runtime run; the existing provider-free suites
provide the persisted-path coverage. The historical sanitized L5 record,
however, contains no failed checkpoint, safe problem type or traceback. Its
five-gate vector is compatible with seven different post-confirm checkpoints,
and the actual public HTTP projection is proven incompatible with the historical
live-harness response-key lookup: the snapshot response exposes
`exportSnapshotId`, while the retained smoke reads `snapshotId`. A successful
snapshot response therefore raises `KeyError` before download and any later
stage. The current/historical harness blocker is confirmed. The exact first
failure of the historical run remains **INCONCLUSIVE** because an earlier
preview/snapshot failure would also fit its sanitized vector.

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

The live harness currently performs `snapshot.json()["snapshotId"]` after the
first snapshot response (`apps/backend/tests/integration/test_fl2_deepseek_live_smoke.py`),
but the public projection emits only `exportSnapshotId`
(`apps/backend/src/ai_ecommerce_agent/entrypoints/http/task_routes.py`). This
response-shape mismatch is a confirmed harness defect at the current and
historical code. It guarantees that any run reaching a successful first
snapshot cannot proceed to its download; it does not prove that this was the
first failure in the historical run.

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
15 passed in 0.33s
```

The normal case reaches `COMPLETE` through the injected HTTP-adapter fakes with
all five gates true. It uses an absolute `tmp_path` directory outside the
repository, creates it once with mode `0700`, writes exactly
`marketing-brief.md` and `xiaohongshu-brief.md` with exclusive `xb` mode, and
rereads both files to prove byte equality. The parameterized matrix injects one
failure at each checkpoint and asserts that the operation list is exactly the
ordered prefix ending at that checkpoint; no later step is executed. The
`OUTSIDE_REPO_PRESERVE` injection fails before directory creation and leaves no
path behind.

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

The confirmed `snapshotId`/`exportSnapshotId` response-shape mismatch is one
concrete `SNAPSHOT_MARKETING`-boundary variant in that compatible set: it
occurs after a successful snapshot response and before the download lookup.

### Confirmed response-shape blocker

The provider-free regression drives the same public HTTP projection and then
applies the historical harness lookup. It receives a successful `201` snapshot
body containing `exportSnapshotId` and no `snapshotId`; the historical lookup
raises `KeyError`, and the operation log contains no download or later stage.

```text
uv run --offline --project apps/backend python -m pytest \
  apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py::test_historical_snapshot_id_key_mismatch_stops_before_download -q
1 passed in 0.16s
```

This confirms the live-harness blocker without importing or modifying the live
smoke module, production code or any external resource.

### Follow-up preservation RED → GREEN

The independent review identified that an in-memory preservation callback did
not satisfy the harness predicate. Before replacing it, this tests-only RED was
captured with production unchanged:

```text
uv run --offline --project apps/backend python -m pytest \
  apps/backend/tests/contract/test_p1_post_confirm_export_characterization.py::test_preservation_red_shows_in_memory_driver_writes_no_export_directory -q
1 failed in 0.16s
AssertionError: assert False
```

The named test was a temporary RED-only assertion and was removed after GREEN.
The final driver now performs the guarded absolute outside-repository `tmp_path`
directory and exclusive file writes described above; its focused GREEN remains
`15 passed`.

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

**Root cause (confirmed for the harness):** response-shape mismatch. The
retained live smoke reads `snapshot.json()["snapshotId"]`, while the actual
public HTTP projection returns `exportSnapshotId`. The provider-free regression
proves a successful snapshot response followed by `KeyError` before download
and no later operation. This is a harness-consumer defect, not a product export
logic defect.

**Historical first-failure attribution:** `INCONCLUSIVE`. The sanitized L5
evidence cannot prove that the response-key mismatch was the first failure;
preview or snapshot conversion/commit could have failed earlier. It does prove
the mismatch existed at the historical run commit and is fully compatible with
the recorded vector whenever the run reached its first snapshot response.

**Pilot impact:** if an admitted product/attempt reaches the same post-confirm
no-export condition, it can yield no qualifying approved immutable export and
therefore remains in the fixed denominator as `FAIL` or `BLOCKED` under the
later exact Pilot outcome contract. This Issue runs no admitted sample and
records no numerator or classification.

`REPAIR_REQUIRED = YES` — a separate bounded harness repair is required before
this retained smoke can be used for any later Pilot execution. No repair is
implemented in Issue #343.

`MUST_FIX_BEFORE_PILOT_EXECUTION = YES` because the harness must be repaired
before it can safely support a later Pilot run. The split is explicit:
`PRODUCTION_FIX_REQUIRED_BEFORE_PILOT_EXECUTION = NO` (no product defect was
reproduced) and `HARNESS_FIX_REQUIRED_BEFORE_PILOT_EXECUTION = YES` (the
response-key consumer is broken). The unresolved historical first-failure
attribution remains a known risk and must be disclosed at any fresh exact-
commit Owner Gate; this does not authorize P2, a retry or a substitution.

**One minimal proposal (not accepted or implemented):** create a separate
bounded provider-free harness-repair Issue that changes only the retained live
smoke response lookup from `snapshotId` to the public `exportSnapshotId` and
adds a regression for the response shape. Do not alter product export logic,
public contracts, evidence schema or raw-material retention.

**Pre-merge next action:** obtain the independent Sol five-axis review and fresh
Required Checks for this exact seven-path PR.

`NEXT_SINGLE_ACTION` after this PR reaches `main` is
`OWNER_AUTHORIZES_ONE_BOUNDED_PROVIDER_FREE_HARNESS_REPAIR_ISSUE`.
That is one Owner authorization only; it does not auto-start the repair or P2.
The later repair Issue must change only the response-key consumer and its
regression. Any accepted P2 still needs its own exact-commit authorization,
Provider/access bounds and stop rules. Do not infer Provider acceptance or
authorize a retry from this characterization.

## Merge-durable status and rollback

Before this PR reaches `main`, the branch remains:

```text
P1_CHARACTERIZATION_IN_PROGRESS
PILOT_EXECUTION_AUTHORIZATION = NOT_AUTHORIZED
```

If the reviewed PR reaches `main`, the exact disposition becomes
`CONFIRMED` for the harness blocker (with historical first-failure attribution
remaining `INCONCLUSIVE`); P1 is then complete only as provider-free
characterization, while P0 remains frozen and no P2 action is authorized.
Rollback is a revert of this PR; no runtime, data, dependency or migration
state is changed.

## Process trace

The first implementation commit was `52c63378257230b2e8a1545b222758b7a1e157a9`.
The test-only preservation follow-up was amended to
`5048d8116a733144b022d5c1094dcb274d0ac6fc`; its first
`git push --force-with-lease` attempt hit one transient GitHub TLS error, then
the remote was verified and one successful force-with-lease push completed.
This follow-up uses an ordinary commit only; no production or protected path
was altered by the process event.

The implementer does not independently review, approve or merge this PR.
