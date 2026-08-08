#!/usr/bin/env python3
"""Report breaking changes between two OpenAPI documents.

The first argument is an explicit baseline (for example, a file exported from
the last accepted commit); the candidate is read-only.  This deliberately
implements only the additive compatibility rules accepted for ``/api/v1`` and
never edits either file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


HTTP_METHODS = frozenset({"get", "post", "put", "patch", "delete", "head", "options", "trace"})


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not an object document")
    return value


def _schema_breaks(
    baseline: dict[str, Any], candidate: dict[str, Any], location: str
) -> list[str]:
    changes: list[str] = []
    if "type" in baseline and baseline.get("type") != candidate.get("type"):
        changes.append(f"{location}: schema type changed")
    if "$ref" in baseline and baseline.get("$ref") != candidate.get("$ref"):
        changes.append(f"{location}: $ref changed")
    baseline_required = set(baseline.get("required", []))
    candidate_required = set(candidate.get("required", []))
    for field in sorted(baseline_required - candidate_required):
        changes.append(f"{location}: required field removed: {field}")
    for field in sorted(candidate_required - baseline_required):
        changes.append(f"{location}: new required field: {field}")
    baseline_enum = set(baseline.get("enum", []))
    if baseline_enum:
        candidate_enum = set(candidate.get("enum", []))
        for value in sorted(baseline_enum - candidate_enum, key=str):
            changes.append(f"{location}: enum value removed: {value}")
    baseline_properties = baseline.get("properties", {})
    candidate_properties = candidate.get("properties", {})
    if isinstance(baseline_properties, dict) and isinstance(candidate_properties, dict):
        for field in sorted(set(baseline_properties) - set(candidate_properties)):
            changes.append(f"{location}: property removed: {field}")
        for field in sorted(set(baseline_properties) & set(candidate_properties)):
            before = baseline_properties[field]
            after = candidate_properties[field]
            if isinstance(before, dict) and isinstance(after, dict):
                changes.extend(_schema_breaks(before, after, f"{location}.{field}"))
    return changes


def find_breaking_changes(baseline: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    changes: list[str] = []
    base_paths = baseline.get("paths", {})
    candidate_paths = candidate.get("paths", {})
    if not isinstance(base_paths, dict) or not isinstance(candidate_paths, dict):
        return ["paths: both documents must define an object"]
    for path in sorted(set(base_paths) - set(candidate_paths)):
        changes.append(f"paths: operation path removed: {path}")
    for path in sorted(set(base_paths) & set(candidate_paths)):
        before_item = base_paths[path]
        after_item = candidate_paths[path]
        if not isinstance(before_item, dict) or not isinstance(after_item, dict):
            changes.append(f"paths.{path}: path item changed shape")
            continue
        for method in sorted(set(before_item) & HTTP_METHODS):
            if method not in after_item:
                changes.append(f"paths.{path}: operation removed: {method.upper()}")
                continue
            before_op = before_item[method]
            after_op = after_item[method]
            if not isinstance(before_op, dict) or not isinstance(after_op, dict):
                changes.append(f"paths.{path}.{method}: operation changed shape")
                continue
            before_responses = before_op.get("responses", {})
            after_responses = after_op.get("responses", {})
            if isinstance(before_responses, dict) and isinstance(after_responses, dict):
                for status in sorted(set(before_responses) - set(after_responses)):
                    changes.append(f"paths.{path}.{method}: response removed: {status}")
                for status in sorted(set(before_responses) & set(after_responses)):
                    before_response = before_responses[status]
                    after_response = after_responses[status]
                    if not isinstance(before_response, dict) or not isinstance(after_response, dict):
                        continue
                    before_content = before_response.get("content", {})
                    after_content = after_response.get("content", {})
                    if isinstance(before_content, dict) and isinstance(after_content, dict):
                        for media_type in sorted(set(before_content) - set(after_content)):
                            changes.append(
                                f"paths.{path}.{method}: response {status} media type removed: {media_type}"
                            )
            # A request parameter or body removal is breaking.  Additions are
            # compatible only when optional, so this tool intentionally leaves
            # additive optional parameters to the accepted review process.
            before_parameters = before_op.get("parameters", [])
            after_parameters = after_op.get("parameters", [])
            before_refs = {
                item.get("$ref")
                for item in before_parameters
                if isinstance(item, dict) and isinstance(item.get("$ref"), str)
            }
            after_refs = {
                item.get("$ref")
                for item in after_parameters
                if isinstance(item, dict) and isinstance(item.get("$ref"), str)
            }
            for reference in sorted(before_refs - after_refs):
                changes.append(f"paths.{path}.{method}: parameter removed: {reference}")
            if "requestBody" in before_op and "requestBody" not in after_op:
                changes.append(f"paths.{path}.{method}: request body removed")

    baseline_schemas = baseline.get("components", {}).get("schemas", {})
    candidate_schemas = candidate.get("components", {}).get("schemas", {})
    if isinstance(baseline_schemas, dict) and isinstance(candidate_schemas, dict):
        for name in sorted(set(baseline_schemas) - set(candidate_schemas)):
            changes.append(f"components.schemas: schema removed: {name}")
        for name in sorted(set(baseline_schemas) & set(candidate_schemas)):
            before = baseline_schemas[name]
            after = candidate_schemas[name]
            if isinstance(before, dict) and isinstance(after, dict):
                changes.extend(_schema_breaks(before, after, f"components.schemas.{name}"))
    return changes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path, help="explicit prior accepted OpenAPI document")
    parser.add_argument("candidate", type=Path, help="candidate authored OpenAPI document")
    args = parser.parse_args(argv)
    try:
        changes = find_breaking_changes(_load(args.baseline), _load(args.candidate))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"contract diff failed: {exc}", file=sys.stderr)
        return 2
    if changes:
        print("Breaking contract changes detected:")
        for change in changes:
            print(f"- {change}")
        return 1
    print("No breaking /api/v1 contract changes detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
