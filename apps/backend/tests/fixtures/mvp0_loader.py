"""Deterministic loader and narrow validator for the repository MVP-0 pack.

The fixture data itself lives at the repository-level ``tests/fixtures/mvp0``
path. This test-only helper deliberately validates only the invariants needed
by the acceptance pack; it is not a general fixture framework.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

FIXTURE_ROOT = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "mvp0"
MANIFEST_PATH = FIXTURE_ROOT / "manifest.yaml"

REQUIRED_FIXTURE_IDS = frozenset(
    {
        "fixture-sufficient-v1",
        "fixture-limited-v1",
        "fixture-conflict-v1",
        "mutation-sufficient-v1",
    }
)
ALLOWED_SOURCE_SUFFIXES = frozenset({".json", ".md", ".txt", ".csv"})
FORBIDDEN_CONTENT = re.compile(
    r"(?:https?://|api[_-]?key|access[_-]?token|password|credential|secret|sha-?256)",
    re.IGNORECASE,
)


class FixtureValidationError(ValueError):
    """Raised when the physical fixture pack violates a required invariant."""


@dataclass(frozen=True)
class FixtureReference:
    """A manifest fixture entry resolved against the physical fixture root."""

    fixture_id: str
    fixture_version: str
    kind: str
    directory: Path
    source_paths: tuple[Path, ...]
    expected_behavior_path: Path
    base_fixture_id: str | None


@dataclass(frozen=True)
class FixtureManifest:
    """Validated manifest and its four stable fixture references."""

    path: Path
    manifest_version: str
    anchor_sku: str
    fixtures: tuple[FixtureReference, ...]

    def fixture(self, fixture_id: str) -> FixtureReference:
        """Return one stable fixture reference by logical ID."""

        for fixture in self.fixtures:
            if fixture.fixture_id == fixture_id:
                return fixture
        raise KeyError(fixture_id)


def load_manifest(path: Path = MANIFEST_PATH) -> FixtureManifest:
    """Load and validate the JSON-compatible YAML manifest deterministically."""

    try:
        decoded: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FixtureValidationError(f"cannot read manifest {path}: {exc}") from exc

    document = _mapping(decoded, "manifest")
    errors: list[str] = []
    _validate_manifest_shape(document, path, errors)
    if errors:
        raise FixtureValidationError("; ".join(errors))

    manifest_version = _string(document["manifest_version"], "manifest_version")
    anchor = _mapping(document["anchor_sku"], "anchor_sku")
    anchor_sku = _string(anchor["sku_id"], "anchor_sku.sku_id")
    raw_fixtures = _sequence(document["fixtures"], "fixtures")
    fixtures: list[FixtureReference] = []

    for index, raw_fixture in enumerate(raw_fixtures):
        context = f"fixtures[{index}]"
        try:
            fixture = _resolve_fixture(raw_fixture, path.parent, context)
        except FixtureValidationError as exc:
            errors.append(str(exc))
            continue
        _validate_fixture_files(fixture, context, errors)
        fixtures.append(fixture)

    fixture_ids = {fixture.fixture_id for fixture in fixtures}
    if fixture_ids != set(REQUIRED_FIXTURE_IDS):
        errors.append(
            "fixtures resolve to "
            f"{sorted(fixture_ids)!r}, expected {sorted(REQUIRED_FIXTURE_IDS)!r}"
        )
    if errors:
        raise FixtureValidationError("; ".join(errors))

    return FixtureManifest(
        path=path,
        manifest_version=manifest_version,
        anchor_sku=anchor_sku,
        fixtures=tuple(fixtures),
    )


def _validate_manifest_shape(
    document: Mapping[str, object], path: Path, errors: list[str]
) -> None:
    required_keys = {
        "manifest_id",
        "manifest_version",
        "fixture_authority",
        "data_notice",
        "anchor_sku",
        "allowed_source_formats",
        "forbidden_source_formats",
        "accepted_logical_fixture_ids",
        "fixtures",
    }
    missing = sorted(required_keys - document.keys())
    if missing:
        errors.append(f"{path}: missing manifest keys {missing!r}")
        return

    for key in ("manifest_id", "manifest_version", "fixture_authority"):
        _check_string(document.get(key), f"manifest.{key}", errors)

    notice = _mapping_or_error(
        document.get("data_notice"), "manifest.data_notice", errors
    )
    if notice is not None:
        expected_notice = {
            "fictional": True,
            "synthetic": True,
            "non_regulated": True,
            "contains_real_personal_data": False,
            "contains_real_merchant_data": False,
            "contains_provider_payload": False,
            "network_access_required": False,
        }
        for key, expected in expected_notice.items():
            if notice.get(key) is not expected:
                errors.append(f"manifest.data_notice.{key} must be {expected!r}")

    allowed = _sequence_or_error(
        document.get("allowed_source_formats"),
        "manifest.allowed_source_formats",
        errors,
    )
    if allowed is not None and set(_strings(allowed, "allowed_source_formats")) != {
        "json",
        "structured-text",
        "txt",
        "markdown",
        "csv",
    }:
        errors.append(
            "manifest.allowed_source_formats does not match the accepted format set"
        )

    forbidden = _sequence_or_error(
        document.get("forbidden_source_formats"),
        "manifest.forbidden_source_formats",
        errors,
    )
    if forbidden is not None and not {"pdf", "image", "ocr", "network"}.issubset(
        _strings(forbidden, "forbidden_source_formats")
    ):
        errors.append(
            "manifest.forbidden_source_formats must include pdf, image, ocr, network"
        )

    accepted = _sequence_or_error(
        document.get("accepted_logical_fixture_ids"),
        "manifest.accepted_logical_fixture_ids",
        errors,
    )
    if accepted is not None and set(
        _strings(accepted, "accepted_logical_fixture_ids")
    ) != set(REQUIRED_FIXTURE_IDS):
        errors.append(
            "manifest.accepted_logical_fixture_ids does not match the frozen IDs"
        )


def _resolve_fixture(raw_fixture: object, root: Path, context: str) -> FixtureReference:
    fixture = _mapping(raw_fixture, context)
    required = {
        "fixture_id",
        "fixture_version",
        "kind",
        "scenario_role",
        "directory",
        "source_files",
        "expected_behavior_file",
        "required_formats",
    }
    missing = sorted(required - fixture.keys())
    if missing:
        raise FixtureValidationError(f"{context} missing keys {missing!r}")

    fixture_id = _string(fixture["fixture_id"], f"{context}.fixture_id")
    fixture_version = _string(fixture["fixture_version"], f"{context}.fixture_version")
    kind = _string(fixture["kind"], f"{context}.kind")
    directory = _safe_relative_path(fixture["directory"], f"{context}.directory")
    expected_relative = _safe_relative_path(
        fixture["expected_behavior_file"], f"{context}.expected_behavior_file"
    )
    source_files = _sequence(fixture["source_files"], f"{context}.source_files")
    source_relatives = tuple(
        _safe_relative_path(value, f"{context}.source_files[{index}]")
        for index, value in enumerate(source_files)
    )
    _strings(
        _sequence(fixture["required_formats"], f"{context}.required_formats"), context
    )
    base_fixture_id = fixture.get("base_fixture_id")
    if base_fixture_id is not None and not isinstance(base_fixture_id, str):
        raise FixtureValidationError(f"{context}.base_fixture_id must be a string")

    return FixtureReference(
        fixture_id=fixture_id,
        fixture_version=fixture_version,
        kind=kind,
        directory=root / directory,
        source_paths=tuple(
            root / directory / relative for relative in source_relatives
        ),
        expected_behavior_path=root / expected_relative,
        base_fixture_id=base_fixture_id,
    )


def _validate_fixture_files(
    fixture: FixtureReference, context: str, errors: list[str]
) -> None:
    if not fixture.directory.is_dir():
        errors.append(f"{context} directory does not exist: {fixture.directory}")
        return
    if not fixture.expected_behavior_path.is_file():
        errors.append(
            f"{context} expected behavior file does not exist: "
            f"{fixture.expected_behavior_path}"
        )
    listed_names = {path.name for path in fixture.source_paths}
    actual_names = {path.name for path in fixture.directory.iterdir() if path.is_file()}
    if listed_names != actual_names:
        errors.append(
            f"{context} source list {sorted(listed_names)!r} differs "
            "from physical files "
            f"{sorted(actual_names)!r}"
        )

    for source_path in fixture.source_paths:
        if not source_path.is_file():
            errors.append(f"{context} source file does not exist: {source_path}")
            continue
        if source_path.suffix.lower() not in ALLOWED_SOURCE_SUFFIXES:
            errors.append(
                f"{context} has unsupported source suffix: {source_path.name}"
            )
            continue
        _validate_text_file(source_path, context, errors)

    if fixture.expected_behavior_path.is_file():
        _validate_expected_behavior(
            fixture.expected_behavior_path, fixture.fixture_id, context, errors
        )


def _validate_text_file(path: Path, context: str, errors: list[str]) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{context} cannot read {path.name} as UTF-8: {exc}")
        return
    lowered = content.lower()
    if "fictional" not in lowered or "synthetic" not in lowered:
        errors.append(f"{context} source {path.name} lacks fictional/synthetic notice")
    if FORBIDDEN_CONTENT.search(content):
        errors.append(
            f"{context} source {path.name} contains forbidden secret/network/hash text"
        )
    if "anchor-city-commuter-backpack" not in content:
        errors.append(
            f"{context} source {path.name} lacks the shared Anchor SKU identity"
        )


def _validate_expected_behavior(
    path: Path, fixture_id: str, context: str, errors: list[str]
) -> None:
    try:
        decoded: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{context} expected behavior is not readable JSON: {exc}")
        return
    document = _mapping_or_error(decoded, f"{context}.expected_behavior", errors)
    if document is None:
        return
    if document.get("fixture_id") != fixture_id:
        errors.append(f"{context} expected behavior fixture_id does not match")
    notice = _mapping_or_error(
        document.get("data_notice"), f"{context}.expected_behavior.data_notice", errors
    )
    if notice is not None:
        for key in ("fictional", "synthetic", "non_regulated"):
            if notice.get(key) is not True:
                errors.append(
                    f"{context} expected behavior data_notice.{key} must be true"
                )
    for key in ("hard_gates", "human_usability_inputs", "non_requirements"):
        if key not in document:
            errors.append(f"{context} expected behavior missing {key}")
    if "generation" not in json.dumps(document, ensure_ascii=False).lower():
        errors.append(
            f"{context} expected behavior must separate generation from approval"
        )


def _mapping(value: object, context: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise FixtureValidationError(f"{context} must be an object")
    return cast(Mapping[str, object], value)


def _mapping_or_error(
    value: object, context: str, errors: list[str]
) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        errors.append(f"{context} must be an object")
        return None
    return cast(Mapping[str, object], value)


def _sequence(value: object, context: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise FixtureValidationError(f"{context} must be an array")
    return cast(Sequence[object], value)


def _sequence_or_error(
    value: object, context: str, errors: list[str]
) -> Sequence[object] | None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        errors.append(f"{context} must be an array")
        return None
    return cast(Sequence[object], value)


def _strings(values: Sequence[object], context: str) -> list[str]:
    strings: list[str] = []
    for index, value in enumerate(values):
        strings.append(_string(value, f"{context}[{index}]"))
    return strings


def _string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise FixtureValidationError(f"{context} must be a non-empty string")
    return value


def _check_string(value: object, context: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{context} must be a non-empty string")


def _safe_relative_path(value: object, context: str) -> Path:
    path = Path(_string(value, context))
    if path.is_absolute() or ".." in path.parts:
        raise FixtureValidationError(f"{context} must be a safe relative path")
    return path
