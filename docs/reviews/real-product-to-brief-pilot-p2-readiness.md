# Real Product-to-Brief Pilot P2 Readiness Review

**Status:** `P2_READINESS_IMPLEMENTATION_IN_PROGRESS`
**Base:** `8c43068038d4c3859383d68263f0ab0336480f6a`
**Scope:** provider-free implementation and lifecycle characterization only

## Authority and boundary

The owner amendment in [Issue #347 comment 5473654628](https://github.com/JettxonHo/ai-ecommerce-agent/issues/347#issuecomment-5473654628)
supersedes the earlier stop comment only for this implementation scope. It
confirms that Issue #345 / PR #346 is merged and repaired, while Issue #347 is
the current P2 readiness implementation. The amendment fixes a 24-path
allowlist: the original 18 paths plus the Task Management, Primary Input,
Deterministic Result, Review/Export and HTTP composition paths, and the new P2
PostgreSQL composition test.

`P2_READINESS_IMPLEMENTATION_IN_PROGRESS` is the current branch fact.
`P2_READINESS_IMPLEMENTED = YES` is merge-effective only after a reviewed Issue
#347 PR reaches `main`. `PILOT_EXECUTION_AUTHORIZATION=NOT_AUTHORIZED`, and the
real P01 Grant, participant work and business observation remain
`NOT_AUTHORIZED`.

## Actual changed subset

The implementation subset is limited to the P2 bootstrap/artifact/runtime
seams and their tests. The five existing PostgreSQL/FastAPI composition paths
are allowlisted for reuse but remain byte-identical and are not changed. The
seven synchronized docs are documentation edits tracked outside the 24-path
implementation allowlist:

- `apps/backend/src/ai_ecommerce_agent/orchestration/deterministic_pipeline.py`
- `apps/backend/src/ai_ecommerce_agent/orchestration/pilot_attempt_artifact.py`
- `apps/backend/src/ai_ecommerce_agent/platform/model_runtime/deepseek/_cost_gate.py`
- `apps/backend/src/ai_ecommerce_agent/bootstrap/pilot_p2.py`
- `apps/backend/tests/architecture/test_pilot_p2_composition_boundaries.py`
- `apps/backend/tests/contract/test_pilot_attempt_artifact_contract.py`
- `apps/backend/tests/integration/test_p2_deepseek_real_product_live.py`
- `apps/backend/tests/integration/test_pilot_p2_postgres_composition.py`
- `apps/backend/tests/unit/test_deepseek_cost_gate.py`
- `apps/backend/tests/unit/test_p2_live_controls.py`
- `apps/backend/tests/unit/test_pilot_p2_composition.py`

The five existing PostgreSQL/FastAPI composition files from the amendment are
reused without changing their bytes. `local_demo.py`, migrations, the public
API/generated client and the default composition remain unchanged.

## Readiness evidence

- The required cost boundary is the fixed DeepSeek reservation, not an owner
  cap guess. The P2 coordinator is lazy, P2-only and rejects scripted binding;
  the generic/local scripted path remains a separate characterization path.
- PilotAttemptArtifacts are outside-Git evidence truth. Reserve/run records are
  immutable and sanitized; Marketing and Xiaohongshu exports use fixed local
  destinations, preserve the actual server filename as metadata, and retain
  UTF-8 bytes, relative references and byte counts without hashes or absolute
  paths.
- Human Review is a separate immutable record with `PENDING`, `APPROVED` or
  `REJECTED`, exact Task/result/export references, a sanitized reviewer role and
  seven independent dimensions. Finalization is explicit `PASS`/`FAIL`/`BLOCKED`;
  only an approved review and at least one qualifying immutable export can
  produce `PASS`. No numerator, ratio or cohort count is recorded.
- PostgreSQL remains Business Truth for the existing Task → Primary Input →
  Result → confirmation/Review-Export lifecycle. The P2 composition reuses the
  existing Task/Primary Input/Result/Review-Export and FastAPI factories without
  adding a migration or a new public route.

## RED → GREEN chronology

1. Slice 3A established immutable attempt identity and run records; Slice 3B
   RED rejected the unsupported export command, then GREEN added fixed-file
   capture, fsync/readback/readonly checks and sanitized metadata.
2. Slice 3C RED rejected the unsupported Human Review command, then GREEN added
   the durable `review.json` record, seven dimensions, timing/identity/export
   gates and no-overwrite behavior.
3. Slice 3D RED rejected unsupported finalization, then GREEN added explicit
   `PASS`/`FAIL`/`BLOCKED` outcome semantics and immutable `outcome.json`.
4. Slice 4A RED showed the generic coordinator accepted a scripted P2 binding
   with five calls; GREEN added the lazy P2-only DeepSeek bootstrap and boundary
   test while preserving the generic path.
5. Slice 5A/5B RED showed missing live controls and missing explicit dependency
   wiring; GREEN added deep preflight and an injected ordered runner seam. The
   direct-artifact default was removed; no automatic fallback remains.
6. The PostgreSQL/FastAPI composition RED showed the direct P2 composition had
   no application lifecycle; GREEN added the no-migration P2 composition over
   existing factories. TestClient warning, AF_UNIX socket, and server/local
   filename REDs were repaired in bounded tests.

## Guarded PostgreSQL chronology

The evidence below is provider-free and not a real P01/business outcome:

- Initial guarded invocation collected one opt-in live test and skipped it with
  zero executed because the real-run flag was absent.
- A malformed ephemeral project name was rejected by
  `mvp0_validate_resource_scope` before resource creation; no retry followed.
- The TestClient/httpx fallback warning produced a RED; the accepted scoped
  warning filter repaired it.
- The TestClient AF_UNIX boundary produced a RED; the accepted socket fixture
  now permits only AF_UNIX and keeps TCP/network sockets blocked.
- The server filename versus fixed local filename distinction produced a RED;
  the artifact capture now stores the actual server basename separately and
  always writes the fixed local path.
- The final guarded provider-free three-test scope is recorded as **3 PASS** at
  the characterization/collection boundary with cleanup PASS. No real P01
  business execution, Provider call, Secret read or participant review is
  claimed; the real database lifecycle remains an opt-in owner action.

## Decision

**Observation:** the implementation and existing lifecycle seams are coherent
for provider-free P2 readiness evidence. **Decision boundary:** this review does
not accept the Pilot, a real P01 run, a human business outcome, a numerator or a
Goal completion. Only a reviewed PR reaching `main` may change the readiness
status to `P2_READINESS_IMPLEMENTED = YES`.
