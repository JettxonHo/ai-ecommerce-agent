"""FastAPI Task and primary-input routes for the first Fast Lane vertical."""

# Decorated route callables are registered by FastAPI rather than called here.
# pyright: reportUnusedFunction=false

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any, Literal, Protocol
from urllib.parse import quote

from fastapi import APIRouter, FastAPI, Header, Path, Query, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field

from ai_ecommerce_agent.modules.export_delivery.public import (
    ConfirmExportRequest,
    ExportBasis,
    ExportBriefKind,
)
from ai_ecommerce_agent.modules.needs_input.public import NeedsInputApplicationError
from ai_ecommerce_agent.modules.source_evidence.public import (
    PRIMARY_INPUT_MAX_BYTES,
    GetPrimaryInput,
    PrimaryInputApplication,
    PrimaryInputError,
    PrimaryInputKind,
    PrimaryInputNotFound,
    PrimaryInputSnapshot,
    SavePrimaryInput,
    validate_primary_content,
    validate_primary_file_name,
)
from ai_ecommerce_agent.modules.task_management.public import (
    CreateDraftTask,
    DomainVersionReference,
    GetTask,
    ListTasks,
    TaskManagementApplication,
    TaskManagementError,
    TaskSnapshot,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ExportSnapshotId,
    Revision,
    TaskId,
    VersionNumber,
)

from .problems import (
    idempotency_conflict_problem,
    payload_too_large_problem,
    safe_problem_response,
)

_NOT_FOUND = "urn:ai-ecommerce-agent:problem:not-found"
_VALIDATION_FAILED = "urn:ai-ecommerce-agent:problem:validation-failed"
_REVISION_CONFLICT = "urn:ai-ecommerce-agent:problem:revision-conflict"
_SERVICE_UNAVAILABLE = "urn:ai-ecommerce-agent:problem:service-unavailable"
_IDEMPOTENCY_CONFLICT = "urn:ai-ecommerce-agent:problem:idempotency-conflict"
_CAPABILITY_CONFLICT = "urn:ai-ecommerce-agent:problem:capability-conflict"
_MARKDOWN_MEDIA_TYPE = "text/markdown; charset=utf-8"


class CreateTaskBody(BaseModel):
    """Authored request fields for creating a draft Task."""

    model_config = ConfigDict(extra="forbid")

    task_name: Annotated[str, Field(alias="taskName", min_length=1)]
    product_category: Annotated[str, Field(alias="productCategory", min_length=1)]
    promotion_goal: Annotated[str, Field(alias="promotionGoal", min_length=1)]


class PrimaryInputBody(BaseModel):
    """Authored JSON body for replacing one current primary input."""

    model_config = ConfigDict(extra="forbid")

    input_kind: Annotated[str, Field(alias="inputKind", min_length=1)]
    file_name: Annotated[str | None, Field(alias="fileName")]
    content: Annotated[str, Field(min_length=1)]


class GenerateResultBody(BaseModel):
    """Authored body for one deterministic current-result generation."""

    model_config = ConfigDict(extra="forbid")

    expected_input_revision: Annotated[int, Field(alias="expectedInputRevision", ge=0)]


class ConfirmCurrentResultBody(BaseModel):
    """The two bounded corrections accepted by the Fast Lane review gate."""

    model_config = ConfigDict(extra="forbid")

    expected_result_revision: Annotated[
        int, Field(alias="expectedResultRevision", ge=0)
    ]
    marketing_core_message: Annotated[
        str, Field(alias="marketingCoreMessage", min_length=1)
    ]
    xiaohongshu_title_direction: Annotated[
        str, Field(alias="xiaohongshuTitleDirection", min_length=1)
    ]


class ExportPreviewBody(BaseModel):
    """Brief family requested for a side-effect-free export preview."""

    model_config = ConfigDict(extra="forbid")

    brief_kind: Literal["marketing", "xiaohongshu"] = Field(alias="briefKind")


class DomainVersionReferenceBody(BaseModel):
    """Wire representation of one immutable domain version reference."""

    model_config = ConfigDict(extra="forbid")

    resource_kind: Annotated[str, Field(alias="resourceKind", min_length=1)]
    resource_version_id: Annotated[str, Field(alias="resourceVersionId", min_length=1)]
    version_number: Annotated[int, Field(alias="versionNumber", ge=1)]


class ExportBasisBody(BaseModel):
    """Exact immutable basis copied from the preview response."""

    model_config = ConfigDict(extra="forbid")

    task_id: Annotated[str, Field(alias="taskId", min_length=1)]
    task_revision: Annotated[int, Field(alias="taskRevision", ge=0)]
    brief_kind: Literal["marketing", "xiaohongshu"] = Field(alias="briefKind")
    brief_version: DomainVersionReferenceBody = Field(alias="briefVersion")
    upstream_versions: list[DomainVersionReferenceBody] = Field(
        alias="upstreamVersions"
    )
    hypotheses: list[str]
    evidence_limitations: list[str] = Field(alias="evidenceLimitations")
    risks: list[str]


class ConfirmExportBody(BaseModel):
    """Explicit confirmation of one previously previewed export basis."""

    model_config = ConfigDict(extra="forbid")

    basis: ExportBasisBody


class ResultPipelineCoordinator(Protocol):
    """Narrow request-time seam injected by the composition root."""

    def generate(self, *, input_text: str) -> Any: ...


def _timestamp(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _summary(task: TaskSnapshot) -> dict[str, Any]:
    return {
        "taskId": str(task.task_id),
        "taskName": task.task_name,
        "productCategory": task.product_category,
        "taskStatus": task.task_status.value,
        "currentStage": task.current_stage.value if task.current_stage else None,
        "waitingReason": task.waiting_reason,
        "updatedAt": _timestamp(task.updated_at),
        "revision": task.revision.value,
        "primaryAction": {"type": "none"},
        "capabilities": [],
    }


def _overview(
    task: TaskSnapshot, needs_input_request: Any | None = None
) -> dict[str, Any]:
    return {
        **_summary(task),
        "stages": [],
        "activeRun": (
            {"runId": str(task.active_run_id)}
            if task.active_run_id is not None
            else None
        ),
        "latestRun": (
            {"runId": str(task.latest_run_id)}
            if task.latest_run_id is not None
            else None
        ),
        "needsInputRequest": (
            {
                "resourceKind": "needs_input",
                "resourceId": needs_input_request.action_request_id,
                "revision": needs_input_request.revision.value,
            }
            if needs_input_request is not None
            else None
        ),
        "reviewPackage": None,
        "approvedStrategy": None,
        "marketingBrief": None,
        "xiaohongshuBrief": None,
    }


def _input_projection(value: PrimaryInputSnapshot) -> dict[str, Any]:
    return {
        "taskId": str(value.task_id),
        "inputRevision": value.revision.value,
        "inputKind": value.input_kind.value,
        "fileName": value.file_name,
        "content": value.content,
        "byteCount": value.byte_count,
        "updatedAt": _timestamp(value.updated_at),
    }


def _task_problem(request: Request, error: TaskManagementError) -> JSONResponse:
    if error.error_code == "not_found":
        return safe_problem_response(
            request=request,
            problem_type=_NOT_FOUND,
            title="Not found",
            status=404,
            detail="The requested Task was not found.",
            action="none",
        )
    status = 503 if error.retryability else 422
    return safe_problem_response(
        request=request,
        problem_type=_SERVICE_UNAVAILABLE if status == 503 else _VALIDATION_FAILED,
        title="Service unavailable" if status == 503 else "Validation failed",
        status=status,
        detail=(
            "The Task service is temporarily unavailable."
            if status == 503
            else "The Task request could not be completed."
        ),
        action="retry_later" if status == 503 else "correct_input",
    )


def _input_problem(request: Request, error: PrimaryInputError) -> JSONResponse:
    if isinstance(error, PrimaryInputNotFound) or error.error_code == "not_found":
        return safe_problem_response(
            request=request,
            problem_type=_NOT_FOUND,
            title="Not found",
            status=404,
            detail="The requested primary input was not found.",
            action="none",
        )
    if error.error_code == "revision_conflict":
        return safe_problem_response(
            request=request,
            problem_type=_REVISION_CONFLICT,
            title="Revision conflict",
            status=409,
            detail="The primary input changed; refresh before retrying.",
            action="refresh",
        )
    status = 503 if error.retryability else 422
    return safe_problem_response(
        request=request,
        problem_type=_SERVICE_UNAVAILABLE if status == 503 else _VALIDATION_FAILED,
        title="Service unavailable" if status == 503 else "Validation failed",
        status=status,
        detail=(
            "The primary input service is temporarily unavailable."
            if status == 503
            else "The primary input is invalid."
        ),
        action="retry_later" if status == 503 else "correct_input",
    )


def _result_problem(request: Request, error: Exception) -> JSONResponse:
    code = getattr(error, "error_code", None)
    if code == "not_found":
        return safe_problem_response(
            request=request,
            problem_type=_NOT_FOUND,
            title="Not found",
            status=404,
            detail="The requested Task or primary input was not found.",
            action="none",
        )
    if code == "revision_conflict":
        return safe_problem_response(
            request=request,
            problem_type=_REVISION_CONFLICT,
            title="Revision conflict",
            status=409,
            detail="The primary input changed; refresh before retrying.",
            action="refresh",
        )
    if code == "idempotency_conflict":
        return safe_problem_response(
            request=request,
            problem_type=_IDEMPOTENCY_CONFLICT,
            title="Idempotency conflict",
            status=409,
            detail="The retry key belongs to another result request.",
            action="correct_input",
        )
    if code == "generation_failed":
        return safe_problem_response(
            request=request,
            problem_type="urn:ai-ecommerce-agent:problem:internal-error",
            title="Internal error",
            status=500,
            detail="The deterministic result could not be generated.",
            action="contact_operator",
        )
    retryable = bool(getattr(error, "retryability", False))
    return safe_problem_response(
        request=request,
        problem_type=_SERVICE_UNAVAILABLE if retryable else _VALIDATION_FAILED,
        title="Service unavailable" if retryable else "Validation failed",
        status=503 if retryable else 422,
        detail=(
            "The result service is temporarily unavailable."
            if retryable
            else "The result request is invalid."
        ),
        action="retry_later" if retryable else "correct_input",
    )


def _result_projection(value: Any) -> dict[str, Any]:
    return {
        "taskId": str(value.task_id),
        "resultRevision": value.result_revision,
        "inputRevision": value.input_revision,
        "status": value.status,
        "generatedAt": _timestamp(value.generated_at),
        "missingInformation": list(value.missing_information),
        "productIntake": value.candidates.get("productIntake"),
        "customerInsight": value.candidates.get("customerInsight"),
        "productPositioning": value.candidates.get("productPositioning"),
        "marketingBrief": value.candidates.get("marketingBrief"),
        "xiaohongshuBrief": value.candidates.get("xiaohongshuBrief"),
        "confirmation": getattr(value, "confirmation", None),
    }


def _version_projection(value: Any) -> dict[str, Any]:
    return {
        "resourceKind": getattr(value, "resource_kind", "domain_version"),
        "resourceVersionId": value.version_id.value,
        "versionNumber": value.version_number.value,
    }


def _export_basis_projection(value: Any) -> dict[str, Any]:
    return {
        "taskId": str(value.task_id),
        "taskRevision": value.task_revision.value,
        "briefKind": value.brief_kind.value,
        "briefVersion": {
            "resourceKind": f"{value.brief_kind.value}_brief",
            "resourceVersionId": value.brief_version.version_id.value,
            "versionNumber": value.brief_version.version_number.value,
        },
        "upstreamVersions": [
            _version_projection(item) for item in value.upstream_versions
        ],
        "hypotheses": list(value.hypotheses),
        "evidenceLimitations": list(value.evidence_limitations),
        "risks": list(value.risks),
    }


def _export_preview_projection(value: Any) -> dict[str, Any]:
    return {
        "basis": _export_basis_projection(value.basis),
        "templateVersion": value.template_version,
        "fileName": value.file_name,
        "mediaType": value.media_type,
    }


def _export_snapshot_projection(value: Any) -> dict[str, Any]:
    return {
        "exportSnapshotId": str(value.export_snapshot_id),
        "taskId": str(value.task_id),
        "briefKind": value.brief_kind.value,
        "briefVersion": {
            "resourceKind": f"{value.brief_kind.value}_brief",
            "resourceVersionId": value.brief_version.version_id.value,
            "versionNumber": value.brief_version.version_number.value,
        },
        "upstreamVersions": [
            _version_projection(item) for item in value.upstream_versions
        ],
        "exportedAt": _timestamp(value.exported_at),
        "fileName": value.file_name,
        "mediaType": value.media_type,
        "contentLocation": value.content_location,
        "templateVersion": value.template_version,
    }


def _export_basis(value: ExportBasisBody) -> ExportBasis:
    def reference(item: DomainVersionReferenceBody) -> DomainVersionReference:
        return DomainVersionReference(
            DomainVersionId(item.resource_version_id),
            VersionNumber(item.version_number),
        )

    try:
        task_id = TaskId(value.task_id)
        brief_kind = ExportBriefKind(value.brief_kind)
        expected_kind = f"{brief_kind.value}_brief"
        if value.brief_version.resource_kind != expected_kind:
            raise ValueError("brief version resource kind is invalid")
        if any(
            item.resource_kind != "domain_version" for item in value.upstream_versions
        ):
            raise ValueError("upstream version resource kind is invalid")
        return ExportBasis(
            task_id=task_id,
            task_revision=Revision(value.task_revision),
            brief_kind=brief_kind,
            brief_version=reference(value.brief_version),
            upstream_versions=tuple(
                reference(item) for item in value.upstream_versions
            ),
            hypotheses=tuple(value.hypotheses),
            evidence_limitations=tuple(value.evidence_limitations),
            risks=tuple(value.risks),
        )
    except (TypeError, ValueError) as error:
        raise ValueError("The export basis is invalid") from error


def _export_problem(request: Request, error: Exception) -> JSONResponse:
    code = getattr(error, "error_code", None)
    if code == "not_found":
        return safe_problem_response(
            request=request,
            problem_type=_NOT_FOUND,
            title="Not found",
            status=404,
            detail="The requested export resource was not found.",
            action="none",
        )
    if code == "revision_conflict":
        return safe_problem_response(
            request=request,
            problem_type=_REVISION_CONFLICT,
            title="Revision conflict",
            status=409,
            detail="The current Brief changed; refresh the export preview.",
            action="refresh",
        )
    if code == "idempotency_conflict":
        return safe_problem_response(
            request=request,
            problem_type=_IDEMPOTENCY_CONFLICT,
            title="Idempotency conflict",
            status=409,
            detail="The retry key belongs to another export basis.",
            action="correct_input",
        )
    if code == "capability_conflict":
        return safe_problem_response(
            request=request,
            problem_type="urn:ai-ecommerce-agent:problem:capability-conflict",
            title="Capability conflict",
            status=409,
            detail="The current result cannot be exported in its current state.",
            action="refresh",
        )
    retryable = bool(getattr(error, "retryability", False))
    return safe_problem_response(
        request=request,
        problem_type=_SERVICE_UNAVAILABLE if retryable else _VALIDATION_FAILED,
        title="Service unavailable" if retryable else "Validation failed",
        status=503 if retryable else 422,
        detail=(
            "The export service is temporarily unavailable."
            if retryable
            else "The export request is invalid."
        ),
        action="retry_later" if retryable else "correct_input",
    )


def _bounded_review_text(value: str) -> str:
    """Trim outer whitespace and enforce the 4 KiB encoded-text boundary."""

    normalized = value.strip()
    if not normalized:
        raise ValueError("review correction must be nonblank")
    if len(normalized.encode("utf-8")) > 4096:
        raise OverflowError("review correction is too large")
    return normalized


def _result_location(task_id: TaskId) -> str:
    """Keep an opaque Task identity in one encoded URL path segment."""

    return f"/api/v1/tasks/{quote(str(task_id), safe='')}/current-result"


def _normalize_task_body(body: CreateTaskBody) -> tuple[str, str, str]:
    values = (body.task_name, body.product_category, body.promotion_goal)
    normalized = tuple(value.strip() for value in values)
    if any(not value for value in normalized):
        raise ValueError("Task fields must be nonblank")
    return normalized[0], normalized[1], normalized[2]


def _invalid_task_id_problem(request: Request) -> JSONResponse:
    return safe_problem_response(
        request=request,
        problem_type=_VALIDATION_FAILED,
        title="Validation failed",
        status=422,
        detail="The Task request could not be completed.",
        action="correct_input",
    )


def _parse_primary_input(
    body: PrimaryInputBody,
) -> tuple[PrimaryInputKind, str | None, str]:
    try:
        input_kind = PrimaryInputKind(body.input_kind)
    except ValueError as error:
        raise ValueError("input kind is unsupported") from error
    if body.file_name is not None and body.file_name != body.file_name.strip():
        raise ValueError("filename is invalid")
    validate_primary_file_name(input_kind, body.file_name)
    normalized_candidate = body.content.replace("\r\n", "\n").replace("\r", "\n")
    try:
        candidate_byte_count = len(normalized_candidate.encode("utf-8"))
    except UnicodeEncodeError as error:
        raise ValueError("content must be valid UTF-8 text") from error
    if candidate_byte_count > PRIMARY_INPUT_MAX_BYTES:
        raise OverflowError("primary input is too large")
    content, _ = validate_primary_content(body.content)
    return input_kind, body.file_name, content


def register_task_routes(
    router: APIRouter | FastAPI,
    *,
    task_application: TaskManagementApplication,
    primary_input_application: PrimaryInputApplication,
    result_application: Any | None = None,
    pipeline_coordinator: ResultPipelineCoordinator | None = None,
    export_application: Any | None = None,
    needs_input_application: Any | None = None,
) -> None:
    """Register only the Task/input operations consumed by the Fast Lane Web UI."""

    @router.post("/api/v1/tasks", status_code=201)
    def create_task(
        request: Request,
        body: CreateTaskBody,
        idempotency_key: Annotated[
            str, Header(alias="Idempotency-Key", min_length=1, max_length=200)
        ],
    ) -> JSONResponse:
        try:
            values = _normalize_task_body(body)
        except ValueError:
            return safe_problem_response(
                request=request,
                problem_type=_VALIDATION_FAILED,
                title="Validation failed",
                status=422,
                detail="The Task request could not be completed.",
                action="correct_input",
            )
        if not idempotency_key.strip():
            return safe_problem_response(
                request=request,
                problem_type=_VALIDATION_FAILED,
                title="Validation failed",
                status=422,
                detail="The Task request could not be completed.",
                action="correct_input",
            )
        try:
            task, replayed = task_application.create_draft_task_idempotent(
                CreateDraftTask(
                    task_id=TaskId.new(),
                    task_name=values[0],
                    product_category=values[1],
                    promotion_goal=values[2],
                    updated_at=datetime.now(UTC),
                    idempotency_key=idempotency_key.strip(),
                )
            )
        except TaskManagementError as error:
            if error.error_code == "idempotency_conflict":
                return idempotency_conflict_problem(request)
            return _task_problem(request, error)
        return JSONResponse(
            _overview(task),
            status_code=200 if replayed else 201,
            headers=(
                {"Location": f"/api/v1/tasks/{task.task_id}"} if not replayed else None
            ),
        )

    @router.get("/api/v1/tasks")
    def list_tasks(
        request: Request,
        limit: Annotated[int, Query(ge=1, le=50)] = 20,
    ) -> JSONResponse:
        try:
            tasks = task_application.list_tasks(ListTasks(limit=limit))
        except TaskManagementError as error:
            return _task_problem(request, error)
        return JSONResponse(
            {"items": [_summary(task) for task in tasks], "limit": limit}
        )

    @router.get("/api/v1/tasks/{taskId:path}/primary-input")
    def get_primary_input(
        request: Request,
        task_id: Annotated[str, Path(alias="taskId", min_length=1)],
    ) -> JSONResponse:
        try:
            task_id_value = TaskId(task_id)
            task_application.get_task(GetTask(task_id_value))
            value = primary_input_application.get_primary_input(
                GetPrimaryInput(task_id_value)
            )
        except (TypeError, ValueError):
            return _invalid_task_id_problem(request)
        except TaskManagementError as error:
            return _task_problem(request, error)
        except PrimaryInputError as error:
            return _input_problem(request, error)
        return JSONResponse(_input_projection(value))

    @router.put("/api/v1/tasks/{taskId:path}/primary-input")
    def put_primary_input(
        request: Request,
        body: PrimaryInputBody,
        task_id: Annotated[str, Path(alias="taskId", min_length=1)],
    ) -> JSONResponse:
        try:
            task_id_value = TaskId(task_id)
            task_application.get_task(GetTask(task_id_value))
            try:
                input_kind, file_name, content = _parse_primary_input(body)
            except OverflowError:
                return payload_too_large_problem(request)
            except (TypeError, ValueError):
                return safe_problem_response(
                    request=request,
                    problem_type=_VALIDATION_FAILED,
                    title="Validation failed",
                    status=422,
                    detail="The primary input is invalid.",
                    action="correct_input",
                )
            value = primary_input_application.save_primary_input(
                SavePrimaryInput(
                    task_id=task_id_value,
                    input_kind=input_kind,
                    file_name=file_name,
                    content=content,
                    updated_at=datetime.now(UTC),
                )
            )
        except (TypeError, ValueError):
            return _invalid_task_id_problem(request)
        except TaskManagementError as error:
            return _task_problem(request, error)
        except PrimaryInputError as error:
            return _input_problem(request, error)
        return JSONResponse(_input_projection(value))

    if result_application is not None:
        if pipeline_coordinator is None:
            raise ValueError(
                "pipeline_coordinator is required when result routes are enabled"
            )
        coordinator = pipeline_coordinator

        @router.post(
            "/api/v1/tasks/{taskId:path}/commands/generate-result",
            status_code=201,
        )
        def generate_result(
            request: Request,
            body: GenerateResultBody,
            task_id: Annotated[str, Path(alias="taskId", min_length=1)],
            idempotency_key: Annotated[
                str, Header(alias="Idempotency-Key", min_length=1, max_length=200)
            ],
        ) -> JSONResponse:
            try:
                task_id_value = TaskId(task_id)
                if not idempotency_key.strip():
                    return safe_problem_response(
                        request=request,
                        problem_type=_VALIDATION_FAILED,
                        title="Validation failed",
                        status=422,
                        detail="The result request is invalid.",
                        action="correct_input",
                    )
                value, replayed = result_application.generate_result(
                    task_id=task_id_value,
                    idempotency_key=idempotency_key.strip(),
                    expected_input_revision=body.expected_input_revision,
                    coordinator=coordinator,
                )
            except (TypeError, ValueError):
                return _invalid_task_id_problem(request)
            except Exception as error:
                return _result_problem(request, error)
            return JSONResponse(
                _result_projection(value),
                status_code=200 if replayed else 201,
                headers=(
                    {"Location": _result_location(task_id_value)}
                    if not replayed
                    else None
                ),
            )

        @router.get("/api/v1/tasks/{taskId:path}/current-result")
        def get_current_result(
            request: Request,
            task_id: Annotated[str, Path(alias="taskId", min_length=1)],
        ) -> JSONResponse:
            try:
                task_id_value = TaskId(task_id)
                value = result_application.get_current_result(task_id=task_id_value)
            except (TypeError, ValueError):
                return _invalid_task_id_problem(request)
            except Exception as error:
                return _result_problem(request, error)
            if value is None:
                return safe_problem_response(
                    request=request,
                    problem_type=_NOT_FOUND,
                    title="Not found",
                    status=404,
                    detail="The current result was not found.",
                    action="none",
                )
            return JSONResponse(_result_projection(value))

        @router.post(
            "/api/v1/tasks/{taskId:path}/commands/confirm-current-result",
            status_code=201,
        )
        def confirm_current_result(
            request: Request,
            body: ConfirmCurrentResultBody,
            task_id: Annotated[str, Path(alias="taskId", min_length=1)],
            idempotency_key: Annotated[
                str, Header(alias="Idempotency-Key", min_length=1, max_length=200)
            ],
        ) -> JSONResponse:
            try:
                task_id_value = TaskId(task_id)
                key = idempotency_key.strip()
                if not key:
                    raise ValueError("idempotency key is blank")
                marketing_message = _bounded_review_text(body.marketing_core_message)
                title_direction = _bounded_review_text(body.xiaohongshu_title_direction)
                value, replayed = result_application.confirm_current_result(
                    task_id=task_id_value,
                    idempotency_key=key,
                    expected_result_revision=body.expected_result_revision,
                    marketing_core_message=marketing_message,
                    xiaohongshu_title_direction=title_direction,
                )
            except OverflowError:
                return payload_too_large_problem(request)
            except (TypeError, ValueError):
                return safe_problem_response(
                    request=request,
                    problem_type=_VALIDATION_FAILED,
                    title="Validation failed",
                    status=422,
                    detail="The review corrections are invalid.",
                    action="correct_input",
                )
            except Exception as error:
                return _result_problem(request, error)
            return JSONResponse(
                _result_projection(value), status_code=200 if replayed else 201
            )

    if export_application is not None:

        @router.post("/api/v1/tasks/{taskId:path}/export-previews")
        def preview_export(
            request: Request,
            body: ExportPreviewBody,
            task_id: Annotated[str, Path(alias="taskId", min_length=1)],
        ) -> JSONResponse:
            try:
                value = export_application.preview_export(
                    task_id=TaskId(task_id), brief_kind=ExportBriefKind(body.brief_kind)
                )
            except (TypeError, ValueError):
                return _invalid_task_id_problem(request)
            except Exception as error:
                return _export_problem(request, error)
            return JSONResponse(_export_preview_projection(value))

        @router.post("/api/v1/export-snapshots", status_code=201)
        def create_export_snapshot(
            request: Request,
            body: ConfirmExportBody,
            idempotency_key: Annotated[
                str, Header(alias="Idempotency-Key", min_length=1, max_length=200)
            ],
        ) -> JSONResponse:
            try:
                key = idempotency_key.strip()
                if not key:
                    raise ValueError("idempotency key is blank")
                basis = _export_basis(body.basis)
                value, replayed = export_application.create_export_snapshot(
                    idempotency_key=key, request=ConfirmExportRequest(basis=basis)
                )
            except (TypeError, ValueError):
                return safe_problem_response(
                    request=request,
                    problem_type=_VALIDATION_FAILED,
                    title="Validation failed",
                    status=422,
                    detail="The export basis is invalid.",
                    action="correct_input",
                )
            except Exception as error:
                return _export_problem(request, error)
            return JSONResponse(
                _export_snapshot_projection(value),
                status_code=200 if replayed else 201,
                headers=(
                    {"Location": value.content_location} if not replayed else None
                ),
            )

        @router.get("/api/v1/export-snapshots/{exportSnapshotId}/content")
        def download_export_snapshot_content(
            request: Request,
            export_snapshot_id: Annotated[
                str, Path(alias="exportSnapshotId", min_length=1)
            ],
        ) -> Response:
            try:
                value, content = export_application.get_export_content(
                    export_snapshot_id=ExportSnapshotId(export_snapshot_id)
                )
            except (TypeError, ValueError):
                return _invalid_task_id_problem(request)
            except Exception as error:
                problem = _export_problem(request, error)
                return Response(
                    content=problem.body,
                    status_code=problem.status_code,
                    headers=dict(problem.headers),
                    media_type=problem.media_type,
                )
            return Response(
                content=content.encode("utf-8"),
                media_type="text/markdown",
                headers={
                    "Content-Type": _MARKDOWN_MEDIA_TYPE,
                    "Content-Disposition": f'attachment; filename="{value.file_name}"',
                },
            )

    @router.get("/api/v1/tasks/{taskId:path}")
    def get_task(
        request: Request,
        task_id: Annotated[str, Path(alias="taskId", min_length=1)],
    ) -> JSONResponse:
        try:
            task_id_value = TaskId(task_id)
        except (TypeError, ValueError):
            return _invalid_task_id_problem(request)
        try:
            task = task_application.get_task(GetTask(task_id_value))
        except TaskManagementError as error:
            return _task_problem(request, error)
        current_needs_input = None
        if needs_input_application is not None:
            try:
                current_needs_input = needs_input_application.get_current_request(
                    task_id_value
                )
            except NeedsInputApplicationError as error:
                status = 503 if error.retryability else 422
                return safe_problem_response(
                    request=request,
                    problem_type=(
                        _SERVICE_UNAVAILABLE if status == 503 else _VALIDATION_FAILED
                    ),
                    title=(
                        "Service unavailable" if status == 503 else "Validation failed"
                    ),
                    status=status,
                    detail=(
                        "The Needs Input service is temporarily unavailable."
                        if status == 503
                        else "The Task overview could not be completed."
                    ),
                    action="retry_later" if status == 503 else "refresh",
                )
        return JSONResponse(_overview(task, current_needs_input))


__all__ = ("register_task_routes",)
