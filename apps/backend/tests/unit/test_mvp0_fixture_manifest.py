"""Structural tests for the repository-level MVP-0 acceptance pack."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from fixtures.mvp0_loader import (
    FIXTURE_ROOT,
    MANIFEST_PATH,
    REQUIRED_FIXTURE_IDS,
    FixtureValidationError,
    load_manifest,
)


@pytest.mark.unit
def test_manifest_resolves_the_four_frozen_fixture_ids() -> None:
    manifest = load_manifest()

    assert manifest.path == MANIFEST_PATH
    assert manifest.anchor_sku == "anchor-city-commuter-backpack"
    assert tuple(fixture.fixture_id for fixture in manifest.fixtures) == (
        "fixture-sufficient-v1",
        "fixture-limited-v1",
        "fixture-conflict-v1",
        "mutation-sufficient-v1",
    )
    assert {fixture.fixture_id for fixture in manifest.fixtures} == REQUIRED_FIXTURE_IDS
    assert all(fixture.fixture_version == "v1" for fixture in manifest.fixtures)
    assert all(
        fixture.expected_behavior_path.is_file() for fixture in manifest.fixtures
    )


@pytest.mark.unit
def test_sources_are_only_allowed_text_formats_and_are_fictional() -> None:
    manifest = load_manifest()

    source_paths = [
        path for fixture in manifest.fixtures for path in fixture.source_paths
    ]
    assert source_paths
    assert all(path.is_relative_to(FIXTURE_ROOT) for path in source_paths)
    assert {path.suffix for path in source_paths} <= {".json", ".md", ".txt", ".csv"}
    assert any(path.suffix == ".csv" for path in source_paths)
    assert any(path.suffix == ".md" for path in source_paths)
    assert any(path.suffix == ".txt" for path in source_paths)
    assert any(path.suffix == ".json" for path in source_paths)
    for source_path in source_paths:
        content = source_path.read_text(encoding="utf-8").lower()
        assert "fictional" in content
        assert "synthetic" in content
        assert "anchor-city-commuter-backpack" in content


@pytest.mark.unit
def test_expected_behavior_keeps_hard_gates_separate_from_human_judgment() -> None:
    manifest = load_manifest()

    for fixture in manifest.fixtures:
        expected = json.loads(
            fixture.expected_behavior_path.read_text(encoding="utf-8")
        )
        assert "hard_gates" in expected
        assert "human_usability_inputs" in expected
        assert "non_requirements" in expected
        expected_text = json.dumps(expected, ensure_ascii=False).lower()
        assert "generation" in expected_text
        assert "approved" in expected_text or "approval" in expected_text
        assert "score" not in expected_text


@pytest.mark.unit
def test_mutation_points_to_sufficient_fixture_and_changes_readable_version() -> None:
    manifest = load_manifest()
    mutation = manifest.fixture("mutation-sufficient-v1")
    sufficient = manifest.fixture("fixture-sufficient-v1")

    assert mutation.kind == "mutation"
    assert mutation.base_fixture_id == sufficient.fixture_id
    mutation_script = (mutation.directory / "mutation.md").read_text(encoding="utf-8")
    changed_source = (mutation.directory / "changed-product.json").read_text(
        encoding="utf-8"
    )
    assert "source-sufficient-product-v1" in mutation_script
    assert "source-sufficient-product-v2" in mutation_script
    assert '"source_version": "source-sufficient-product-v2"' in changed_source
    assert '"replaces_source_version": "source-sufficient-product-v1"' in changed_source
    assert "确认" in mutation_script
    assert "superseded" in mutation_script.lower()


@pytest.mark.unit
def test_manifest_validation_rejects_missing_authority_key(tmp_path: Path) -> None:
    document = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    del document["accepted_logical_fixture_ids"]
    invalid_manifest = tmp_path / "manifest.yaml"
    invalid_manifest.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(FixtureValidationError, match="missing manifest keys"):
        load_manifest(invalid_manifest)


@pytest.mark.unit
def test_manifest_validation_rejects_required_format_drift(tmp_path: Path) -> None:
    copied_root = tmp_path / "mvp0"
    shutil.copytree(FIXTURE_ROOT, copied_root)
    manifest_path = copied_root / "manifest.yaml"
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    document["fixtures"][0]["required_formats"] = ["json", "markdown", "txt"]
    manifest_path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(FixtureValidationError, match="required_formats"):
        load_manifest(manifest_path)
