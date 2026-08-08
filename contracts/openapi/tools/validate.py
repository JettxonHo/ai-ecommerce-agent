#!/usr/bin/env python3
"""Validate and lint the authored OpenAPI entry document.

The OpenAPI Description remains the authority.  This helper only reads the
document and checks the accepted RFC-004 catalog; it never writes or generates
another contract.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename
from openapi_spec_validator.validation.validators import OpenAPIV31SpecValidator


EXPECTED_OPERATIONS: dict[str, frozenset[str]] = {
    "/api/v1/tasks": frozenset({"get", "post"}),
    "/api/v1/tasks/{taskId}": frozenset({"get"}),
    "/api/v1/tasks/{taskId}/commands/start": frozenset({"post"}),
    "/api/v1/tasks/{taskId}/commands/rerun": frozenset({"post"}),
    "/api/v1/runs/{runId}": frozenset({"get"}),
    "/api/v1/runs/{runId}/commands/cancel": frozenset({"post"}),
    "/api/v1/runs/{runId}/commands/resume": frozenset({"post"}),
    "/api/v1/runs/{runId}/commands/retry-current-stage": frozenset({"post"}),
    "/api/v1/runs/{runId}/commands/restart-from-safe-boundary": frozenset({"post"}),
    "/api/v1/needs-input-requests/{actionRequestId}": frozenset({"get"}),
    "/api/v1/needs-input-requests/{actionRequestId}/commands/resolve": frozenset({"post"}),
    "/api/v1/tasks/{taskId}/source-associations/{sourceAssociationId}/previews/remove": frozenset({"post"}),
    "/api/v1/tasks/{taskId}/source-associations/{sourceAssociationId}/commands/remove": frozenset({"post"}),
    "/api/v1/tasks/{taskId}/source-associations/{sourceAssociationId}/previews/replace": frozenset({"post"}),
    "/api/v1/tasks/{taskId}/source-associations/{sourceAssociationId}/commands/replace": frozenset({"post"}),
    "/api/v1/review-packages/{reviewPackageId}": frozenset({"get"}),
    "/api/v1/review-packages/{reviewPackageId}/draft": frozenset({"get", "put"}),
    "/api/v1/review-packages/{reviewPackageId}/commands/submit": frozenset({"post"}),
    "/api/v1/review-packages/{reviewPackageId}/commands/request-more-information": frozenset({"post"}),
    "/api/v1/review-packages/{reviewPackageId}/commands/reject-all-and-request-regeneration": frozenset({"post"}),
    "/api/v1/approved-strategies/{approvedStrategyVersionId}": frozenset({"get"}),
    "/api/v1/approved-strategies/{approvedStrategyVersionId}/commands/withdraw": frozenset({"post"}),
    "/api/v1/tasks/{taskId}/marketing-briefs": frozenset({"get"}),
    "/api/v1/marketing-briefs/{marketingBriefVersionId}": frozenset({"get"}),
    "/api/v1/marketing-brief-comparisons": frozenset({"post"}),
    "/api/v1/marketing-briefs/{marketingBriefVersionId}/commands/revise": frozenset({"post"}),
    "/api/v1/tasks/{taskId}/xiaohongshu-briefs": frozenset({"get"}),
    "/api/v1/xiaohongshu-briefs/{xiaohongshuBriefVersionId}": frozenset({"get"}),
    "/api/v1/xiaohongshu-brief-comparisons": frozenset({"post"}),
    "/api/v1/xiaohongshu-briefs/{xiaohongshuBriefVersionId}/commands/revise": frozenset({"post"}),
    "/api/v1/tasks/{taskId}/export-previews": frozenset({"post"}),
    "/api/v1/export-snapshots": frozenset({"post"}),
    "/api/v1/export-snapshots/{exportSnapshotId}": frozenset({"get"}),
    "/api/v1/export-snapshots/{exportSnapshotId}/content": frozenset({"get"}),
}

IDEMPOTENT_OPERATIONS = frozenset(
    {
        "createTask",
        "startTask",
        "rerunTask",
        "cancelRun",
        "resumeRun",
        "retryCurrentStage",
        "restartFromSafeBoundary",
        "resolveNeedsInput",
        "removeSourceAssociation",
        "replaceSourceAssociation",
        "putReviewDraft",
        "submitReview",
        "requestMoreInformation",
        "rejectAllAndRequestRegeneration",
        "withdrawApprovedStrategy",
        "reviseMarketingBrief",
        "reviseXiaohongshuBrief",
        "createExportSnapshot",
    }
)

REQUIRED_SCHEMAS = frozenset(
    {
        "CreateTaskRequest",
        "TaskSummaryList",
        "TaskSummary",
        "TaskOverview",
        "StageSummary",
        "CommandReceipt",
        "Run",
        "NeedsInputActionRequest",
        "ReviewSemanticGroup",
        "BriefSemanticGroup",
        "NeedsInputResolution",
        "ReviewPackage",
        "ApprovedStrategySemanticGroup",
        "MarketingBriefSemanticGroup",
        "XiaohongshuBriefSemanticGroup",
        "ReviewDraft",
        "ReviewOutcomeResult",
        "ApprovedStrategyVersion",
        "MarketingBriefVersion",
        "XiaohongshuBriefVersion",
        "BriefComparison",
        "ExportPreview",
        "ExportSnapshot",
        "ProblemDetails",
    }
)


def _walk_refs(value: Any) -> Iterator[str]:
    if isinstance(value, dict):
        reference = value.get("$ref")
        if isinstance(reference, str):
            yield reference
        for child in value.values():
            yield from _walk_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_refs(child)


def _resolve_local(spec: dict[str, Any], reference: str) -> Any:
    if not reference.startswith("#/"):
        raise ValueError(f"non-local reference is not allowed in the entry document: {reference}")
    value: Any = spec
    for part in reference[2:].split("/"):
        value = value[part.replace("~1", "/").replace("~0", "~")]
    return value


def _lint_catalog(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    paths = spec.get("paths", {})
    if set(paths) != set(EXPECTED_OPERATIONS):
        missing = sorted(set(EXPECTED_OPERATIONS) - set(paths))
        extra = sorted(set(paths) - set(EXPECTED_OPERATIONS))
        if missing:
            errors.append(f"missing paths: {', '.join(missing)}")
        if extra:
            errors.append(f"unfrozen paths: {', '.join(extra)}")

    operation_ids: set[str] = set()
    for path, expected_methods in EXPECTED_OPERATIONS.items():
        path_item = paths.get(path, {})
        actual_methods = {key for key in path_item if key in {"get", "post", "put", "patch", "delete"}}
        if actual_methods != set(expected_methods):
            errors.append(f"{path}: methods {sorted(actual_methods)} != {sorted(expected_methods)}")
        for method in expected_methods:
            operation = path_item.get(method, {})
            operation_id = operation.get("operationId")
            if not isinstance(operation_id, str) or not operation_id:
                errors.append(f"{method.upper()} {path}: missing operationId")
            elif operation_id in operation_ids:
                errors.append(f"duplicate operationId: {operation_id}")
            else:
                operation_ids.add(operation_id)
            if not operation.get("responses"):
                errors.append(f"{method.upper()} {path}: responses are required")
            for response_code, response in operation.get("responses", {}).items():
                resolved = _resolve_local(spec, response["$ref"]) if "$ref" in response else response
                if not isinstance(resolved, dict):
                    errors.append(f"{method.upper()} {path} {response_code}: invalid response")
                    continue
                if response_code.startswith("2") and response_code != "204":
                    content = resolved.get("content")
                    if not isinstance(content, dict) or not content:
                        errors.append(f"{method.upper()} {path} {response_code}: success media type is missing")
            if operation_id in IDEMPOTENT_OPERATIONS:
                parameters = operation.get("parameters", [])
                if not any(
                    isinstance(parameter, dict)
                    and parameter.get("$ref") == "#/components/parameters/IdempotencyKey"
                    for parameter in parameters
                ):
                    errors.append(f"{operation_id}: Idempotency-Key parameter is required")

    schema_names = set(spec.get("components", {}).get("schemas", {}))
    missing_schemas = sorted(REQUIRED_SCHEMAS - schema_names)
    if missing_schemas:
        errors.append(f"missing required schemas: {', '.join(missing_schemas)}")

    for reference in _walk_refs(spec):
        try:
            _resolve_local(spec, reference)
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"unresolved reference {reference}: {exc}")
    return errors


def validate_contract(path: Path) -> list[str]:
    spec, base_uri = read_from_filename(str(path))
    validate(spec, cls=OpenAPIV31SpecValidator, base_uri=base_uri)
    if spec.get("openapi") != "3.1.0":
        return ["openapi must use the accepted 3.1 feature line (3.1.0 document version)"]
    if any(not path_name.startswith("/api/v1/") and path_name != "/api/v1/tasks" for path_name in spec.get("paths", {})):
        return ["all public paths must be under /api/v1"]
    return _lint_catalog(spec)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="authored OpenAPI entry document")
    args = parser.parse_args(argv)
    try:
        errors = validate_contract(args.path)
    except Exception as exc:  # noqa: BLE001 - CLI must report validation failure cleanly
        print(f"OpenAPI validation failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"OpenAPI contract OK: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
