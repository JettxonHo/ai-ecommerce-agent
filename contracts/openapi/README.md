# Authored OpenAPI contract

`openapi.yaml` is the single authored OpenAPI 3.1 entry document for the
MVP-0 `/api/v1` public HTTP boundary. It is maintained from RFC-004 and
DEC-063--066. Future generated clients and runtime conformance tests consume
this document; no handler, framework-generated schema, DTO reference, or
generated artifact may replace or edit it.

The contract describes a server-bound fixed workspace and loopback same-origin
transport. It does not mean that an HTTP server, database, worker, model
provider, or frontend is implemented.

## Deterministic local validation

Run from `apps/backend/` after `uv sync --locked`:

```bash
uv run openapi-spec-validator ../../contracts/openapi/openapi.yaml
uv run python ../../contracts/openapi/tools/validate.py \
  ../../contracts/openapi/openapi.yaml
```

The first command performs specification-level OAS 3.1 validation using the
official `python-openapi/openapi-spec-validator` package. The second command
checks the accepted operation catalog, operation IDs, local `$ref`s, required
schema families, success media types, `/api/v1` namespace, and required
`Idempotency-Key` usage. Both commands are read-only.

`openapi-spec-validator==0.9.0` is a dev-only dependency. The [official
documentation](https://python-openapi.org/openapi-spec-validator/docs/latest/)
lists OAS 3.1 support, a CLI, and Python API usage; the [PyPI release
metadata](https://pypi.org/project/openapi-spec-validator/0.9.0/) declares
Python `>=3.10,<4.0` and ships a pure-Python wheel, compatible with this
repository's Python 3.13 environment. The validator never generates or
rewrites an OpenAPI document.

## Breaking-diff boundary

The compatibility command compares an explicit prior accepted baseline to a
candidate and returns exit status `1` for a breaking change. It never modifies
either input:

```bash
uv run python ../../contracts/openapi/tools/diff.py \
  /path/to/accepted-openapi.yaml \
  ../../contracts/openapi/openapi.yaml
```

In CI, the baseline should be exported from the last accepted Contract commit
(for example, with `git show <accepted-commit>:contracts/openapi/openapi.yaml`)
to a temporary file. The current entry document is not copied into the
repository as a second authority. The bounded diff checks the accepted `/api/v1`
rules: removed paths or operations, removed response status/media types,
removed parameters/request bodies, removed schemas/properties, added required
fields, changed types/refs, and removed enum values. Additive optional fields
and operations remain compatible, subject to the RFC-004 review gate.

## Scope reminder

The first-Goal operation catalog, status enums, typed semantic preconditions,
idempotent replay response distinction (`201`/`202` first, `200` replay), Run
monitor, Review Draft, immutable Brief / Export Snapshot, and finite RFC 9457
Problem catalog are intentionally bounded. Source content, upload, processing,
Fragment, Locator, Evidence, and Retrieval operations remain owned by RFC-005
and are not invented here.
