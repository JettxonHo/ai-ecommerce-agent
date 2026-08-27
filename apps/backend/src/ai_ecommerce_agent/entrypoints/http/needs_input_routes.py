"""Transport-owned Needs Input DTOs, projections, problems and operations."""

# Decorated route callables are registered by FastAPI rather than called here.
# pyright: reportUnusedFunction=false

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastapi import APIRouter, FastAPI, Header, Path, Request
from fastapi.responses import JSONResponse
from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from ai_ecommerce_agent.modules.needs_input.public import (
    NeedsInputApplicationError,
    ResolveNeedsInput,
)
from ai_ecommerce_agent.shared_kernel import Revision

from .problems import safe_problem_response

_NOT_FOUND = "urn:ai-ecommerce-agent:problem:not-found"
_VALIDATION_FAILED = "urn:ai-ecommerce-agent:problem:validation-failed"
_REVISION_CONFLICT = "urn:ai-ecommerce-agent:problem:revision-conflict"
_SERVICE_UNAVAILABLE = "urn:ai-ecommerce-agent:problem:service-unavailable"
_IDEMPOTENCY_CONFLICT = "urn:ai-ecommerce-agent:problem:idempotency-conflict"
_CAPABILITY_CONFLICT = "urn:ai-ecommerce-agent:problem:capability-conflict"


def _validate_needs_input_notes(value: str | None) -> str | None:
    """Bound untrusted notes by UTF-8 bytes, not Python code points."""

    if value is not None and len(value.encode("utf-8")) > 4096:
        raise ValueError("notes exceed the UTF-8 byte bound")
    return value


_NeedsInputNotes = Annotated[
    str | None,
    Field(max_length=4096),
    AfterValidator(_validate_needs_input_notes),
]


class _NeedsInputResourceReferenceBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resource_kind: Annotated[str, Field(alias="resourceKind", min_length=1)]
    resource_id: Annotated[str, Field(alias="resourceId", min_length=1)]


class _NeedsInputProvideSourceReferenceBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resolution_type: Literal["provide_source_reference"] = Field(alias="resolutionType")
    source_references: Annotated[
        list[_NeedsInputResourceReferenceBody],
        Field(alias="sourceReferences", min_length=1),
    ]
    notes: _NeedsInputNotes = None


class _NeedsInputChooseExistingValueBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resolution_type: Literal["choose_existing_value"] = Field(alias="resolutionType")
    selected_value: object = Field(alias="selectedValue")
    notes: _NeedsInputNotes = None


class _NeedsInputSubmitCorrectionBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resolution_type: Literal["submit_correction"] = Field(alias="resolutionType")
    corrected_value: object = Field(alias="correctedValue")
    notes: _NeedsInputNotes = None


class _NeedsInputConfirmKnownLimitationBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resolution_type: Literal["confirm_known_limitation"] = Field(alias="resolutionType")
    notes: _NeedsInputNotes = None


class _NeedsInputCancelPathBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resolution_type: Literal["cancel_path"] = Field(alias="resolutionType")
    notes: _NeedsInputNotes = None


_NeedsInputResolutionBody = (
    _NeedsInputProvideSourceReferenceBody
    | _NeedsInputChooseExistingValueBody
    | _NeedsInputSubmitCorrectionBody
    | _NeedsInputConfirmKnownLimitationBody
    | _NeedsInputCancelPathBody
)


class _NeedsInputResolveBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_revision: Annotated[int, Field(alias="expectedRevision", ge=0)]
    resolution: _NeedsInputResolutionBody


def _needs_input_request_projection(
    value: Any, *, superseded_by_revision: int | None = None
) -> dict[str, Any]:
    superseded_by = value.superseded_by
    return {
        "actionRequestId": value.action_request_id,
        "taskId": str(value.task_id),
        "revision": value.revision.value,
        "status": value.status.value,
        "reasonType": value.reason_type,
        "reasonSummary": value.reason_summary,
        "affectedStages": list(value.affected_stages),
        "sourceReferences": [dict(item) for item in value.source_references],
        "conflictValues": [dict(item) for item in value.conflict_values],
        "allowedResolutionTypes": list(value.allowed_resolution_types),
        "expectedRecovery": value.expected_recovery.value,
        "supersededBy": (
            {
                "resourceKind": "needs_input",
                "resourceId": superseded_by,
                "revision": (
                    superseded_by_revision
                    if superseded_by_revision is not None
                    else value.revision.value
                ),
            }
            if superseded_by is not None
            else None
        ),
    }


def _needs_input_problem(
    request: Request, error: NeedsInputApplicationError
) -> JSONResponse:
    if error.error_code == "not_found":
        return safe_problem_response(
            request=request,
            problem_type=_NOT_FOUND,
            title="Not found",
            status=404,
            detail="The requested Needs Input request was not found.",
            action="none",
        )
    if error.error_code == "revision_conflict":
        return safe_problem_response(
            request=request,
            problem_type=_REVISION_CONFLICT,
            title="Revision conflict",
            status=409,
            detail="The Needs Input request changed; refresh before retrying.",
            action="refresh",
        )
    if error.error_code == "idempotency_conflict":
        return safe_problem_response(
            request=request,
            problem_type=_IDEMPOTENCY_CONFLICT,
            title="Idempotency conflict",
            status=409,
            detail="The retry key belongs to another Needs Input resolution.",
            action="correct_input",
        )
    if error.error_code in {"capability_conflict", "ownership_conflict"}:
        return safe_problem_response(
            request=request,
            problem_type=_CAPABILITY_CONFLICT,
            title="Capability conflict",
            status=409,
            detail="The Needs Input request cannot be resolved in its current state.",
            action="refresh",
        )
    return safe_problem_response(
        request=request,
        problem_type=_SERVICE_UNAVAILABLE if error.retryability else _VALIDATION_FAILED,
        title="Service unavailable" if error.retryability else "Validation failed",
        status=503 if error.retryability else 422,
        detail=(
            "The Needs Input service is temporarily unavailable."
            if error.retryability
            else "The Needs Input resolution is invalid."
        ),
        action="retry_later" if error.retryability else "correct_input",
    )


def _needs_input_resolution_payload(
    resolution: _NeedsInputResolutionBody,
) -> dict[str, object]:
    dumped = resolution.model_dump(by_alias=True, exclude_none=True)
    dumped.pop("resolutionType", None)
    return {str(key): value for key, value in dumped.items()}


def register_needs_input_routes(
    router: APIRouter | FastAPI,
    *,
    needs_input_application: Any,
) -> None:
    """Register the two authored Needs Input operations."""

    @router.get("/api/v1/needs-input-requests/{actionRequestId:path}")
    def get_needs_input_action_request(
        request: Request,
        action_request_id: Annotated[str, Path(alias="actionRequestId", min_length=1)],
    ) -> JSONResponse:
        try:
            value = needs_input_application.get_action_request(action_request_id)
        except NeedsInputApplicationError as error:
            return _needs_input_problem(request, error)
        successor_revision = None
        if value.superseded_by is not None:
            try:
                successor = needs_input_application.get_action_request(
                    value.superseded_by
                )
            except NeedsInputApplicationError as error:
                return _needs_input_problem(request, error)
            successor_revision = successor.revision.value
        return JSONResponse(
            _needs_input_request_projection(
                value, superseded_by_revision=successor_revision
            )
        )

    @router.post("/api/v1/needs-input-requests/{actionRequestId:path}/commands/resolve")
    def resolve_needs_input(
        request: Request,
        body: _NeedsInputResolveBody,
        action_request_id: Annotated[str, Path(alias="actionRequestId", min_length=1)],
        idempotency_key: Annotated[
            str, Header(alias="Idempotency-Key", min_length=1, max_length=200)
        ],
    ) -> JSONResponse:
        try:
            key = idempotency_key.strip()
            if not key:
                raise ValueError("idempotency key is blank")
            command = ResolveNeedsInput(
                action_request_id=action_request_id,
                expected_revision=Revision(body.expected_revision),
                idempotency_key=key,
                resolution_type=body.resolution.resolution_type,
                resolution_payload=_needs_input_resolution_payload(body.resolution),
            )
            value = needs_input_application.resolve_needs_input(command)
        except OverflowError:
            return safe_problem_response(
                request=request,
                problem_type=_VALIDATION_FAILED,
                title="Validation failed",
                status=422,
                detail="The Needs Input resolution is invalid.",
                action="correct_input",
            )
        except (TypeError, ValueError):
            return safe_problem_response(
                request=request,
                problem_type=_VALIDATION_FAILED,
                title="Validation failed",
                status=422,
                detail="The Needs Input resolution is invalid.",
                action="correct_input",
            )
        except NeedsInputApplicationError as error:
            return _needs_input_problem(request, error)
        return JSONResponse(
            {
                "actionRequest": _needs_input_request_projection(value.action_request),
                "task": {"taskId": str(value.task_id)},
            }
        )


__all__ = ("register_needs_input_routes",)
