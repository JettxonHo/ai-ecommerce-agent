"""FastAPI Task and primary-input routes for the first Fast Lane vertical."""

# Decorated route callables are registered by FastAPI rather than called here.
# pyright: reportUnusedFunction=false

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, FastAPI, Header, Path, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

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
    GetTask,
    ListTasks,
    TaskManagementApplication,
    TaskManagementError,
    TaskSnapshot,
)
from ai_ecommerce_agent.shared_kernel import TaskId

from .problems import (
    idempotency_conflict_problem,
    payload_too_large_problem,
    safe_problem_response,
)

_NOT_FOUND = "urn:ai-ecommerce-agent:problem:not-found"
_VALIDATION_FAILED = "urn:ai-ecommerce-agent:problem:validation-failed"
_REVISION_CONFLICT = "urn:ai-ecommerce-agent:problem:revision-conflict"
_SERVICE_UNAVAILABLE = "urn:ai-ecommerce-agent:problem:service-unavailable"


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


def _overview(task: TaskSnapshot) -> dict[str, Any]:
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
        "needsInputRequest": None,
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
        return JSONResponse(_overview(task))


__all__ = ("register_task_routes",)
