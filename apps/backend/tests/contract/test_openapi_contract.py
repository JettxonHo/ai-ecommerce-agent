"""Representative checks for the authored RFC-004 OpenAPI contract.

These tests intentionally verify the public description, not an HTTP handler.
The backend package has no API runtime yet; future conformance tests must
consume this same entry document rather than creating a second DTO contract.
"""

from __future__ import annotations

import copy
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

import pytest
import yaml

pytestmark = pytest.mark.contract

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
CONTRACT = REPOSITORY_ROOT / "contracts" / "openapi" / "openapi.yaml"
VALIDATOR = REPOSITORY_ROOT / "contracts" / "openapi" / "tools" / "validate.py"
DIFF_TOOL = REPOSITORY_ROOT / "contracts" / "openapi" / "tools" / "diff.py"


def _load_contract() -> dict[str, Any]:
    with CONTRACT.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    assert isinstance(value, dict)
    return cast(dict[str, Any], value)


def _operations(spec: dict[str, Any]) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    paths = cast(dict[str, Any], spec["paths"])
    for path_item in paths.values():
        assert isinstance(path_item, dict)
        typed_path_item = cast(dict[str, Any], path_item)
        for method, operation in typed_path_item.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            assert isinstance(operation, dict)
            operations.append(cast(dict[str, Any], operation))
    return operations


def test_authored_document_passes_oas_and_catalog_validation() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(CONTRACT)],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_operation_ids_are_unique_and_catalog_is_bounded() -> None:
    spec = _load_contract()
    operation_ids = [operation["operationId"] for operation in _operations(spec)]
    assert len(operation_ids) == 36
    assert len(operation_ids) == len(set(operation_ids))
    assert all(path.startswith("/api/v1/") for path in spec["paths"])
    assert "/api/v1/tasks" in spec["paths"]


def test_fixed_workspace_and_origin_boundary_are_not_client_selectable() -> None:
    spec = _load_contract()
    serialized = str(spec)
    assert "workspaceId" not in serialized
    assert "X-Workspace-Id" not in serialized
    assert "Authorization" not in serialized
    assert spec["servers"] == [
        {"url": "/", "description": "Server-bound loopback same-origin workbench"}
    ]


def test_idempotency_and_semantic_revision_are_explicit() -> None:
    spec = _load_contract()
    idempotent_operations = {
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
    for operation in _operations(spec):
        operation_id = operation["operationId"]
        if operation_id not in idempotent_operations:
            continue
        parameters = operation.get("parameters", [])
        assert isinstance(parameters, list)
        parameters = cast(list[Any], parameters)
        references = {
            cast(dict[str, Any], parameter).get("$ref")
            for parameter in parameters
            if isinstance(parameter, dict)
        }
        assert references >= {"#/components/parameters/IdempotencyKey"}
    schemas = spec["components"]["schemas"]
    assert "revision" in schemas["TaskSummary"]["properties"]
    assert "revision" in schemas["ReviewDraft"]["properties"]
    assert schemas["CommandReceipt"]["required"] == [
        "commandId",
        "commandType",
        "taskId",
        "acceptedAt",
        "monitor",
        "resultReference",
    ]


def test_async_receipts_and_run_monitor_states_preserve_accepted_semantics() -> None:
    spec = _load_contract()
    async_operations = {
        "startTask",
        "rerunTask",
        "cancelRun",
        "resumeRun",
        "retryCurrentStage",
        "restartFromSafeBoundary",
        "rejectAllAndRequestRegeneration",
    }
    for operation in _operations(spec):
        if operation["operationId"] not in async_operations:
            continue
        assert {"202", "200"} <= set(operation["responses"])
        assert operation["responses"]["202"]["content"]["application/json"]["schema"][
            "$ref"
        ] == ("#/components/schemas/CommandReceipt")
    assert spec["components"]["schemas"]["RunStatus"]["enum"] == [
        "queued",
        "running",
        "retrying",
        "waiting_for_input",
        "waiting_for_review",
        "paused",
        "cancellation_requested",
        "completed",
        "failed",
        "cancelled",
        "superseded",
    ]


def test_needs_input_review_brief_export_and_problem_projection_are_typed() -> None:
    schemas = _load_contract()["components"]["schemas"]
    assert schemas["NeedsInputActionRequest"]["required"] == [
        "actionRequestId",
        "taskId",
        "revision",
        "status",
        "reasonType",
        "reasonSummary",
        "affectedStages",
        "sourceReferences",
        "conflictValues",
        "allowedResolutionTypes",
        "expectedRecovery",
        "supersededBy",
    ]
    assert "expectedDraftRevision" in schemas["SubmitReviewRequest"]["required"]
    assert (
        "semanticGroups" in schemas["MarketingBriefVersion"]["allOf"][0]["$ref"]
        or "semanticGroups" in schemas["BriefVersion"]["properties"]
    )
    assert "basis" in schemas["ConfirmExportRequest"]["required"]
    assert (
        schemas["ExportSnapshot"]["properties"]["mediaType"]["const"]
        == "text/markdown; charset=utf-8"
    )
    assert (
        schemas["ProblemDetails"]["properties"]["action"]["$ref"]
        == "#/components/schemas/ProblemAction"
    )
    assert schemas["ProblemType"]["enum"] == [
        "urn:ai-ecommerce-agent:problem:malformed-request",
        "urn:ai-ecommerce-agent:problem:not-found",
        "urn:ai-ecommerce-agent:problem:payload-too-large",
        "urn:ai-ecommerce-agent:problem:unsupported-media-type",
        "urn:ai-ecommerce-agent:problem:validation-failed",
        "urn:ai-ecommerce-agent:problem:revision-conflict",
        "urn:ai-ecommerce-agent:problem:idempotency-conflict",
        "urn:ai-ecommerce-agent:problem:superseded-resource",
        "urn:ai-ecommerce-agent:problem:capability-conflict",
        "urn:ai-ecommerce-agent:problem:operation-in-progress",
        "urn:ai-ecommerce-agent:problem:rate-limited",
        "urn:ai-ecommerce-agent:problem:internal-error",
        "urn:ai-ecommerce-agent:problem:service-unavailable",
    ]


def test_representative_schema_examples_cover_required_wire_fields() -> None:
    schemas = _load_contract()["components"]["schemas"]
    for schema_name in (
        "CommandReceipt",
        "Run",
        "ReviewDraft",
        "BriefVersion",
        "ExportSnapshot",
        "ProblemDetails",
    ):
        schema = schemas[schema_name]
        example = schema.get("example")
        assert isinstance(example, dict), schema_name
        required = cast(list[str], schema["required"])
        example = cast(dict[str, Any], example)
        assert set(required) <= set(example), schema_name
    assert len(schemas["BriefVersion"]["example"]["semanticGroups"]) == 6
    assert re.fullmatch(
        r"task-[^-]+-(marketing|xiaohongshu)-v[0-9]+-[0-9]{8}T[0-9]{6}Z\.md",
        schemas["ExportSnapshot"]["example"]["fileName"],
    )


def test_mutable_review_brief_and_export_commands_expose_typed_conflicts() -> None:
    operations = {
        operation["operationId"]: operation
        for operation in _operations(_load_contract())
    }
    for operation_id in (
        "putReviewDraft",
        "submitReview",
        "reviseMarketingBrief",
        "reviseXiaohongshuBrief",
        "createExportSnapshot",
    ):
        operation = operations[operation_id]
        assert "409" in operation["responses"], operation_id
        problem_response = operation["responses"]["409"]
        assert problem_response["$ref"] == "#/components/responses/Problem409"
    revise_result = _load_contract()["components"]["schemas"]["ReviseBriefResult"]
    assert "invalidatedBrief" in revise_result["required"]


def test_bounded_breaking_diff_rejects_removed_operation(tmp_path: Path) -> None:
    baseline = _load_contract()
    candidate = copy.deepcopy(baseline)
    del candidate["paths"]["/api/v1/tasks/{taskId}"]
    baseline_path = tmp_path / "baseline.yaml"
    candidate_path = tmp_path / "candidate.yaml"
    baseline_path.write_text(
        yaml.safe_dump(baseline, sort_keys=False), encoding="utf-8"
    )
    candidate_path.write_text(
        yaml.safe_dump(candidate, sort_keys=False), encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, str(DIFF_TOOL), str(baseline_path), str(candidate_path)],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "operation path removed" in result.stdout


def test_bounded_breaking_diff_allows_optional_addition(tmp_path: Path) -> None:
    baseline = _load_contract()
    candidate = copy.deepcopy(baseline)
    candidate["components"]["schemas"]["TaskSummary"]["properties"]["optionalLabel"] = {
        "type": "string"
    }
    baseline_path = tmp_path / "baseline.yaml"
    candidate_path = tmp_path / "candidate.yaml"
    baseline_path.write_text(
        yaml.safe_dump(baseline, sort_keys=False), encoding="utf-8"
    )
    candidate_path.write_text(
        yaml.safe_dump(candidate, sort_keys=False), encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, str(DIFF_TOOL), str(baseline_path), str(candidate_path)],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
