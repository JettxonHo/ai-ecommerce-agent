# MVP-0L L5 DeepSeek live acceptance — Phase A harness review

**Issue:** [#335](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335)
**Branch:** `codex/mvp0l-l5-deepseek-live-acceptance`
**Reviewed base:** `origin/main@ef5ac0d4b372c1478ee2541ee3ec5318e72a1060`
**Status:** `L5_HARNESS_REVIEW_READY` — owner authorization pending
**Scope:** Phase A offline harness preparation only

## Result

Phase A adds an explicit operator-selected export-directory control to the
retained opt-in DeepSeek smoke seam. A later, separately authorized L5 run may
preserve the two already-generated user-facing Markdown downloads outside the
repository for human review. This Phase-A result is not a Provider run, does
not claim live success, and does not authorize Secret access or any runtime
action.

The historical Fast Lane remains `GOAL_BLOCKED`. The two prior DeepSeek
authorizations remain consumed; no authorization carries forward from them.

## Isolation and routing evidence

- Work was performed in the fresh clone `/private/tmp/ai-ecommerce-agent-issue335`;
  the shared checkout was not modified.
- The branch started clean at exact `HEAD=origin/main=
  ef5ac0d4b372c1478ee2541ee3ec5318e72a1060`.
- `/Users/ketchup/.codex/agents/luna-worker.toml` was parsed with Python 3.12
  `tomllib`: `name=luna-worker`, `model=gpt-5.6-luna`,
  `model_reasoning_effort=max`. This is `CONFIG_VERIFIED` only; runtime
  identity is not inferred.
- The direct PRE-EDIT checkpoint was reported before the harness edit. The
  orchestrator then explicitly accepted it. The harness edit began only after
  that acceptance; the late checkpoint is retained as process history, not
  hidden.
- Eight of the nine Issue paths are changed in this Phase-A working tree: the
  two test paths, this review document, `README.md`, `apps/web/README.md`, the
  Goal, the implementation-readiness handoff and the live-smoke handoff. The
  remaining `AGENTS.md` slot is untouched; no tenth path exists.

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

No provider request, profile, call count, prompt, schema, mapper, runtime,
public API, database/evidence schema, dependency, migration or product behavior
changed. The helper never receives or writes raw Provider response,
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

The changed-path audit reports 8 of the 9 Issue slots, all allowlisted. No
production/runtime or live-evidence-schema source file is changed; the
relative-document link/fence audit passes for every changed document.

## Pre-call boundary

Before any later live action, this Phase-A PR still requires:

- exact clean reviewed head and a non-draft Ready PR;
- fresh Required Checks at `12/12 PASS`;
- independent `ORCHESTRATOR_REVIEWER` five-axis review of the actual diff;
- a read-only recheck of official DeepSeek base/model/price/access material;
- explicit owner authorization for the exact one-time paid run, including the
  new absolute evidence path and export directory.

Until every gate is complete, the current truth is only
`L5_HARNESS_REVIEW_READY` / authorization pending. No `.env` presence check,
Secret access, Docker/PG/API/Web/browser runtime, Provider/model request,
account/paid action, or live evidence is part of this Phase-A record.
