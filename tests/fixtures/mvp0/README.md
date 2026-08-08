# MVP-0 acceptance fixtures

This directory is the single, repository-level acceptance-data authority for
the first end-to-end demo. Every record is **fictional, synthetic, and
non-regulated**; it is not a real merchant listing, customer study, review
export, private token, or provider response.

The four stable logical fixture IDs are declared in
[`manifest.yaml`](manifest.yaml):

- `fixture-sufficient-v1` — sufficient material for the normal closed loop;
- `fixture-limited-v1` — intentionally limited material that must still run
  while exposing hypotheses and evidence limitations;
- `fixture-conflict-v1` — a blocking identity/fact conflict that must produce a
  finite Needs Input action request before recovery; and
- `mutation-sufficient-v1` — a readable change script based on the sufficient
  fixture.

The source set deliberately uses only JSON, structured text, TXT, Markdown,
and a synthetic comments CSV. There are no PDF or image assets, network
references, or content fingerprints. Expected behavior files describe
semantic gates and human-usability inputs; they do not snapshot complete model
wording or turn generation/QC success into approval.

## Loading

The deterministic manifest validator lives in
[`apps/backend/tests/fixtures/mvp0_loader.py`](../../../apps/backend/tests/fixtures/mvp0_loader.py)
and is exercised by
[`test_mvp0_fixture_manifest.py`](../../../apps/backend/tests/unit/test_mvp0_fixture_manifest.py).
`manifest.yaml` intentionally uses the JSON-compatible YAML subset so the
loader can remain standard-library-only and deterministic until a public
fixture consumer establishes a YAML dependency.

Backend, Browser E2E, and manual acceptance should resolve paths through the
manifest rather than duplicating source lists or expected behavior.

## Authority

The scenario roles and behavior gates come from [DEC-048](../../../docs/decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md),
[DEC-058](../../../docs/decisions/dec-058-fictional-anchor-sku-acceptance-fixture-strategy.md),
and [Testing Strategy §8](../../../docs/development/testing-strategy.md#81-fixture-authority).
This pack physicalizes those accepted roles only; it does not implement
business workflow, API, model, persistence, or browser behavior.
