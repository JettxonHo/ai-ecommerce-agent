"""Safe RFC 9457 projections owned by the HTTP adapter."""

from collections.abc import Mapping, Sequence
from typing import Any, cast

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

_MALFORMED_REQUEST = "urn:ai-ecommerce-agent:problem:malformed-request"
_NOT_FOUND = "urn:ai-ecommerce-agent:problem:not-found"
_VALIDATION_FAILED = "urn:ai-ecommerce-agent:problem:validation-failed"
_INTERNAL_ERROR = "urn:ai-ecommerce-agent:problem:internal-error"
_PROBLEM_MEDIA_TYPE = "application/problem+json"


def _problem_response(
    *,
    request: Request,
    problem_type: str,
    title: str,
    status: int,
    detail: str,
    action: str,
    field_issues: Sequence[Mapping[str, str]] | None = None,
) -> JSONResponse:
    payload: dict[str, Any] = {
        "type": problem_type,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
        "action": action,
    }
    if field_issues is not None:
        payload["fieldIssues"] = [dict(issue) for issue in field_issues]
    return JSONResponse(payload, status_code=status, media_type=_PROBLEM_MEDIA_TYPE)


def malformed_origin_problem(request: Request) -> JSONResponse:
    """Return the fixed safe response for a rejected write Origin."""

    return _problem_response(
        request=request,
        problem_type=_MALFORMED_REQUEST,
        title="Malformed request",
        status=400,
        detail="The request Origin is not allowed.",
        action="correct_input",
    )


def not_found_problem(request: Request, _exc: Exception) -> JSONResponse:
    """Project unknown framework routes without exposing framework detail."""

    return _problem_response(
        request=request,
        problem_type=_NOT_FOUND,
        title="Not found",
        status=404,
        detail="The requested resource was not found.",
        action="none",
    )


def _field_issue(error: Mapping[str, object]) -> dict[str, str]:
    location = error.get("loc", ())
    if not isinstance(location, (tuple, list)):
        location = ()
    path_parts: list[str] = []
    for part in cast(Sequence[object], location):
        if type(part) in (str, int):
            path_parts.append(str(part))
    field_path = ".".join(path_parts) or "request"
    reason_code = error.get("type")
    if type(reason_code) is not str or not reason_code:
        reason_code = "invalid"
    return {"fieldPath": field_path, "reasonCode": reason_code}


def request_validation_problem(request: Request, exc: Exception) -> JSONResponse:
    """Project only stable location and Pydantic error-type codes."""

    if not isinstance(exc, RequestValidationError):
        return unhandled_problem(request, exc)
    field_issues = [_field_issue(error) for error in exc.errors()]
    return _problem_response(
        request=request,
        problem_type=_VALIDATION_FAILED,
        title="Validation failed",
        status=422,
        detail="One or more request fields are invalid.",
        action="correct_input",
        field_issues=field_issues,
    )


def unhandled_problem(request: Request, _exc: Exception) -> JSONResponse:
    """Project an unhandled exception without exposing its payload or type."""

    return _problem_response(
        request=request,
        problem_type=_INTERNAL_ERROR,
        title="Internal error",
        status=500,
        detail="The server could not complete the request.",
        action="contact_operator",
    )


__all__ = (
    "malformed_origin_problem",
    "not_found_problem",
    "request_validation_problem",
    "unhandled_problem",
)
