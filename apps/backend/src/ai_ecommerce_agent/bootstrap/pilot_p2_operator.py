"""Repository-owned provider-free P2 operator binder.

The binder presents one small synchronous seam for a single admitted P01
attempt.  It owns the HTTP command choreography, persisted PostgreSQL
composition, outside-Git attempt evidence, runtime observation and safe
terminalization while keeping Provider and Secret access behind the existing
lazy P2 runtime seam.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol, cast

from ai_ecommerce_agent.bootstrap import pilot_p2
from ai_ecommerce_agent.bootstrap.pilot_p2 import (
    P2RuntimeObserver,
    RuntimeBuilder,
)
from ai_ecommerce_agent.entrypoints.http import FixedWorkspaceHttpConfig
from ai_ecommerce_agent.orchestration.pilot_attempt_artifact import (
    ArtifactReference,
    AttemptArtifactError,
    AttemptArtifactSnapshot,
    CaptureExport,
    ExportContentReference,
    ExportVersionReference,
    FinalDisposition,
    FinalizationCost,
    FinalizationExecution,
    FinalizationGates,
    PilotAttemptArtifacts,
    RecordReview,
    RecordRun,
    ReserveAttempt,
    ReviewDimension,
    UnknownValue,
)
from ai_ecommerce_agent.orchestration.pilot_attempt_artifact import (
    FinalizeAttempt as ArtifactFinalizeAttempt,
)
from ai_ecommerce_agent.platform.model_runtime.deepseek._cost_gate import (
    DEEPSEEK_P2_RESERVATION_MICRO_USD,
    DEEPSEEK_PRICING_RECORD,
)
from ai_ecommerce_agent.platform.postgres import PostgresEngineConfig

__all__ = [
    "ConfirmAndCapture",
    "FinalizeAttempt",
    "OperatorErrorCode",
    "PilotP2Operator",
    "PilotP2OperatorError",
    "PilotP2OperatorSnapshot",
    "StartAttempt",
    "SubmitHumanReview",
]


_SAMPLE_ID = "P01"
_ATTEMPT_ID = "P2-P01-A1"
_PRICING_RECORD_ID = DEEPSEEK_PRICING_RECORD.record_id
_MAX_CALLS = 5
_INPUT_FIELDS: tuple[tuple[str, str], ...] = (
    ("sample_id", _SAMPLE_ID),
    ("attempt_id", _ATTEMPT_ID),
    ("product", "Anker Nano Power Bank"),
    ("model/designation", "A1259"),
    ("color", "Black Stone"),
    ("variant", "42733233766550"),
    ("category", "A"),
)
_FIXTURE_MARKERS = ("anchor", "backpack", "scripted")
_EXPORT_KINDS = frozenset({"marketing", "xiaohongshu"})
_SAFE_FAILURE_CATEGORIES = frozenset(
    {
        "configuration_or_access",
        "invalid_request",
        "transient_provider_failure",
        "refusal",
        "incomplete_output",
        "invalid_candidate",
        "cancelled_or_superseded",
        "unknown_runtime_failure",
        "operator_failure",
    }
)
_SAFE_LIFECYCLE_PHASES = frozenset({"generation", "confirmation", "export"})
_SAFE_TERMINAL_STAGES = frozenset(
    {
        "generation",
        "confirmation",
        "export",
        "review",
        "finalization",
        "stage-1",
        "stage-2",
        "stage-3",
        "stage-4",
        "stage-5",
    }
)


class OperatorErrorCode(StrEnum):
    """Fixed safe operator errors; no paths or provider payloads are exposed."""

    INVALID_COMMAND = "invalid_command"
    GIT_HEAD_MISMATCH = "git_head_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    INPUT_ROOT_INVALID = "input_root_invalid"
    INPUT_PATH_INVALID = "input_path_invalid"
    INPUT_OUTSIDE_ROOT = "input_path_outside_approved_root"
    FIXTURE_INPUT_REJECTED = "fixture_input_rejected"
    ARTIFACT_ROOT_INVALID = "artifact_root_invalid"
    ARTIFACT_ROOT_EXISTS = "artifact_root_must_be_absent"
    ARTIFACT_ROOT_INSIDE_REPOSITORY = "artifact_root_inside_repository"
    OWNER_CAP_INVALID = "owner_cap_invalid"
    OWNER_CAP_UNDERFUNDED = "owner_cap_underfunded"
    PRICING_RECORD_MISMATCH = "pricing_record_mismatch"
    EXECUTION_POLICY_INVALID = "execution_policy_invalid"
    INPUT_CONTENT_INVALID = "input_content_invalid"
    POSTGRES_COMPOSITION_FAILED = "postgres_composition_failed"
    HTTP_COMMAND_FAILED = "http_command_failed"
    RUN_EVIDENCE_INVALID = "run_evidence_invalid"
    RESUME_NOT_AVAILABLE = "resume_not_available"
    REVIEW_DECISION_REQUIRED = "review_decision_required"
    REVIEW_NOT_AVAILABLE = "review_not_available"
    FINALIZATION_INVALID = "finalization_invalid"
    DURABILITY_FAILED = "durability_failed"
    CLEANUP_FAILED = "cleanup_failed"


class PilotP2OperatorError(ValueError):
    """Safe fixed error with no raw exception, prompt or private path."""

    def __init__(self, code: OperatorErrorCode | str) -> None:
        if isinstance(code, OperatorErrorCode):
            value = code.value
        elif type(code) is str and code in {item.value for item in OperatorErrorCode}:
            value = code
        else:
            raise TypeError("code must be an OperatorErrorCode")
        self.error_code = value
        self.code = value
        super().__init__(f"{value}:operator")


@dataclass(frozen=True, slots=True)
class StartAttempt:
    """Typed command for one exact P01/P2 generation attempt."""

    input_path: Path | str | None = None
    artifact_root: Path | str | None = None
    authorized_commit: str | None = None
    owner_cap_micro_usd: int | None = None
    pricing_record_id: str | None = None
    sample_id: str = _SAMPLE_ID
    attempt_id: str = _ATTEMPT_ID
    git_commit: str | None = None
    git_head: str | None = None
    max_calls: int = _MAX_CALLS
    retry_count: int = 0
    recovery_count: int = 0
    replay_count: int = 0
    fallback_count: int = 0
    manual_intervention_count: int = 0


@dataclass(frozen=True, slots=True)
class ConfirmAndCapture:
    """Typed command that resumes an awaiting result and captures exports."""

    brief_kinds: tuple[str, ...] | None = None
    marketing_core_message: str | None = None
    xiaohongshu_title_direction: str | None = None
    sample_id: str = _SAMPLE_ID
    attempt_id: str = _ATTEMPT_ID
    owner_cap_micro_usd: int | None = None
    pricing_record_id: str | None = None
    export_kinds: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        if self.export_kinds is not None:
            object.__setattr__(self, "brief_kinds", self.export_kinds)


@dataclass(frozen=True, slots=True)
class SubmitHumanReview:
    """Typed command for the explicit, immutable P0 human review."""

    overall: str | None = None
    rationale: str | None = None
    review_id: str | None = None
    captured_export_snapshot_ids: tuple[str, ...] | None = None
    reviewer_role: str | None = None
    reviewed_at: datetime | str | None = None
    dimensions: tuple[ReviewDimension, ...] | None = None
    notes: tuple[str, ...] = ()
    material_edits: tuple[str, ...] = ()
    sample_id: str = _SAMPLE_ID
    attempt_id: str = _ATTEMPT_ID


@dataclass(frozen=True, slots=True)
class FinalizeAttempt:
    """Typed command for explicit PASS/FAIL/BLOCKED terminalization."""

    outcome: FinalDisposition | str | None = None
    reason_code: str | None = None
    approved_review_id: str | None = None
    selected_export_snapshot_ids: tuple[str, ...] = ()
    owner_cap_micro_usd: int | None = None
    pricing_record_id: str | None = None
    sample_id: str = _SAMPLE_ID
    attempt_id: str = _ATTEMPT_ID


def _freeze(value: object) -> object:
    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, object], value)
        frozen: dict[str, object] = {}
        for key, item in mapping.items():
            if type(key) is not str:
                continue
            frozen[key] = _freeze(item)
        return frozen
    if isinstance(value, (list, tuple)):
        sequence = cast(Sequence[object], value)
        return tuple(_freeze(item) for item in sequence)
    return value


@dataclass(frozen=True, slots=True)
class PilotP2OperatorSnapshot(Mapping[str, object]):
    """Sanitized immutable projection of the operator binder state."""

    status: str = "NOT_STARTED"
    sample_id: str = _SAMPLE_ID
    attempt_id: str = _ATTEMPT_ID
    task_id: str | None = None
    task_revision: int | None = None
    input_revision: int | None = None
    result_id: str | None = None
    result_revision: int | None = None
    attempted_call_count: int = 0
    completed_call_count: int = 0
    observation: Mapping[str, object] = field(
        default_factory=lambda: cast(Mapping[str, object], {})
    )
    run: Mapping[str, object] | None = None
    exports: tuple[Mapping[str, object], ...] = ()
    review_status: str = "PENDING"
    review_record: Mapping[str, object] | None = None
    outcome: str | None = None
    outcome_record: Mapping[str, object] | None = None
    error_category: str | None = None
    terminal_stage: str | None = None
    artifact_root: Path | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "observation", cast(Mapping[str, object], _freeze(self.observation))
        )
        if self.run is not None:
            object.__setattr__(
                self, "run", cast(Mapping[str, object], _freeze(self.run))
            )
        object.__setattr__(
            self,
            "exports",
            tuple(cast(Mapping[str, object], _freeze(item)) for item in self.exports),
        )
        if self.review_record is not None:
            object.__setattr__(
                self,
                "review_record",
                cast(Mapping[str, object], _freeze(self.review_record)),
            )
        if self.outcome_record is not None:
            object.__setattr__(
                self,
                "outcome_record",
                cast(Mapping[str, object], _freeze(self.outcome_record)),
            )

    def __getitem__(self, key: str) -> object:
        return {
            "status": self.status,
            "sample_id": self.sample_id,
            "attempt_id": self.attempt_id,
            "task_id": self.task_id,
            "task_revision": self.task_revision,
            "input_revision": self.input_revision,
            "result_id": self.result_id,
            "result_revision": self.result_revision,
            "attempted_call_count": self.attempted_call_count,
            "completed_call_count": self.completed_call_count,
            "observation": self.observation,
            "run": self.run,
            "exports": self.exports,
            "review_status": self.review_status,
            "review_record": self.review_record,
            "outcome": self.outcome,
            "outcome_record": self.outcome_record,
            "error_category": self.error_category,
            "terminal_stage": self.terminal_stage,
        }[key]

    def __iter__(self):
        return iter(
            (
                "status",
                "sample_id",
                "attempt_id",
                "task_id",
                "task_revision",
                "input_revision",
                "result_id",
                "result_revision",
                "attempted_call_count",
                "completed_call_count",
                "observation",
                "run",
                "exports",
                "review_status",
                "review_record",
                "outcome",
                "outcome_record",
                "error_category",
                "terminal_stage",
            )
        )

    def __len__(self) -> int:
        return 19


class _ObserverLike(Protocol):
    def snapshot(self) -> Mapping[str, object]: ...


@dataclass(frozen=True, slots=True)
class _HttpResponse:
    status_code: int
    content: bytes

    def json(self) -> object:
        try:
            return json.loads(self.content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise PilotP2OperatorError(OperatorErrorCode.HTTP_COMMAND_FAILED) from None


class _InProcessHttpClient:
    """Small ASGI client that never opens a network socket."""

    def __init__(self, application: Any):
        self._application = application

    def _request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        payload: Mapping[str, object] | None = None,
    ) -> _HttpResponse:
        body = (
            b""
            if payload is None
            else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        )
        request_headers = [(b"host", b"127.0.0.1")]
        if body:
            request_headers.append((b"content-type", b"application/json"))
        if headers is not None:
            request_headers.extend(
                (key.lower().encode("ascii"), value.encode("utf-8"))
                for key, value in headers.items()
            )
        messages: list[dict[str, object]] = [
            {"type": "http.request", "body": body, "more_body": False}
        ]
        response_status = 500
        response_body: list[bytes] = []

        async def receive() -> dict[str, object]:
            if messages:
                return messages.pop(0)
            return {"type": "http.disconnect"}

        async def send(message: dict[str, object]) -> None:
            nonlocal response_status
            if message.get("type") == "http.response.start":
                status = message.get("status")
                if type(status) is int:
                    response_status = status
            elif message.get("type") == "http.response.body":
                chunk = message.get("body", b"")
                if type(chunk) is bytes:
                    response_body.append(chunk)

        scope: dict[str, object] = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("ascii"),
            "query_string": b"",
            "root_path": "",
            "headers": request_headers,
            "client": ("127.0.0.1", 0),
            "server": ("127.0.0.1", 0),
            "state": {},
        }

        async def invoke() -> None:
            await self._application(scope, receive, send)

        try:
            asyncio.run(invoke())
        except PilotP2OperatorError:
            raise
        except Exception:
            raise PilotP2OperatorError(OperatorErrorCode.HTTP_COMMAND_FAILED) from None
        return _HttpResponse(response_status, b"".join(response_body))

    @staticmethod
    def _object(response: _HttpResponse) -> Mapping[str, object]:
        if response.status_code >= 400:
            raise PilotP2OperatorError(OperatorErrorCode.HTTP_COMMAND_FAILED)
        value = response.json()
        if not isinstance(value, Mapping):
            raise PilotP2OperatorError(OperatorErrorCode.HTTP_COMMAND_FAILED)
        return cast(Mapping[str, object], value)

    def create_task(self, *, idempotency_key: str) -> Mapping[str, object]:
        return self._object(
            self._request(
                "POST",
                "/api/v1/tasks",
                headers={"Idempotency-Key": idempotency_key},
                payload={
                    "taskName": "Real P01 Product-to-Brief attempt",
                    "productCategory": "Category A",
                    "promotionGoal": "Product-to-Brief pilot",
                },
            )
        )

    def save_primary_input(
        self, *, task_id: str, content: str, file_name: str
    ) -> Mapping[str, object]:
        return self._object(
            self._request(
                "PUT",
                f"/api/v1/tasks/{task_id}/primary-input",
                payload={
                    "inputKind": "text_file",
                    "fileName": file_name,
                    "content": content,
                },
            )
        )

    def generate_result(
        self, *, task_id: str, input_revision: int, idempotency_key: str
    ) -> Mapping[str, object]:
        return self._object(
            self._request(
                "POST",
                f"/api/v1/tasks/{task_id}/commands/generate-result",
                headers={"Idempotency-Key": idempotency_key},
                payload={"expectedInputRevision": input_revision},
            )
        )

    def current_result(self, *, task_id: str) -> Mapping[str, object]:
        return self._object(
            self._request("GET", f"/api/v1/tasks/{task_id}/current-result")
        )

    def confirm_result(
        self,
        *,
        task_id: str,
        result_revision: int,
        marketing_core_message: str,
        xiaohongshu_title_direction: str,
        idempotency_key: str,
    ) -> Mapping[str, object]:
        return self._object(
            self._request(
                "POST",
                f"/api/v1/tasks/{task_id}/commands/confirm-current-result",
                headers={"Idempotency-Key": idempotency_key},
                payload={
                    "expectedResultRevision": result_revision,
                    "marketingCoreMessage": marketing_core_message,
                    "xiaohongshuTitleDirection": xiaohongshu_title_direction,
                },
            )
        )

    def preview_export(self, *, task_id: str, brief_kind: str) -> Mapping[str, object]:
        return self._object(
            self._request(
                "POST",
                f"/api/v1/tasks/{task_id}/export-previews",
                payload={"briefKind": brief_kind},
            )
        )

    def create_export_snapshot(
        self, *, basis: Mapping[str, object], idempotency_key: str
    ) -> Mapping[str, object]:
        return self._object(
            self._request(
                "POST",
                "/api/v1/export-snapshots",
                headers={"Idempotency-Key": idempotency_key},
                payload={"basis": dict(basis)},
            )
        )

    def download_export(self, *, content_location: str) -> bytes:
        response = self._request("GET", content_location)
        if response.status_code >= 400:
            raise PilotP2OperatorError(OperatorErrorCode.HTTP_COMMAND_FAILED)
        return response.content


_CompositionFactory = Callable[..., Any]
_HttpClientFactory = Callable[[Any], Any]
_COMPOSITION_FACTORY: _CompositionFactory = pilot_p2.compose_pilot_p2_postgres
_HTTP_CLIENT_FACTORY: _HttpClientFactory = _InProcessHttpClient


class PilotP2Operator:
    """Deep P2 operator module with four typed commands and one read seam."""

    def __init__(
        self,
        *,
        repository_root: Path | str,
        approved_inputs_root: Path | str,
        approved_artifact_parent: Path | str,
        postgres_config: PostgresEngineConfig,
        http_config: FixedWorkspaceHttpConfig,
        owner_cap_micro_usd: int | None = None,
        pricing_record_id: str | None = None,
        schema: str = "public",
        runtime_factory: RuntimeBuilder | None = None,
    ) -> None:
        self._repository_root = self._directory(repository_root, "repository_root")
        self._approved_inputs_root = self._directory(
            approved_inputs_root, "approved_inputs_root"
        )
        self._approved_artifact_parent = self._directory(
            approved_artifact_parent, "approved_artifact_parent"
        )
        if self._approved_inputs_root.is_relative_to(self._repository_root):
            raise PilotP2OperatorError(OperatorErrorCode.INPUT_ROOT_INVALID)
        if self._approved_artifact_parent.is_relative_to(self._repository_root):
            raise PilotP2OperatorError(
                OperatorErrorCode.ARTIFACT_ROOT_INSIDE_REPOSITORY
            )
        if type(postgres_config) is not PostgresEngineConfig:
            raise TypeError("postgres_config must be PostgresEngineConfig")
        if type(http_config) is not FixedWorkspaceHttpConfig:
            raise TypeError("http_config must be FixedWorkspaceHttpConfig")
        if runtime_factory is not None and not callable(runtime_factory):
            raise TypeError("runtime_factory must be callable")
        self._postgres_config = postgres_config
        self._http_config = http_config
        self._schema = schema
        self._runtime_factory = runtime_factory
        self._composition_factory = _COMPOSITION_FACTORY
        self._http_client_factory = _HTTP_CLIENT_FACTORY
        self._owner_cap_micro_usd = owner_cap_micro_usd
        self._pricing_record_id = pricing_record_id
        self._artifacts: PilotAttemptArtifacts | None = None
        self._task_id: str | None = None
        self._task_revision: int | None = None
        self._input_revision: int | None = None
        self._result_id: str | None = None
        self._result_revision: int | None = None
        self._last_error_category: str | None = None
        self._terminal_stage: str | None = None

    @staticmethod
    def _directory(value: Path | str, field_name: str) -> Path:
        path = value if isinstance(value, Path) else Path(value)
        if not path.is_absolute() or path.is_symlink() or not path.is_dir():
            code = (
                OperatorErrorCode.INPUT_ROOT_INVALID
                if "input" in field_name
                else OperatorErrorCode.ARTIFACT_ROOT_INVALID
                if "artifact" in field_name
                else OperatorErrorCode.GIT_HEAD_MISMATCH
            )
            raise PilotP2OperatorError(code)
        try:
            resolved = path.resolve(strict=True)
        except OSError:
            raise PilotP2OperatorError(
                OperatorErrorCode.ARTIFACT_ROOT_INVALID
            ) from None
        if resolved.is_symlink():
            raise PilotP2OperatorError(OperatorErrorCode.ARTIFACT_ROOT_INVALID)
        return resolved

    def apply(
        self,
        command: StartAttempt | ConfirmAndCapture | SubmitHumanReview | FinalizeAttempt,
    ) -> PilotP2OperatorSnapshot:
        """Apply exactly one typed operator command."""

        if type(command) is StartAttempt:
            return self._start(command)
        if type(command) is ConfirmAndCapture:
            return self._confirm_and_capture(command)
        if type(command) is SubmitHumanReview:
            return self._submit_review(command)
        if type(command) is FinalizeAttempt:
            return self._finalize(command)
        raise PilotP2OperatorError(OperatorErrorCode.INVALID_COMMAND)

    def read(self) -> PilotP2OperatorSnapshot:
        """Read the durable current state without starting composition."""

        artifacts = self._artifact_service()
        try:
            artifact = artifacts.read(_ATTEMPT_ID)
        except AttemptArtifactError as error:
            if error.error_code == "attempt_not_found":
                return PilotP2OperatorSnapshot()
            raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID) from None
        return self._snapshot_from_artifact(artifact)

    def _artifact_service(self) -> PilotAttemptArtifacts:
        if self._artifacts is None:
            self._artifacts = PilotAttemptArtifacts(
                self._repository_root, self._approved_artifact_parent
            )
        return self._artifacts

    def _validate_start(
        self, command: StartAttempt
    ) -> tuple[Path, Path, str, int, str]:
        if command.sample_id != _SAMPLE_ID or command.attempt_id != _ATTEMPT_ID:
            raise PilotP2OperatorError(OperatorErrorCode.IDENTITY_MISMATCH)
        actual_head = self._git_head()
        requested_commit = command.authorized_commit or command.git_commit
        if type(requested_commit) is not str or requested_commit != actual_head:
            raise PilotP2OperatorError(OperatorErrorCode.GIT_HEAD_MISMATCH)
        if command.git_commit is not None and command.git_commit != actual_head:
            raise PilotP2OperatorError(OperatorErrorCode.GIT_HEAD_MISMATCH)
        if command.git_head is not None and command.git_head != actual_head:
            raise PilotP2OperatorError(OperatorErrorCode.GIT_HEAD_MISMATCH)
        if type(command.owner_cap_micro_usd) is not int:
            raise PilotP2OperatorError(OperatorErrorCode.OWNER_CAP_INVALID)
        if command.owner_cap_micro_usd <= 0:
            raise PilotP2OperatorError(OperatorErrorCode.OWNER_CAP_INVALID)
        if command.owner_cap_micro_usd < DEEPSEEK_P2_RESERVATION_MICRO_USD:
            raise PilotP2OperatorError(OperatorErrorCode.OWNER_CAP_UNDERFUNDED)
        if command.pricing_record_id != _PRICING_RECORD_ID:
            raise PilotP2OperatorError(OperatorErrorCode.PRICING_RECORD_MISMATCH)
        if (
            command.max_calls != _MAX_CALLS
            or command.retry_count != 0
            or command.recovery_count != 0
            or command.replay_count != 0
            or command.fallback_count != 0
            or command.manual_intervention_count != 0
        ):
            raise PilotP2OperatorError(OperatorErrorCode.EXECUTION_POLICY_INVALID)
        input_path = self._validate_input_path(command.input_path)
        artifact_root = self._validate_artifact_root(command.artifact_root)
        try:
            content = input_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            raise PilotP2OperatorError(
                OperatorErrorCode.INPUT_CONTENT_INVALID
            ) from None
        if type(content) is not str or not content.strip():
            raise PilotP2OperatorError(OperatorErrorCode.INPUT_CONTENT_INVALID)
        try:
            pilot_p2.validate_p2_input(
                sample_id=command.sample_id,
                attempt_id=command.attempt_id,
                input_text=content,
            )
        except (TypeError, ValueError):
            raise PilotP2OperatorError(OperatorErrorCode.IDENTITY_MISMATCH) from None
        return (
            input_path,
            artifact_root,
            content,
            command.owner_cap_micro_usd,
            cast(str, command.pricing_record_id),
        )

    def _git_head(self) -> str:
        try:
            completed = subprocess.run(
                ["git", "-C", os.fspath(self._repository_root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (OSError, subprocess.SubprocessError):
            raise PilotP2OperatorError(OperatorErrorCode.GIT_HEAD_MISMATCH) from None
        head = completed.stdout.strip()
        if not head:
            raise PilotP2OperatorError(OperatorErrorCode.GIT_HEAD_MISMATCH)
        return head

    def _validate_input_path(self, value: Path | str | None) -> Path:
        if value is None:
            raise PilotP2OperatorError(OperatorErrorCode.INPUT_PATH_INVALID)
        path = value if isinstance(value, Path) else Path(value)
        if not path.is_absolute() or path.is_symlink() or not path.is_file():
            raise PilotP2OperatorError(OperatorErrorCode.INPUT_PATH_INVALID)
        try:
            relative = path.resolve(strict=True).relative_to(self._approved_inputs_root)
        except (OSError, ValueError):
            raise PilotP2OperatorError(OperatorErrorCode.INPUT_OUTSIDE_ROOT) from None
        if not relative.parts or any(
            part in {"", ".", ".."} for part in relative.parts
        ):
            raise PilotP2OperatorError(OperatorErrorCode.INPUT_PATH_INVALID)
        if path.resolve(strict=True).is_relative_to(self._repository_root):
            raise PilotP2OperatorError(OperatorErrorCode.INPUT_OUTSIDE_ROOT)
        if any(marker in path.name.casefold() for marker in _FIXTURE_MARKERS):
            raise PilotP2OperatorError(OperatorErrorCode.FIXTURE_INPUT_REJECTED)
        return path.resolve(strict=True)

    def _validate_artifact_root(self, value: Path | str | None) -> Path:
        if value is None:
            raise PilotP2OperatorError(OperatorErrorCode.ARTIFACT_ROOT_INVALID)
        path = value if isinstance(value, Path) else Path(value)
        if not path.is_absolute() or path.is_symlink():
            raise PilotP2OperatorError(OperatorErrorCode.ARTIFACT_ROOT_INVALID)
        lexical = Path(os.path.normpath(os.fspath(path)))
        expected = self._approved_artifact_parent / "p2" / _SAMPLE_ID / _ATTEMPT_ID
        if lexical != expected:
            raise PilotP2OperatorError(OperatorErrorCode.ARTIFACT_ROOT_INVALID)
        if lexical.is_relative_to(self._repository_root):
            raise PilotP2OperatorError(
                OperatorErrorCode.ARTIFACT_ROOT_INSIDE_REPOSITORY
            )
        current = self._approved_artifact_parent
        for part in lexical.relative_to(self._approved_artifact_parent).parts:
            current /= part
            if current.is_symlink():
                raise PilotP2OperatorError(OperatorErrorCode.ARTIFACT_ROOT_INVALID)
        if lexical.exists():
            raise PilotP2OperatorError(OperatorErrorCode.ARTIFACT_ROOT_EXISTS)
        return lexical

    def _compose(
        self, *, owner_cap: int, pricing_record_id: str
    ) -> tuple[Any, P2RuntimeObserver]:
        observer: _ObserverLike = P2RuntimeObserver()
        try:
            composition = self._composition_factory(
                self._postgres_config,
                self._http_config,
                schema=self._schema,
                sample_id=_SAMPLE_ID,
                attempt_id=_ATTEMPT_ID,
                owner_cap_micro_usd=owner_cap,
                pricing_record_id=pricing_record_id,
                runtime_builder=self._runtime_factory,
                runtime_observer=observer,
            )
        except PilotP2OperatorError:
            raise
        except Exception:
            raise PilotP2OperatorError(
                OperatorErrorCode.POSTGRES_COMPOSITION_FAILED
            ) from None
        return composition, observer

    def _start(self, command: StartAttempt) -> PilotP2OperatorSnapshot:
        input_path, artifact_root, content, owner_cap, pricing_record_id = (
            self._validate_start(command)
        )
        artifacts = self._artifact_service()
        try:
            artifacts.apply(ReserveAttempt(artifact_root))
        except AttemptArtifactError:
            raise PilotP2OperatorError(OperatorErrorCode.ARTIFACT_ROOT_EXISTS) from None
        composition: Any | None = None
        observer = P2RuntimeObserver()
        task_id: str | None = None
        task_revision: int | None = None
        input_revision: int | None = None
        result_id: str | None = None
        result_revision: int | None = None
        primary_failure: PilotP2OperatorError | None = None
        try:
            composition, observer = self._compose(
                owner_cap=owner_cap, pricing_record_id=pricing_record_id
            )
            if composition is None:
                raise PilotP2OperatorError(
                    OperatorErrorCode.POSTGRES_COMPOSITION_FAILED
                )
            observer = self._composition_observer(composition, observer)
            client = self._http_client_factory(composition.application)
            task = client.create_task(idempotency_key=f"operator-{_ATTEMPT_ID}-task")
            task_id = self._string(task, "taskId")
            task_revision = self._integer(task, "revision")
            saved = client.save_primary_input(
                task_id=task_id, content=content, file_name=input_path.name
            )
            if self._string(saved, "taskId") != task_id:
                raise PilotP2OperatorError(OperatorErrorCode.IDENTITY_MISMATCH)
            input_revision = self._integer(saved, "inputRevision")
            generated = client.generate_result(
                task_id=task_id,
                input_revision=input_revision,
                idempotency_key=f"operator-{_ATTEMPT_ID}-generate",
            )
            if (
                self._string(generated, "taskId") != task_id
                or self._integer(generated, "inputRevision") != input_revision
            ):
                raise PilotP2OperatorError(OperatorErrorCode.IDENTITY_MISMATCH)
            result_revision = self._integer(generated, "resultRevision")
            result_id = f"{task_id}:r{result_revision}"
            if self._string(generated, "status") != "awaiting_review":
                raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID)
            self._record_run(
                artifacts,
                observer,
                task_id=task_id,
                task_revision=task_revision,
                result_id=result_id,
                result_revision=result_revision,
                input_revision=input_revision,
                completed=True,
                owner_cap_micro_usd=owner_cap,
                pricing_record_id=pricing_record_id,
            )
            self._remember(
                owner_cap=owner_cap,
                pricing_record_id=pricing_record_id,
                task_id=task_id,
                task_revision=task_revision,
                input_revision=input_revision,
                result_id=result_id,
                result_revision=result_revision,
            )
            snapshot = self.read()
            return self._with_state(snapshot, status="AWAITING_CONFIRMATION")
        except Exception as error:
            observer = self._composition_observer(composition, observer)
            self._remember(
                owner_cap=owner_cap,
                pricing_record_id=pricing_record_id,
                task_id=task_id,
                task_revision=task_revision,
                input_revision=input_revision,
                result_id=result_id,
                result_revision=result_revision,
            )
            try:
                self._durable_failure(
                    artifacts,
                    observer,
                    task_id=task_id,
                    task_revision=task_revision,
                    result_id=result_id,
                    result_revision=result_revision,
                    input_revision=input_revision,
                    lifecycle_phase="generation",
                    owner_cap_micro_usd=owner_cap,
                    pricing_record_id=pricing_record_id,
                    error=error,
                )
            except PilotP2OperatorError as durable_error:
                primary_failure = durable_error
                raise
            return self.read()
        finally:
            try:
                self._close(composition)
            except PilotP2OperatorError:
                # Preserve a primary durable/binder error.  If there was no
                # primary failure, cleanup remains observable to the caller.
                if primary_failure is None:
                    raise

    def _confirm_and_capture(
        self, command: ConfirmAndCapture
    ) -> PilotP2OperatorSnapshot:
        if command.sample_id != _SAMPLE_ID or command.attempt_id != _ATTEMPT_ID:
            raise PilotP2OperatorError(OperatorErrorCode.IDENTITY_MISMATCH)
        if type(command.brief_kinds) is not tuple:
            raise PilotP2OperatorError(OperatorErrorCode.INVALID_COMMAND)
        kinds = command.brief_kinds
        if not 1 <= len(kinds) <= 2:
            raise PilotP2OperatorError(OperatorErrorCode.INVALID_COMMAND)
        if len(set(kinds)) != len(kinds) or any(
            kind not in _EXPORT_KINDS for kind in kinds
        ):
            raise PilotP2OperatorError(OperatorErrorCode.INVALID_COMMAND)
        if (
            type(command.marketing_core_message) is not str
            or not command.marketing_core_message.strip()
            or type(command.xiaohongshu_title_direction) is not str
            or not command.xiaohongshu_title_direction.strip()
        ):
            raise PilotP2OperatorError(OperatorErrorCode.INVALID_COMMAND)
        current = self.read()
        if current.status == "PENDING_HUMAN_REVIEW":
            return current
        if current.status != "AWAITING_CONFIRMATION" or current.run is None:
            raise PilotP2OperatorError(OperatorErrorCode.RESUME_NOT_AVAILABLE)
        cap = self._require_owner_cap(command.owner_cap_micro_usd)
        pricing = self._require_pricing(command.pricing_record_id)
        task_id = current.task_id
        task_revision = current.task_revision
        result_revision = current.result_revision
        if task_id is None or task_revision is None or result_revision is None:
            raise PilotP2OperatorError(OperatorErrorCode.RESUME_NOT_AVAILABLE)
        composition: Any | None = None
        observer: _ObserverLike = P2RuntimeObserver()
        lifecycle_phase = "confirmation"
        primary_failure: PilotP2OperatorError | None = None
        try:
            composition, observer = self._compose(
                owner_cap=cap, pricing_record_id=pricing
            )
            if composition is None:
                raise PilotP2OperatorError(
                    OperatorErrorCode.POSTGRES_COMPOSITION_FAILED
                )
            observer = self._composition_observer(composition, observer)
            client = self._http_client_factory(composition.application)
            persisted = client.current_result(task_id=task_id)
            if self._string(persisted, "taskId") != task_id:
                raise PilotP2OperatorError(OperatorErrorCode.IDENTITY_MISMATCH)
            if self._integer(persisted, "resultRevision") != result_revision:
                raise PilotP2OperatorError(OperatorErrorCode.IDENTITY_MISMATCH)
            if (
                current.input_revision is not None
                and self._integer(persisted, "inputRevision") != current.input_revision
            ):
                raise PilotP2OperatorError(OperatorErrorCode.IDENTITY_MISMATCH)
            client.confirm_result(
                task_id=task_id,
                result_revision=result_revision,
                marketing_core_message=command.marketing_core_message,
                xiaohongshu_title_direction=command.xiaohongshu_title_direction,
                idempotency_key=f"operator-{_ATTEMPT_ID}-confirm",
            )
            lifecycle_phase = "export"
            for kind in kinds:
                preview = client.preview_export(task_id=task_id, brief_kind=kind)
                basis = self._mapping(preview, "basis")
                exported = client.create_export_snapshot(
                    basis=basis,
                    idempotency_key=f"operator-{_ATTEMPT_ID}-export-{kind}",
                )
                content_location = self._string(exported, "contentLocation")
                if (
                    self._string(exported, "taskId") != task_id
                    or self._string(exported, "briefKind") != kind
                    or not content_location.startswith("/api/v1/export-snapshots/")
                ):
                    raise PilotP2OperatorError(OperatorErrorCode.IDENTITY_MISMATCH)
                content_bytes = client.download_export(
                    content_location=content_location
                )
                self._capture_export(
                    artifacts=self._artifact_service(),
                    task_id=task_id,
                    task_revision=task_revision,
                    result_revision=result_revision,
                    exported=exported,
                    content_bytes=content_bytes,
                    brief_kind=kind,
                )
            return self._with_state(self.read(), status="PENDING_HUMAN_REVIEW")
        except Exception as error:
            observer = self._composition_observer(composition, observer)
            try:
                self._durable_failure(
                    self._artifact_service(),
                    observer,
                    task_id=task_id,
                    task_revision=task_revision,
                    result_id=current.result_id,
                    result_revision=result_revision,
                    input_revision=current.input_revision,
                    lifecycle_phase=lifecycle_phase,
                    owner_cap_micro_usd=cap,
                    pricing_record_id=pricing,
                    error=error,
                )
            except PilotP2OperatorError as durable_error:
                primary_failure = durable_error
                raise
            return self.read()
        finally:
            try:
                self._close(composition)
            except PilotP2OperatorError:
                if primary_failure is None:
                    raise

    def _submit_review(self, command: SubmitHumanReview) -> PilotP2OperatorSnapshot:
        if command.sample_id != _SAMPLE_ID or command.attempt_id != _ATTEMPT_ID:
            raise PilotP2OperatorError(OperatorErrorCode.IDENTITY_MISMATCH)
        current = self.read()
        if current.status != "PENDING_HUMAN_REVIEW" or current.run is None:
            raise PilotP2OperatorError(OperatorErrorCode.REVIEW_NOT_AVAILABLE)
        if command.overall not in {"APPROVED", "REJECTED"}:
            raise PilotP2OperatorError(OperatorErrorCode.REVIEW_DECISION_REQUIRED)
        if (
            type(command.rationale) is not str
            or type(command.review_id) is not str
            or type(command.reviewer_role) is not str
            or command.reviewed_at is None
            or type(command.dimensions) is not tuple
            or type(command.captured_export_snapshot_ids) is not tuple
        ):
            raise PilotP2OperatorError(OperatorErrorCode.REVIEW_DECISION_REQUIRED)
        task_id = current.task_id
        task_revision = current.task_revision
        result_id = current.result_id
        result_revision = current.result_revision
        if (
            task_id is None
            or task_revision is None
            or result_id is None
            or result_revision is None
        ):
            raise PilotP2OperatorError(OperatorErrorCode.REVIEW_NOT_AVAILABLE)
        export_ids = command.captured_export_snapshot_ids
        if not export_ids:
            raise PilotP2OperatorError(OperatorErrorCode.REVIEW_NOT_AVAILABLE)
        dimensions = command.dimensions
        rationale = command.rationale
        review_id = command.review_id
        reviewed_at = command.reviewed_at
        try:
            self._artifact_service().apply(
                RecordReview(
                    task_id=task_id,
                    task_revision=task_revision,
                    result_id=result_id,
                    result_revision=result_revision,
                    review_id=review_id,
                    captured_export_snapshot_ids=export_ids,
                    reviewer_role=command.reviewer_role,
                    reviewed_at=reviewed_at,
                    dimensions=dimensions,
                    overall=command.overall,
                    rationale=rationale,
                    notes=command.notes,
                    material_edits=command.material_edits,
                )
            )
        except AttemptArtifactError:
            raise PilotP2OperatorError(OperatorErrorCode.FINALIZATION_INVALID) from None
        return self._with_state(self.read(), status="REVIEW_SUBMITTED")

    def _finalize(self, command: FinalizeAttempt) -> PilotP2OperatorSnapshot:
        if command.sample_id != _SAMPLE_ID or command.attempt_id != _ATTEMPT_ID:
            raise PilotP2OperatorError(OperatorErrorCode.IDENTITY_MISMATCH)
        if command.outcome is None or command.reason_code is None:
            raise PilotP2OperatorError(OperatorErrorCode.FINALIZATION_INVALID)
        current = self.read()
        if current.run is None or current.outcome is not None:
            raise PilotP2OperatorError(OperatorErrorCode.FINALIZATION_INVALID)
        outcome = (
            command.outcome.value
            if isinstance(command.outcome, FinalDisposition)
            else command.outcome
        )
        if outcome not in {item.value for item in FinalDisposition}:
            raise PilotP2OperatorError(OperatorErrorCode.FINALIZATION_INVALID)
        task_id = current.task_id
        task_revision = current.task_revision
        result_id = current.result_id
        result_revision = current.result_revision
        run = current.run
        task_mapping = self._mapping(run, "task")
        result_mapping = self._mapping(run, "result")
        if task_id is None:
            task_id = self._optional_string(task_mapping, "task_id")
        if task_revision is None:
            task_revision = self._optional_integer(task_mapping, "revision")
        if result_id is None:
            result_id = self._optional_string(result_mapping, "result_id")
        if result_revision is None:
            result_revision = self._optional_integer(result_mapping, "revision")
        cap = self._require_owner_cap(command.owner_cap_micro_usd)
        pricing = self._require_pricing(command.pricing_record_id)
        run_cost = self._mapping(run, "cost")
        actual_raw = run_cost.get("actual_micro_usd")
        actual: int | UnknownValue
        if type(actual_raw) is int:
            actual = actual_raw
        elif type(actual_raw) is str and actual_raw in {
            item.value for item in UnknownValue
        }:
            actual = UnknownValue(actual_raw)
        else:
            actual = UnknownValue.NOT_EXPOSED
        calls = run.get("calls")
        call_count = run.get("call_count")
        if type(call_count) is not int:
            call_count = (
                len(cast(Sequence[object], calls)) if isinstance(calls, Sequence) else 0
            )
        command_execution = FinalizationExecution(
            call_count=call_count,
            retry_count=0,
            recovery_count=0,
            replay_count=0,
            fallback_count=0,
            manual_intervention_count=0,
        )
        gates_mapping = run.get("gates")
        gates = FinalizationGates(
            schema=self._gate(gates_mapping, "schema", True),
            domain=self._gate(gates_mapping, "domain", True),
            persistence=self._gate(gates_mapping, "persistence", True),
            export=(
                True
                if outcome == FinalDisposition.PASS.value
                and bool(command.selected_export_snapshot_ids)
                else self._gate(gates_mapping, "export", False)
            ),
        )
        artifact_command = ArtifactFinalizeAttempt(
            task_id=task_id,
            task_revision=task_revision,
            result_id=result_id,
            result_revision=result_revision,
            outcome=outcome,
            reason_code=command.reason_code,
            approved_review_id=command.approved_review_id,
            selected_export_snapshot_ids=command.selected_export_snapshot_ids,
            automated_gates=gates,
            cost=FinalizationCost(
                actual_micro_usd=actual,
                owner_cap_micro_usd=cap,
                reservation_ref=pricing,
            ),
            execution=command_execution,
        )
        try:
            self._artifact_service().apply(artifact_command)
        except AttemptArtifactError:
            raise PilotP2OperatorError(OperatorErrorCode.FINALIZATION_INVALID) from None
        return self._with_state(self.read(), status=outcome)

    def _record_run(
        self,
        artifacts: PilotAttemptArtifacts,
        observer: _ObserverLike,
        *,
        task_id: str | None,
        task_revision: int | None,
        result_id: str | None,
        result_revision: int | None,
        input_revision: int | None,
        completed: bool,
        owner_cap_micro_usd: int,
        pricing_record_id: str,
    ) -> None:
        try:
            observed = observer.snapshot()
        except Exception:
            raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID) from None
        calls_value = observed.get("calls")
        if type(calls_value) in (tuple, list):
            call_values = cast(tuple[object, ...] | list[object], calls_value)
            if any(not isinstance(value, Mapping) for value in call_values):
                raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID)
            calls = tuple(cast(Mapping[str, object], value) for value in call_values)
        else:
            calls = ()
        self._validate_observed_calls(
            observed,
            calls,
            require_complete=completed,
        )
        sanitized_calls = tuple(
            {
                key: value
                for key, value in call.items()
                if key
                in {
                    "model_call_id",
                    "provider_attempt_ids",
                    "provider_response_id",
                    "provider_request_id",
                    "latency_ms",
                    "status",
                    "usage",
                }
            }
            for call in calls
        )
        attempted = observed.get("attempted_count")
        call_count = attempted if type(attempted) is int else len(calls)
        provider_id = self._optional_string(observed, "provider_id") or "deepseek"
        api_family = self._optional_string(observed, "api_family") or "chat_completions"
        configured_model = (
            self._optional_string(observed, "configured_model_id") or "deepseek-v4-pro"
        )
        resolved_model = (
            self._optional_string(observed, "resolved_model_id") or configured_model
        )
        usage = self._aggregate_usage(calls)
        actual = (
            UnknownValue.NOT_DERIVABLE
            if usage is not None
            else UnknownValue.NOT_EXPOSED
        )
        gates = {
            "schema": completed,
            "domain": completed,
            "persistence": completed,
            # Export is deliberately false until immutable export sidecars are captured.
            "export": False,
        }
        refs: list[ArtifactReference] = []
        if input_revision is not None:
            refs.append(ArtifactReference("input_revision", str(input_revision)))
        if not completed:
            failure = self._failure_category(calls)
            terminal_stage = self._failure_stage(calls)
            refs.append(
                ArtifactReference(
                    "terminal_stage", self._terminal_stage or terminal_stage
                )
            )
            refs.append(ArtifactReference("failure_category", failure))
        artifacts.apply(
            RecordRun(
                task_id=task_id,
                task_revision=task_revision,
                result_id=result_id,
                result_revision=result_revision,
                provider_id=provider_id,
                api_family=api_family,
                configured_model_id=configured_model,
                resolved_model_id=resolved_model,
                base_url="https://api.deepseek.com",
                reasoning_effort="high",
                pricing_record_id=pricing_record_id,
                pricing_source_url=DEEPSEEK_PRICING_RECORD.source_url,
                pricing_model_id=DEEPSEEK_PRICING_RECORD.model_id,
                started_at_utc=datetime.now(UTC),
                completed_at_utc=datetime.now(UTC) if completed else None,
                gates=gates,
                call_count=call_count,
                calls=sanitized_calls,
                usage=usage,
                cost={
                    "reserved_micro_usd": DEEPSEEK_P2_RESERVATION_MICRO_USD,
                    "actual_micro_usd": actual,
                },
                refs=refs,
            )
        )

    def _durable_failure(
        self,
        artifacts: PilotAttemptArtifacts,
        observer: _ObserverLike,
        *,
        task_id: str | None,
        task_revision: int | None,
        result_id: str | None,
        result_revision: int | None,
        input_revision: int | None,
        lifecycle_phase: str,
        owner_cap_micro_usd: int,
        pricing_record_id: str,
        error: BaseException,
    ) -> None:
        category = self._error_category(error)
        phase_stage = (
            lifecycle_phase
            if lifecycle_phase in _SAFE_LIFECYCLE_PHASES
            else "generation"
        )
        current_run: Mapping[str, object] | None = None
        current_outcome: str | None = None
        try:
            current = artifacts.read(_ATTEMPT_ID)
            current_run = current.run
            current_outcome = current.outcome
        except AttemptArtifactError:
            raise PilotP2OperatorError(OperatorErrorCode.DURABILITY_FAILED) from None
        if current_run is None:
            try:
                self._record_run(
                    artifacts,
                    observer,
                    task_id=task_id,
                    task_revision=task_revision,
                    result_id=result_id,
                    result_revision=result_revision,
                    input_revision=input_revision,
                    completed=False,
                    owner_cap_micro_usd=owner_cap_micro_usd,
                    pricing_record_id=pricing_record_id,
                )
                current_run = artifacts.read(_ATTEMPT_ID).run
            except (AttemptArtifactError, PilotP2OperatorError):
                raise PilotP2OperatorError(
                    OperatorErrorCode.DURABILITY_FAILED
                ) from None
        if current_run is None:
            raise PilotP2OperatorError(OperatorErrorCode.DURABILITY_FAILED)
        if current_outcome is not None:
            self._last_error_category = category
            return
        try:
            calls = current_run.get("calls")
            call_count = current_run.get("call_count")
            if type(call_count) is not int:
                call_count = (
                    len(cast(Sequence[object], calls))
                    if isinstance(calls, Sequence)
                    else 0
                )
            gates_mapping = current_run.get("gates")
            gates = FinalizationGates(
                schema=self._gate(gates_mapping, "schema", False),
                domain=self._gate(gates_mapping, "domain", False),
                persistence=self._gate(gates_mapping, "persistence", False),
                export=self._gate(gates_mapping, "export", False),
            )
            actual_raw = self._mapping(current_run, "cost").get("actual_micro_usd")
            actual: int | UnknownValue = (
                actual_raw
                if type(actual_raw) is int
                else UnknownValue(actual_raw)
                if type(actual_raw) is str
                and actual_raw in {item.value for item in UnknownValue}
                else UnknownValue.NOT_EXPOSED
            )
            result = current_run.get("result")
            task = current_run.get("task")
            resolved_task_id = (
                self._optional_string(cast(Mapping[str, object], task), "task_id")
                if isinstance(task, Mapping)
                else task_id
            )
            resolved_task_revision = (
                self._optional_integer(cast(Mapping[str, object], task), "revision")
                if isinstance(task, Mapping)
                else task_revision
            )
            resolved_result_id = (
                self._optional_string(cast(Mapping[str, object], result), "result_id")
                if isinstance(result, Mapping)
                else result_id
            )
            resolved_result_revision = (
                self._optional_integer(cast(Mapping[str, object], result), "revision")
                if isinstance(result, Mapping)
                else result_revision
            )
            current_calls = tuple(
                cast(Mapping[str, object], value)
                for value in cast(Sequence[object], current_run.get("calls", ()))
                if isinstance(value, Mapping)
            )
            terminal_stage = (
                self._failure_stage(current_calls)
                if phase_stage == "generation"
                else phase_stage
            )
            artifacts.apply(
                ArtifactFinalizeAttempt(
                    task_id=resolved_task_id,
                    task_revision=resolved_task_revision,
                    result_id=resolved_result_id,
                    result_revision=resolved_result_revision,
                    outcome=FinalDisposition.FAIL,
                    reason_code=(
                        "execution_not_qualified"
                        if call_count != _MAX_CALLS or resolved_result_id is None
                        else "automated_gate_failed"
                    ),
                    automated_gates=gates,
                    cost=FinalizationCost(
                        actual_micro_usd=actual,
                        owner_cap_micro_usd=owner_cap_micro_usd,
                        reservation_ref=pricing_record_id,
                    ),
                    execution=FinalizationExecution(
                        call_count=call_count,
                        manual_intervention_count=0,
                    ),
                    error_category=category,
                    terminal_stage=terminal_stage,
                )
            )
        except (AttemptArtifactError, PilotP2OperatorError):
            raise PilotP2OperatorError(OperatorErrorCode.DURABILITY_FAILED) from None
        self._last_error_category = category
        self._terminal_stage = terminal_stage

    def _capture_export(
        self,
        *,
        artifacts: PilotAttemptArtifacts,
        task_id: str,
        task_revision: int,
        result_revision: int,
        exported: Mapping[str, object],
        content_bytes: bytes,
        brief_kind: str,
    ) -> None:
        export_id = self._string(exported, "exportSnapshotId")
        if (
            self._string(exported, "taskId") != task_id
            or self._string(exported, "briefKind") != brief_kind
        ):
            raise PilotP2OperatorError(OperatorErrorCode.IDENTITY_MISMATCH)
        brief_version = self._mapping(exported, "briefVersion")
        upstream_values = exported.get("upstreamVersions")
        upstream = (
            tuple(
                ExportVersionReference(
                    self._string(cast(Mapping[str, object], item), "resourceVersionId"),
                    self._integer(cast(Mapping[str, object], item), "versionNumber"),
                )
                for item in cast(Sequence[object], upstream_values)
            )
            if isinstance(upstream_values, Sequence)
            else ()
        )
        file_name = (
            "marketing-brief.md"
            if brief_kind == "marketing"
            else "xiaohongshu-brief.md"
        )
        artifacts.apply(
            CaptureExport(
                task_id=task_id,
                task_revision=task_revision,
                result_id=f"{task_id}:r{result_revision}",
                result_revision=result_revision,
                export_snapshot_id=export_id,
                brief_kind=brief_kind,
                brief_version=ExportVersionReference(
                    self._string(brief_version, "resourceVersionId"),
                    self._integer(brief_version, "versionNumber"),
                ),
                upstream_versions=upstream,
                exported_at=self._string(exported, "exportedAt"),
                file_name=file_name,
                server_file_name=self._string(exported, "fileName"),
                template_version=self._string(exported, "templateVersion"),
                media_type=self._string(exported, "mediaType"),
                content_reference=ExportContentReference(
                    "local_relative", f"exports/{file_name}"
                ),
                content_bytes=content_bytes,
            )
        )

    @staticmethod
    def _validate_observed_calls(
        observed: Mapping[str, object],
        calls: tuple[Mapping[str, object], ...],
        *,
        require_complete: bool,
    ) -> None:
        """Validate the private observer's exact ordered P2 call record."""

        attempted_value = observed.get("attempted_count")
        completed_value = observed.get("completed_count")
        if type(attempted_value) is not int or type(completed_value) is not int:
            raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID)
        if not 0 <= attempted_value <= _MAX_CALLS or attempted_value != len(calls):
            raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID)
        completed_count = 0
        failed_count = 0
        expected_ids = tuple(
            f"P2-P01-A1-stage-{index}" for index in range(1, _MAX_CALLS + 1)
        )
        for index, call in enumerate(calls):
            model_call_id = call.get("model_call_id")
            status = call.get("status")
            if model_call_id != expected_ids[index] or status not in {
                "COMPLETED",
                "FAILED",
            }:
                raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID)
            if status == "COMPLETED":
                completed_count += 1
            else:
                failed_count += 1
                if index != len(calls) - 1:
                    raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID)
        if (
            completed_value != completed_count
            or completed_count + failed_count != attempted_value
        ):
            raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID)
        if failed_count > 1:
            raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID)
        if require_complete and (
            attempted_value != _MAX_CALLS
            or completed_count != _MAX_CALLS
            or failed_count != 0
        ):
            raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID)

    @staticmethod
    def _aggregate_usage(
        calls: tuple[Mapping[str, object], ...],
    ) -> Mapping[str, object] | None:
        totals = [0, 0, 0]
        found = False
        for call in calls:
            usage = call.get("usage")
            if not isinstance(usage, Mapping):
                return {
                    "input_tokens": UnknownValue.NOT_EXPOSED,
                    "output_tokens": UnknownValue.NOT_EXPOSED,
                    "total_tokens": UnknownValue.NOT_EXPOSED,
                }
            usage_mapping = cast(Mapping[str, object], usage)
            values: list[object] = [
                usage_mapping.get("input_tokens"),
                usage_mapping.get("output_tokens"),
                usage_mapping.get("total_tokens"),
            ]
            for value in values:
                if type(value) is not int or value < 0:
                    return {
                        "input_tokens": UnknownValue.NOT_EXPOSED,
                        "output_tokens": UnknownValue.NOT_EXPOSED,
                        "total_tokens": UnknownValue.NOT_EXPOSED,
                    }
            totals = [
                left + right
                for left, right in zip(
                    totals, (cast(int, value) for value in values), strict=True
                )
            ]
            found = True
        if not found:
            return None
        return {
            "input_tokens": totals[0],
            "output_tokens": totals[1],
            "total_tokens": totals[2],
        }

    def _snapshot_from_artifact(
        self, artifact: AttemptArtifactSnapshot
    ) -> PilotP2OperatorSnapshot:
        identity = artifact.identity
        run = artifact.run
        task_id: str | None = None
        task_revision: int | None = None
        input_revision: int | None = None
        result_id: str | None = None
        result_revision: int | None = None
        attempted = completed = 0
        observation: Mapping[str, object] = {}
        error_category = self._last_error_category
        terminal_stage = self._terminal_stage
        if isinstance(artifact.outcome_record, Mapping):
            durable_category = artifact.outcome_record.get("error_category")
            if (
                type(durable_category) is str
                and durable_category in _SAFE_FAILURE_CATEGORIES
            ):
                error_category = durable_category
            durable_stage = artifact.outcome_record.get("terminal_stage")
            if type(durable_stage) is str and durable_stage in _SAFE_TERMINAL_STAGES:
                terminal_stage = durable_stage
        if run is not None:
            task = run.get("task")
            result = run.get("result")
            if isinstance(task, Mapping):
                task_id = self._optional_string(
                    cast(Mapping[str, object], task), "task_id"
                )
                task_revision = self._optional_integer(
                    cast(Mapping[str, object], task), "revision"
                )
            if isinstance(result, Mapping):
                result_id = self._optional_string(
                    cast(Mapping[str, object], result), "result_id"
                )
                result_revision = self._optional_integer(
                    cast(Mapping[str, object], result), "revision"
                )
            call_count = run.get("call_count")
            attempted = call_count if type(call_count) is int else 0
            calls = run.get("calls")
            if isinstance(calls, Sequence):
                completed = sum(
                    1
                    for item in cast(Sequence[object], calls)
                    if isinstance(item, Mapping)
                    and cast(Mapping[str, object], item).get("status") == "COMPLETED"
                )
            observation = {
                "attempted_count": attempted,
                "completed_count": completed,
                "calls": tuple(cast(Sequence[object], calls))
                if isinstance(calls, Sequence)
                else (),
                "provider_id": self._optional_string(
                    cast(Mapping[str, object], run.get("provider", {})), "provider_id"
                ),
                "api_family": self._optional_string(
                    cast(Mapping[str, object], run.get("provider", {})), "api_family"
                ),
                "configured_model_id": self._optional_string(
                    cast(Mapping[str, object], run.get("model", {})),
                    "configured_model_id",
                ),
                "resolved_model_id": self._optional_string(
                    cast(Mapping[str, object], run.get("model", {})),
                    "resolved_model_id",
                ),
            }
            refs = run.get("refs")
            if isinstance(refs, Sequence):
                for ref in cast(Sequence[object], refs):
                    if (
                        isinstance(ref, Mapping)
                        and cast(Mapping[str, object], ref).get("kind")
                        == "failure_category"
                    ):
                        value = cast(Mapping[str, object], ref).get("value")
                        if error_category is None and type(value) is str:
                            error_category = value
                    if (
                        isinstance(ref, Mapping)
                        and cast(Mapping[str, object], ref).get("kind")
                        == "terminal_stage"
                    ):
                        value = cast(Mapping[str, object], ref).get("value")
                        if terminal_stage is None and type(value) is str:
                            terminal_stage = value
                    if (
                        isinstance(ref, Mapping)
                        and cast(Mapping[str, object], ref).get("kind")
                        == "input_revision"
                    ):
                        value = cast(Mapping[str, object], ref).get("value")
                        if type(value) is str and value.isdigit():
                            input_revision = int(value)
        status = "NOT_STARTED"
        if artifact.outcome is not None:
            status = artifact.outcome
        elif artifact.review != "PENDING":
            status = "REVIEW_SUBMITTED"
        elif artifact.exports:
            status = "PENDING_HUMAN_REVIEW"
        elif run is not None:
            status = "AWAITING_CONFIRMATION"
        return PilotP2OperatorSnapshot(
            status=status,
            sample_id=str(identity.get("sample_id", _SAMPLE_ID)),
            attempt_id=str(identity.get("attempt_id", _ATTEMPT_ID)),
            task_id=task_id,
            task_revision=task_revision,
            input_revision=input_revision,
            result_id=result_id,
            result_revision=result_revision,
            attempted_call_count=attempted,
            completed_call_count=completed,
            observation=observation,
            run=run,
            exports=tuple(artifact.exports.values()),
            review_status=artifact.review,
            review_record=artifact.review_record,
            outcome=artifact.outcome,
            outcome_record=artifact.outcome_record,
            error_category=error_category,
            terminal_stage=terminal_stage,
            artifact_root=artifact.artifact_root,
        )

    def _remember(
        self,
        *,
        owner_cap: int,
        pricing_record_id: str,
        task_id: str | None,
        task_revision: int | None,
        input_revision: int | None,
        result_id: str | None,
        result_revision: int | None,
    ) -> None:
        self._owner_cap_micro_usd = owner_cap
        self._pricing_record_id = pricing_record_id
        self._task_id = task_id
        self._task_revision = task_revision
        self._input_revision = input_revision
        self._result_id = result_id
        self._result_revision = result_revision

    def _with_state(
        self, snapshot: PilotP2OperatorSnapshot, *, status: str
    ) -> PilotP2OperatorSnapshot:
        return PilotP2OperatorSnapshot(
            status=status,
            sample_id=snapshot.sample_id,
            attempt_id=snapshot.attempt_id,
            task_id=snapshot.task_id,
            task_revision=snapshot.task_revision,
            input_revision=snapshot.input_revision,
            result_id=snapshot.result_id,
            result_revision=snapshot.result_revision,
            attempted_call_count=snapshot.attempted_call_count,
            completed_call_count=snapshot.completed_call_count,
            observation=snapshot.observation,
            run=snapshot.run,
            exports=snapshot.exports,
            review_status=snapshot.review_status,
            review_record=snapshot.review_record,
            outcome=snapshot.outcome,
            outcome_record=snapshot.outcome_record,
            error_category=snapshot.error_category,
            terminal_stage=snapshot.terminal_stage,
            artifact_root=snapshot.artifact_root,
        )

    @staticmethod
    def _composition_observer(
        composition: Any | None, fallback: _ObserverLike
    ) -> _ObserverLike:
        candidate = (
            None if composition is None else getattr(composition, "observer", None)
        )
        if isinstance(candidate, P2RuntimeObserver):
            return candidate
        if candidate is not None and callable(getattr(candidate, "snapshot", None)):
            return cast(_ObserverLike, candidate)
        return fallback

    @staticmethod
    def _close(composition: Any | None) -> None:
        if composition is None:
            return
        close = getattr(composition, "close", None)
        if callable(close):
            try:
                close()
            except Exception:
                raise PilotP2OperatorError(OperatorErrorCode.CLEANUP_FAILED) from None

    def _require_owner_cap(self, value: int | None) -> int:
        cap = self._owner_cap_micro_usd if value is None else value
        if type(cap) is not int or cap <= 0:
            raise PilotP2OperatorError(OperatorErrorCode.OWNER_CAP_INVALID)
        if cap < DEEPSEEK_P2_RESERVATION_MICRO_USD:
            raise PilotP2OperatorError(OperatorErrorCode.OWNER_CAP_UNDERFUNDED)
        return cap

    def _require_pricing(self, value: str | None) -> str:
        pricing = self._pricing_record_id if value is None else value
        if pricing != _PRICING_RECORD_ID:
            raise PilotP2OperatorError(OperatorErrorCode.PRICING_RECORD_MISMATCH)
        return cast(str, pricing)

    @staticmethod
    def _string(mapping: Mapping[str, object], key: str) -> str:
        value = mapping.get(key)
        if type(value) is not str or not value.strip():
            raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID)
        return value

    @staticmethod
    def _optional_string(mapping: Mapping[str, object], key: str) -> str | None:
        value = mapping.get(key)
        return value if type(value) is str and value.strip() else None

    @staticmethod
    def _integer(mapping: Mapping[str, object], key: str) -> int:
        value = mapping.get(key)
        if type(value) is not int or value < 0:
            raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID)
        return value

    @staticmethod
    def _optional_integer(mapping: Mapping[str, object], key: str) -> int | None:
        value = mapping.get(key)
        return value if type(value) is int and value >= 0 else None

    @staticmethod
    def _mapping(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
        value = mapping.get(key)
        if not isinstance(value, Mapping):
            raise PilotP2OperatorError(OperatorErrorCode.RUN_EVIDENCE_INVALID)
        return cast(Mapping[str, object], value)

    @staticmethod
    def _gate(value: object, key: str, default: bool) -> bool:
        if isinstance(value, Mapping):
            candidate = cast(Mapping[str, object], value).get(key)
            if type(candidate) is bool:
                return candidate
        return default

    @staticmethod
    def _failure_category(calls: tuple[Mapping[str, object], ...]) -> str:
        for call in calls:
            value = call.get("error_category")
            if type(value) is str and value in _SAFE_FAILURE_CATEGORIES:
                return value
        return "unknown_runtime_failure"

    @staticmethod
    def _failure_stage(calls: tuple[Mapping[str, object], ...]) -> str:
        for call in calls:
            if call.get("status") != "FAILED":
                continue
            model_call_id = call.get("model_call_id")
            if type(model_call_id) is str and "-stage-" in model_call_id:
                suffix = model_call_id.rsplit("-stage-", 1)[-1]
                if suffix.isdigit():
                    return f"stage-{suffix}"
        return "generation"

    @staticmethod
    def _error_category(error: BaseException) -> str:
        category = getattr(error, "category", None)
        value = getattr(category, "value", None)
        if type(value) is str and value in _SAFE_FAILURE_CATEGORIES:
            return value
        code = getattr(error, "error_code", None)
        if type(code) is str and code in _SAFE_FAILURE_CATEGORIES:
            return code
        return "operator_failure"
