# MVP-0L L3 Docker-only Local Web Lifecycle Review

**Status:** offline implementation `GREEN`; the historical first provider-free
runtime is `HOLD` (image-build failure only), and the single bounded repair
runtime is `PASS`. Independent five-axis review, commit/PR and merge remain
pending. This document records implementation evidence only and does not
approve or merge the change.

## Baseline and authority

- Live contract: [Issue #331](https://github.com/JettxonHo/ai-ecommerce-agent/issues/331),
  including its frozen 22-path allowlist, non-goals and safety/stop conditions.
- Accepted decision: [DEC-085](../decisions/dec-085-docker-only-local-web-lifecycle.md),
  which preserves the host-development lifecycle while adding a guarded
  Docker-only `local-web` profile.
- Isolated clone: `/private/tmp/ai-ecommerce-agent-331-q9oSSB`.
- Branch: `codex/mvp0l-l3-docker-local-web`.
- Base: `origin/main@dbccacacc54cb21c393987a8612dfc6aa825093b` (exact frozen
  merge-effective L2 base; Issue #329 and PR #330 are closed/merged-current).
- The initial clone and branch were clean before edits. No shared checkout,
  prior #318/#329 worktree, provider, Secret, `.env`, migration, public
  contract, dependency or lockfile was touched.
- Agent configuration was parsed with Python 3.12 and matched exactly
  `luna-worker` / `gpt-5.6-luna` / `max`; only `CONFIG_VERIFIED` is claimed.
  Runtime model identity is not exposed and is not claimed.

## TDD boundary

Before production edits, the executable `scripts/mvp0/test-local-web` produced a
true RED for the missing Docker-only lifecycle entry:

```text
FAIL: missing executable Docker-only lifecycle entry: /private/tmp/ai-ecommerce-agent-331-q9oSSB/scripts/mvp0/local-web
```

Additional proportional characterization REDs captured the existing host-dev
`.env` compatibility requirement, the Dockerfile dependency/project ordering,
and the invalid `open -a "$app_path"` path invocation. GREEN then restored the
host `mvp0_compose` behavior, introduced the separate no-`.env` local-Web
wrapper, opened Docker Desktop with `open "$app_path"` before bounded
`docker info` polling, and implemented the locked two-phase backend image
build.

## Historical first runtime and bounded repair

The ORCHESTRATOR_REVIEWER bounded repair/runtime ruling on [Issue #331](https://github.com/JettxonHo/ai-ecommerce-agent/issues/331#issuecomment-5442500417)
records the first authorized provider-free `--ephemeral` runtime as a
historical `HOLD`: it reached image build only, the Web image built, and the
API image failed because `apps/backend/Dockerfile.local` requested the
unpublished `uv==0.12.8` pin. No service was created, and no health,
browser or product-behavior result was produced. The guarded lifecycle cleaned
the emitted ephemeral container, network and paired volume; loopback ports
were free and unrelated/default resources were unchanged. This is not product
acceptance and not a product-behavior failure.

Under the owner's standing serial-order instruction, that ruling authorized
exactly one bounded repair and exactly one new provider-free runtime attempt.
Tests first added an exact `uv==0.12.6`
requirement and rejected `uv==0.12.8`; with the Dockerfile still unchanged,
`bash scripts/mvp0/test-local-web` produced the intended RED:

~~~text
FAIL: backend Dockerfile must use the published official uv==0.12.6 pin and reject uv==0.12.8
~~~

The only production-byte repair is the backend Dockerfile pin
`uv==0.12.8` → `uv==0.12.6`. The locked two-phase sync, base images,
package/lock files and all other production bytes remain frozen. The focused
fake lifecycle, shell/static checks, Dockerfile provenance, lock identity and
scope checks are now GREEN; the changed-path inventory remains exactly the
known 21 allowlisted paths, with no lingering local-Web process and no runtime
resources started before the new attempt.

The single new `scripts/mvp0/local-web --ephemeral` runtime completed `PASS`
with project `ai-ecommerce-agent-mvp0-ephemeral-260827171237-60805-30829` and
paired volume `ai-ecommerce-agent-mvp0-ephemeral-260827171237-60805-30829-pg`.
The Web and API images built, PostgreSQL/API/Web health passed, and the wrapper
opened the system browser only after health. One bounded `/tasks` read reached
the page titled “商品上新行动工作台” with heading “行动首页”. Exactly one
Ctrl-C returned 130; the target containers, network and paired volume were
absent afterward, ports 5173/55432 were free, and the default/unrelated
resource identities were unchanged. No Provider/model/Secret/.env access was
made.

This `PASS` is runtime evidence only. Independent five-axis review, commit/PR
and merge remain pending; no self-approval or merge is claimed here.

## Implemented contract

- The tracked `AI Ecommerce Agent.command` delegates to
  `scripts/mvp0/local-web`.
- `compose.yaml` keeps the default host path as Postgres-only with
  `${MVP0_...:-default}` interpolation. The explicit `local-web` profile adds
  exactly `postgres`, private `api` and loopback-bound static `web`.
- API is not host-published (`expose: 8000` only), uses internal
  `postgres:5432`, and has a bounded healthcheck. Web publishes only
  `127.0.0.1:5173:8080`, proxies `/api/` to `api:8000`, and has a bounded
  `/tasks` healthcheck.
- `mvp0_local_web_compose` always passes `--env-file /dev/null` and the
  `local-web` profile. Its non-secret local interpolation values are fixed, so
  hostile caller environment values cannot change topology, credentials or
  port; only validated project and paired-volume identities are variable.
- Default lifecycle cleanup removes owned containers/network while preserving
  `ai-ecommerce-agent-mvp0-postgres-data`. `--ephemeral` creates a validated
  repository-prefixed project and exact `${project}-pg` volume, then removes
  that paired volume with `down --volumes --remove-orphans`.
- Browser opening follows Compose `up --wait`, Web loopback health and exact
  sorted running service membership `{api, postgres, web}`. Missing, extra or
  permuted Compose service output is handled deterministically. Stop/status
  use the same local-Web wrapper; TERM/INT cleanup is bounded and owned.
- `apps/backend/Dockerfile.local` performs locked dependency hydration before
  copying project files, then locked non-editable project installation. Web
  dependencies are installed from the committed npm lockfile; no lockfile is
  modified.

## Offline evidence

The following completed without provider/model calls, Secret access, `.env`
inspection or Docker container creation:

- `scripts/mvp0/test-local-web`: PASS (fake Docker Desktop open-before-poll,
  fixed interpolation, browser/readiness ordering, default-volume protection,
  exact service-set monitor, port/architecture/desktop failures and ephemeral
  paired cleanup).
- `scripts/mvp0/test-static`: PASS (default Postgres-only and rendered
  `local-web` configuration, static lifecycle/migration seams and the focused
  harness).
- R1/R2 follow-up: the executable root `AI Ecommerce Agent.command` is guarded
  to one exact `scripts/mvp0/local-web` delegation (a controlled misdirected
  fixture is rejected), and oversized readiness limits fail before Compose or
  browser mutation. The central fixed upper bound is 600 attempts; existing
  value `2` and default `60` remain unchanged.
- Backend: `pytest tests/unit/test_local_demo_entrypoint.py` 6 passed;
  architecture tests 174 passed; Ruff and Pyright pass under locked offline
  `uv`; `uv sync --locked --dev --offline` succeeded with no lock diff.
- Web (Node `24.18.0`, npm `11.16.0`): `npm ci --offline` succeeded;
  format, lint, typecheck, unit (120 passed), contract (50 passed), generated
  API check and production build all pass. `apps/web/package-lock.json` and
  backend `uv.lock` remain byte-identical.
- `git diff --check` passes. The changed-path inventory is 21 allowlisted
  paths (the optional `scripts/mvp0/test-lifecycle` path is untouched); no
  23rd path is required.

## Remaining gate

One provider-free `scripts/mvp0/local-web --ephemeral` runtime completed `PASS` with
the required image-build, PostgreSQL/API/Web health, browser-after-health,
bounded `/tasks`, Ctrl-C and exact cleanup evidence. Remaining gates are final
evidence reconciliation, ordinary commit/Ready PR, fresh Required Checks and
independent five-axis review/merge. No additional runtime is authorized; no
retry, second scope, raw Compose invocation or provider/model call is permitted.
