# Session-015 — Real Product-to-Brief Pilot P2 Readiness

**Date:** 2026-08-31
**Base:** `8c43068038d4c3859383d68263f0ab0336480f6a`
**Status:** `P2_READINESS_IMPLEMENTATION_IN_PROGRESS`

## Fact: owner amendment and scope

The owner amendment in [Issue #347 comment 5473654628](https://github.com/JettxonHo/ai-ecommerce-agent/issues/347#issuecomment-5473654628)
records Issue #345 / PR #346 as merged and repaired, and authorizes a fixed
24-path Issue #347 scope: the original 18 paths plus five existing
PostgreSQL/FastAPI composition paths and the new integration test. The five
existing composition paths are reused byte-identically and are not changed. The
actual changed subset is the P2 bootstrap, DeepSeek cost/runtime,
PilotAttemptArtifacts, deterministic P2 wiring and their bounded tests, plus the
new PostgreSQL/FastAPI composition test; the seven synchronized docs are
documentation edits tracked separately. Migrations, `local_demo.py`, public
API/generated client and default composition remain unchanged.

The required cost boundary is the fixed DeepSeek reservation, not an owner-cap
guess. Pilot execution and the real P01 Grant remain `NOT_AUTHORIZED`.

## Fact: implementation chronology

- Slice 3A reserve/run artifact identity was established.
- Slice 3B export RED→GREEN added fixed local Markdown files, actual server
  filename metadata, byte-count/relative-reference sanitization and immutable
  writes.
- Slice 3C review RED→GREEN added one durable Human Review with `PENDING`,
  `APPROVED` and `REJECTED`, seven dimensions and fixed rationale/identity
  boundaries.
- Slice 3D finalization RED→GREEN added explicit `PASS`, `FAIL` and `BLOCKED`
  terminal records without numerator, ratio or exclusion fields.
- Slice 4A scripted-P2 RED→GREEN added the lazy P2-only DeepSeek composition and
  preserved the generic/local scripted characterization path.
- Slice 5A/5B live-control and explicit-dependency RED→GREEN added deep
  preflight and the provider-free injected ordered runner seam; automatic
  fallback was removed.
- PostgreSQL/FastAPI composition RED→GREEN added a no-migration P2 composition
  over the existing Task, Primary Input, Result/Review-Export and HTTP factories.

## Observation: provider-free PostgreSQL harness chronology

The following are harness observations, not business acceptance:

1. Initial guarded invocation skipped one opt-in live test with zero executed.
2. A malformed ephemeral project name was rejected before creation.
3. The TestClient/httpx warning was captured as RED and repaired with a scoped
   warning filter.
4. The AF_UNIX socket boundary was captured as RED and repaired with the
   accepted narrow socket fixture; TCP/network sockets stayed blocked.
5. Server filename versus fixed local filename was captured as RED and repaired
   by separating the two fields.
6. The final guarded provider-free three-test scope recorded **3 PASS** with
   cleanup PASS. No real P01, Provider, Secret, participant or business result
   was executed or accepted.

## Fact: acceptance boundary

PostgreSQL remains Business Truth for the existing Task → Primary Input → Result
→ confirmation/Review-Export lifecycle. Outside-Git PilotAttemptArtifacts remain
Pilot Evidence Truth for attempt, cost, calls, Human Review and
`PASS`/`FAIL`/`BLOCKED`. Human Review and qualifying export semantics are
explicit and immutable; a qualifying result requires at least one approved
immutable Marketing or Xiaohongshu export, while two exports still represent
one attempt. This session does not register a numerator, ratio, cohort result or
Goal completion.

`P2_READINESS_IMPLEMENTATION_IN_PROGRESS` remains current until a reviewed PR
reaches `main`, at which point the owner may accept
`P2_READINESS_IMPLEMENTED = YES`. No Provider/Secret action, real P01 Grant,
participant execution, migration or public-contract change is implied.

## Archive result

- Session-015 records the owner amendment, exact base, implementation chronology,
  bounded 24-path scope, provider-free PostgreSQL chronology and acceptance
  boundary.
- No earlier Session, Decision, RFC, Contract or P0/P1 history was rewritten.
- The synchronized review is [P2 readiness review](../reviews/real-product-to-brief-pilot-p2-readiness.md).
