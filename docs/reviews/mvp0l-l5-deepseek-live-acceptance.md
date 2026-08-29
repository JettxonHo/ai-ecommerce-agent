# MVP-0L L5 DeepSeek live acceptance — terminal reconciliation

**Issue:** [#335](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335)
**Branch:** `codex/mvp0l-l5-deepseek-live-acceptance`
**Reviewed base:** `origin/main@ef5ac0d4b372c1478ee2541ee3ec5318e72a1060`
**Status:** `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` — terminal
**Scope:** Phase-A harness preparation plus the single owner-authorized L5 run

## Result

Phase A added an explicit operator-selected export-directory control to the
retained opt-in DeepSeek smoke seam. Its harness-only result is preserved below
as historical preparation evidence.

The single owner-authorized L5 run then executed from exact commit
`2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f` and has terminal disposition
`L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS`. This is not Provider acceptance. The
sanitized evidence record reports five ordered `deepseek-v4-pro` calls,
`duration_ms=523230`, `retry_count=0`, `recovery_count=0`,
`validated_candidates=true`, `confirmed_result=true`, input/output/total token
totals of `23845`/`43999`/`67844`, both immutable export gates false, and the
UTF-8/download gate false. No export directory or Markdown file was produced,
so no human usability judgment was possible. The record intentionally does not
identify an exact cause and contains no raw response, prompt, candidate,
reasoning, traceback, account or balance material.

The authorization was consumed at the first Provider request. There was no
rerun, repair, substitution or top-up. Cleanup required exactly one Ctrl-C /
SIGINT attempt; the retained background lifecycle ignored it, so one SIGTERM
fallback was required. Final ports/resources, Secret environment state and
checkout state were clean. The SIGTERM fallback is disclosed as a cleanup
contract deviation.

Sanitized evidence is retained at
`/private/tmp/ai-ecommerce-issue335-l5-final2.aodiRX/evidence.json`; no other
runtime/provider artifact is part of this reconciliation.

The historical Fast Lane remains `GOAL_BLOCKED`. The two prior DeepSeek
authorizations remain consumed; no authorization carries forward from them.

## Isolation and routing evidence

- Phase-A harness work was performed in the historical fresh clone
  `/private/tmp/ai-ecommerce-agent-issue335`; the shared checkout was not
  modified.
- The authorized L5 runtime then ran in the fresh detached checkout
  `/private/tmp/ai-ecommerce-issue335-resume.qzlnzM/repo` at exact
  `HEAD=2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`.
- Runtime preflight used disposable locked backend Python 3.13 hydration and
  one offline locked Web hydration; tracked backend/Web package and lock bytes
  remained unchanged, with no package network access implied or used.
- `/Users/ketchup/.codex/agents/luna-worker.toml` was parsed with Python 3.12
  `tomllib`: `name=luna-worker`, `model=gpt-5.6-luna`,
  `model_reasoning_effort=max`. This is `CONFIG_VERIFIED` only; runtime
  identity is not inferred.
- The direct PRE-EDIT checkpoint was reported before the harness edit. The
  orchestrator then explicitly accepted it. The harness edit began only after
  that acceptance; the late checkpoint is retained as process history, not
  hidden.
- All nine allowlisted Issue paths are changed across the Phase-A harness and
  this terminal reconciliation: the two test paths, this review document,
  `README.md`, `apps/web/README.md`, `AGENTS.md`, the Goal, the
  implementation-readiness handoff and the live-smoke handoff. No tenth path
  exists.

## Phase-A implementation

`apps/backend/tests/integration/test_fl2_deepseek_live_smoke.py` now:

1. requires `FL2_DEEPSEEK_LIVE_EXPORT_DIR` when the existing explicit smoke
   controls select the module;
2. rejects a non-absolute path, a path resolved inside the repository, or a
   target that already exists during module preflight, before the runtime
   fixture can resolve the private credential, construct a client, open
   PostgreSQL, or make a network request;
3. validates each downloaded payload as UTF-8 without BOM and with exactly one
   final line feed;
4. preserves only `marketing-brief.md` and `xiaohongshu-brief.md`, using an
   exclusive directory/file creation path and cleanup on any write/validation
   failure; and
5. invokes preservation only after the existing five ordered calls, result
   gates, confirmation and immutable export assertions have passed. The
   existing sanitized evidence writer remains the only failure evidence path.

Phase A itself made no provider request, profile, call, prompt, schema, mapper,
runtime, public API, database/evidence schema, dependency, migration or product
behavior change. The helper never receives or writes raw Provider response,
reasoning, prompt, context, candidate, traceback, Secret, account or database
row material; its exact key/file allowlist rejects anything beyond the two
user-facing downloads.

## Tests-first evidence

### TRUE RED before the harness edit

The new tests were added first and run against the unchanged harness:

```text
PYTHONPATH=src /Users/ketchup/Projects/AI-Ecommerce-Agent-issue270/apps/backend/.venv/bin/python -m pytest tests/unit/test_fl2_live_controls.py -q
4 failed, 3 passed
```

The failures were the absent export control, absent preservation helper and
missing existing-target fail-closed behavior. No runtime or Provider seam was
invoked.

### Focused GREEN

After the minimal harness edit:

```text
PYTHONPATH=src /Users/ketchup/Projects/AI-Ecommerce-Agent-issue270/apps/backend/.venv/bin/python -m pytest tests/unit/test_fl2_live_controls.py -q
7 passed

ruff format --check \
  tests/integration/test_fl2_deepseek_live_smoke.py \
  tests/unit/test_fl2_live_controls.py
PASS

ruff check \
  tests/integration/test_fl2_deepseek_live_smoke.py \
  tests/unit/test_fl2_live_controls.py
PASS

git diff --check
PASS
```

The focused tests cover one normal exact-download preservation, one existing
target fail-closed preflight with runtime/PostgreSQL sentinels untouched, and
one two-file/no-raw-material invariant. They intentionally do not construct
Docker, PostgreSQL, API/Web, browser or Provider resources.

Additional affected offline checks from the same fresh clone:

```text
pytest tests/unit/test_fl2_live_controls.py \
  tests/integration/test_fl2_deepseek_live_smoke.py -q
7 passed, 1 skipped

pytest tests/integration/test_fl2_deepseek_offline_diagnosis.py \
  tests/unit/test_deepseek_runtime_factory.py \
  tests/unit/test_deepseek_response_mapping.py \
  tests/unit/test_deepseek_runtime.py -q
23 passed

pytest tests/architecture -q
174 passed

pyright src
0 errors, 0 warnings, 0 informations
```

The architecture run uses the already-installed repository virtualenv tools;
no dependency installation or network package action was performed. The
Pyright invocation reports the expected missing local `.venv` advisory for
this disposable clone but completes with zero diagnostics.

The changed-path audit reports 9 of the 9 Issue slots, all allowlisted. No
production/runtime or live-evidence-schema source file is changed; the
relative-document link/fence audit passes for every changed document.

## Historical Phase-A pre-call boundary

Before the now-completed live action, the Phase-A PR required:

- exact clean reviewed head and a non-draft Ready PR;
- fresh Required Checks at `12/12 PASS`;
- independent `ORCHESTRATOR_REVIEWER` five-axis review of the actual diff;
- a read-only recheck of official DeepSeek base/model/price/access material;
- explicit owner authorization for the exact one-time paid run, including the
  new absolute evidence path and export directory.

Those gates were completed for the single authorized run; the current truth is
the terminal `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` disposition recorded above.
The Phase-A harness evidence itself contains no `.env` value, raw Secret,
Provider material or live result.
