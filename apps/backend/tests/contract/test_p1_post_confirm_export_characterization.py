"""Provider-free public-seam characterization for Issue #343.

The harness below deliberately injects interface-shaped fakes into the real
HTTP adapter.  It records only stage names and safe HTTP problem metadata; no
product, model, credential or provider material is retained.
"""

# FastAPI/Starlette's TestClient is an untyped framework test helper.  Keep
# this contract test focused on the public HTTP behavior and the fake seams.
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportPrivateUsage=false, reportUnusedFunction=false, reportCallIssue=false

from __future__ import annotations

import socket
import warnings
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal, cast

import pytest
from pytest_socket import SocketBlockedError, _true_socket
from starlette.exceptions import StarletteDeprecationWarning

from ai_ecommerce_agent.entrypoints.http import (
    FixedWorkspaceHttpConfig,
    create_task_http_application,
)
from ai_ecommerce_agent.modules.export_delivery.public import (
    ConfirmExportRequest,
    ExportBasis,
    ExportBriefKind,
    ExportPreview,
    ExportSnapshot,
)
from ai_ecommerce_agent.modules.source_evidence.public import (
    PrimaryInputKind,
    PrimaryInputSnapshot,
)
from ai_ecommerce_agent.modules.task_management.public import (
    CreateDraftTask,
    DomainVersionReference,
    TaskSnapshot,
    TaskStatus,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ExportSnapshotId,
    Revision,
    TaskId,
    VersionNumber,
)

warnings.filterwarnings("ignore", category=StarletteDeprecationWarning)
from fastapi.testclient import TestClient  # noqa: E402

pytestmark = pytest.mark.contract

NOW = datetime(2026, 8, 30, 0, 0, tzinfo=UTC)
TASK_ID = TaskId("task-p1-characterization")


@pytest.fixture(autouse=True)
def _allow_testclient_socketpair(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow TestClient's local Unix socketpair while blocking network I/O."""

    true_socket = _true_socket

    class LocalSocket(true_socket):  # type: ignore[misc, valid-type]
        def __new__(
            cls,
            family: socket.AddressFamily | int = -1,
            type: socket.SocketKind | int = -1,
            proto: int = -1,
            fileno: int | None = None,
        ) -> LocalSocket:
            if int(family) == int(socket.AF_UNIX):
                return super().__new__(cls, family, type, proto, fileno)
            raise SocketBlockedError()

    monkeypatch.setattr(socket, "socket", LocalSocket)


Stage = Literal[
    "CONFIRM",
    "PREVIEW_MARKETING",
    "SNAPSHOT_MARKETING",
    "DOWNLOAD_MARKETING",
    "PREVIEW_XIAOHONGSHU",
    "SNAPSHOT_XIAOHONGSHU",
    "DOWNLOAD_XIAOHONGSHU",
    "DISTINCT_SNAPSHOT_IDS",
    "UTF8_VALIDATE_MARKETING",
    "UTF8_VALIDATE_XIAOHONGSHU",
    "OUTSIDE_REPO_PRESERVE",
    "COMPLETE",
]

ALL_STAGES: tuple[Stage, ...] = (
    "CONFIRM",
    "PREVIEW_MARKETING",
    "SNAPSHOT_MARKETING",
    "DOWNLOAD_MARKETING",
    "PREVIEW_XIAOHONGSHU",
    "SNAPSHOT_XIAOHONGSHU",
    "DOWNLOAD_XIAOHONGSHU",
    "DISTINCT_SNAPSHOT_IDS",
    "UTF8_VALIDATE_MARKETING",
    "UTF8_VALIDATE_XIAOHONGSHU",
    "OUTSIDE_REPO_PRESERVE",
    "COMPLETE",
)

HISTORICAL_GATES: dict[str, bool] = {
    "validated_candidates": True,
    "confirmed_result": True,
    "marketing_export_immutable": False,
    "xiaohongshu_export_immutable": False,
    "downloads_utf8_no_bom_one_final_lf": False,
}

CHECKPOINT_PROBLEM: Mapping[str, object] = {
    "status": 0,
    "type": "urn:ai-ecommerce-agent:problem:validation-failed",
    "title": "Characterization checkpoint failed",
}


class _InjectedFailure(Exception):
    """Safe fake failure mapped by the HTTP adapter to a generic problem."""

    error_code = "validation_failed"
    retryability = False


@dataclass(frozen=True, slots=True)
class _Result:
    task_id: TaskId = TASK_ID
    result_revision: int = 0
    input_revision: int = 0
    status: str = "awaiting_review"
    generated_at: datetime = NOW
    missing_information: tuple[str, ...] = ()
    candidates: dict[str, object] = field(
        default_factory=lambda: {
            "productIntake": {"kind": "facts"},
            "customerInsight": {"kind": "insight"},
            "productPositioning": {"kind": "positioning"},
            "marketingBrief": {"kind": "marketing"},
            "xiaohongshuBrief": {"kind": "xiaohongshu"},
        }
    )
    confirmation: dict[str, object] | None = None


@dataclass(frozen=True, slots=True)
class _HarnessMetadata:
    """Sanitized result record; content and fake internals never cross it."""

    failed_stage: Stage | None
    brief_kind: str | None
    last_completed_stage: Stage | None
    operations: tuple[Stage, ...]
    problem: Mapping[str, object] | None
    legacy_gate_vector: Mapping[str, bool]


class _Tasks:
    """Interface-shaped Task application fake for the HTTP adapter."""

    def __init__(self) -> None:
        self.task = TaskSnapshot(
            task_id=TASK_ID,
            task_name="P1 characterization",
            product_category="synthetic",
            promotion_goal="characterization",
            task_status=TaskStatus.WAITING_FOR_REVIEW,
            revision=Revision.initial(),
            current_stage=None,
            active_run_id=None,
            latest_run_id=None,
            waiting_reason=None,
            updated_at=NOW,
        )

    def create_draft_task_idempotent(
        self, command: CreateDraftTask
    ) -> tuple[TaskSnapshot, bool]:
        del command
        return self.task, False

    def create_draft_task(self, command: CreateDraftTask) -> TaskSnapshot:
        del command
        return self.task

    def get_task(self, query: object) -> TaskSnapshot:
        del query
        return self.task

    def list_tasks(self, query: object) -> tuple[TaskSnapshot, ...]:
        del query
        return (self.task,)


class _PrimaryInputs:
    """Interface-shaped primary-input fake (not used by this seam)."""

    def __init__(self) -> None:
        self.input = PrimaryInputSnapshot(
            task_id=TASK_ID,
            input_kind=PrimaryInputKind.PASTED_TEXT,
            file_name=None,
            content="synthetic characterization input",
            byte_count=len(b"synthetic characterization input"),
            revision=Revision.initial(),
            updated_at=NOW,
        )

    def save_primary_input(self, command: object) -> PrimaryInputSnapshot:
        del command
        return self.input

    def get_primary_input(self, query: object) -> PrimaryInputSnapshot:
        del query
        return self.input


class _Coordinator:
    def generate(self, *, input_text: str) -> None:
        del input_text


class _Results:
    """Confirmed-result interface fake with one injectable failure boundary."""

    def __init__(self, failure: Stage | None, operations: list[Stage]) -> None:
        self.failure = failure
        self.operations = operations
        self.result = _Result()

    def generate_result(
        self,
        *,
        task_id: TaskId,
        idempotency_key: str,
        expected_input_revision: int,
        coordinator: object,
    ) -> tuple[_Result, bool]:
        del task_id, idempotency_key, expected_input_revision, coordinator
        return self.result, False

    def get_current_result(self, *, task_id: TaskId) -> _Result:
        del task_id
        return self.result

    def confirm_current_result(
        self,
        *,
        task_id: TaskId,
        idempotency_key: str,
        expected_result_revision: int,
        marketing_core_message: str,
        xiaohongshu_title_direction: str,
    ) -> tuple[_Result, bool]:
        del (
            task_id,
            idempotency_key,
            expected_result_revision,
            marketing_core_message,
            xiaohongshu_title_direction,
        )
        self.operations.append("CONFIRM")
        if self.failure == "CONFIRM":
            raise _InjectedFailure("confirm failed")
        return (
            _Result(
                status="confirmed",
                candidates=self.result.candidates,
                confirmation={
                    "marketingBriefVersion": {
                        "resourceKind": "marketing_brief",
                        "resourceVersionId": "marketing-v1",
                        "versionNumber": 1,
                    },
                    "xiaohongshuBriefVersion": {
                        "resourceKind": "xiaohongshu_brief",
                        "resourceVersionId": "xiaohongshu-v1",
                        "versionNumber": 1,
                    },
                    "confirmedAt": "2026-08-30T00:00:00Z",
                },
            ),
            False,
        )


def _basis(brief_kind: ExportBriefKind) -> ExportBasis:
    return ExportBasis(
        task_id=TASK_ID,
        task_revision=Revision.initial(),
        brief_kind=brief_kind,
        brief_version=DomainVersionReference(
            DomainVersionId(f"{brief_kind.value}-v1"), VersionNumber.initial()
        ),
        upstream_versions=(),
        hypotheses=("synthetic hypothesis",),
        evidence_limitations=("synthetic limitation",),
        risks=("synthetic risk",),
    )


class _Exports:
    """Export application fake exposing only the accepted public methods."""

    def __init__(self, failure: Stage | None, operations: list[Stage]) -> None:
        self.failure = failure
        self.operations = operations
        self.snapshots: dict[str, tuple[ExportSnapshot, str]] = {}

    @staticmethod
    def _kind(value: ExportBriefKind) -> str:
        return "marketing" if value is ExportBriefKind.MARKETING else "xiaohongshu"

    def preview_export(
        self, *, task_id: TaskId, brief_kind: ExportBriefKind
    ) -> ExportPreview:
        del task_id
        kind = self._kind(brief_kind)
        stage: Stage = (
            "PREVIEW_MARKETING" if kind == "marketing" else "PREVIEW_XIAOHONGSHU"
        )
        self.operations.append(stage)
        if self.failure == stage:
            raise _InjectedFailure("preview failed")
        return ExportPreview(
            basis=_basis(brief_kind),
            template_version="mvp0-markdown-v1",
            file_name=f"{kind}.md",
            media_type="text/markdown; charset=utf-8",
        )

    def create_export_snapshot(
        self, *, idempotency_key: str, request: ConfirmExportRequest
    ) -> tuple[ExportSnapshot, bool]:
        del idempotency_key
        kind = self._kind(request.basis.brief_kind)
        stage: Stage = (
            "SNAPSHOT_MARKETING" if kind == "marketing" else "SNAPSHOT_XIAOHONGSHU"
        )
        self.operations.append(stage)
        if self.failure == stage:
            raise _InjectedFailure("snapshot failed")

        snapshot_id = (
            "shared-snapshot"
            if self.failure == "DISTINCT_SNAPSHOT_IDS"
            else f"{kind}-snapshot"
        )
        snapshot = ExportSnapshot(
            export_snapshot_id=ExportSnapshotId(snapshot_id),
            task_id=TASK_ID,
            brief_kind=request.basis.brief_kind,
            brief_version=request.basis.brief_version,
            upstream_versions=request.basis.upstream_versions,
            exported_at=NOW,
            file_name=f"{kind}.md",
            media_type="text/markdown; charset=utf-8",
            content_location=f"/api/v1/export-snapshots/{snapshot_id}/content",
            template_version="mvp0-markdown-v1",
        )
        content = (
            "# Marketing Brief\n营销内容：界\n"
            if kind == "marketing"
            else "# Xiaohongshu Brief\n小红书内容：界\n"
        )
        if self.failure == "UTF8_VALIDATE_MARKETING" and kind == "marketing":
            content = "\ufeff" + content
        if self.failure == "UTF8_VALIDATE_XIAOHONGSHU" and kind == "xiaohongshu":
            content += "\n"
        self.snapshots[snapshot_id] = (snapshot, content)
        return snapshot, False

    def get_export_content(
        self, *, export_snapshot_id: ExportSnapshotId
    ) -> tuple[ExportSnapshot, str]:
        value = self.snapshots[str(export_snapshot_id)]
        kind = self._kind(value[0].brief_kind)
        stage: Stage = (
            "DOWNLOAD_MARKETING" if kind == "marketing" else "DOWNLOAD_XIAOHONGSHU"
        )
        self.operations.append(stage)
        if self.failure == stage:
            raise _InjectedFailure("download failed")
        return value


@dataclass
class _Driver:
    failure: Stage | None
    operations: list[Stage] = field(default_factory=list)
    gates: dict[str, bool] = field(
        default_factory=lambda: {
            "validated_candidates": True,
            "confirmed_result": False,
            "marketing_export_immutable": False,
            "xiaohongshu_export_immutable": False,
            "downloads_utf8_no_bom_one_final_lf": False,
        }
    )

    def run(self) -> _HarnessMetadata:
        application = create_task_http_application(
            config=FixedWorkspaceHttpConfig(
                workspace_id="workspace-p1",
                workbench_origin="http://127.0.0.1:5173",
            ),
            task_application=_Tasks(),
            primary_input_application=_PrimaryInputs(),
            result_application=_Results(self.failure, self.operations),
            pipeline_coordinator=_Coordinator(),
            export_application=_Exports(self.failure, self.operations),
        )
        last_completed: Stage | None = None
        with TestClient(application) as client:
            response = client.post(
                f"/api/v1/tasks/{TASK_ID}/commands/confirm-current-result",
                headers={"Idempotency-Key": "p1-confirm"},
                json={
                    "expectedResultRevision": 0,
                    "marketingCoreMessage": "confirmed synthetic message",
                    "xiaohongshuTitleDirection": "confirmed synthetic title",
                },
            )
            if response.status_code != 201:
                return self._problem("CONFIRM", None, response, last_completed)
            self.gates["confirmed_result"] = True
            last_completed = "CONFIRM"

            contents: dict[str, bytes] = {}
            snapshot_ids: list[str] = []
            for kind in ("marketing", "xiaohongshu"):
                preview_stage: Stage = (
                    "PREVIEW_MARKETING"
                    if kind == "marketing"
                    else "PREVIEW_XIAOHONGSHU"
                )
                preview = client.post(
                    f"/api/v1/tasks/{TASK_ID}/export-previews",
                    json={"briefKind": kind},
                )
                if preview.status_code != 200:
                    return self._problem(preview_stage, kind, preview, last_completed)
                last_completed = preview_stage

                snapshot_stage: Stage = (
                    "SNAPSHOT_MARKETING"
                    if kind == "marketing"
                    else "SNAPSHOT_XIAOHONGSHU"
                )
                snapshot = client.post(
                    "/api/v1/export-snapshots",
                    headers={"Idempotency-Key": f"p1-{kind}-snapshot"},
                    json={"basis": preview.json()["basis"]},
                )
                if snapshot.status_code != 201:
                    return self._problem(snapshot_stage, kind, snapshot, last_completed)
                snapshot_ids.append(snapshot.json()["exportSnapshotId"])
                last_completed = snapshot_stage

                download_stage: Stage = (
                    "DOWNLOAD_MARKETING"
                    if kind == "marketing"
                    else "DOWNLOAD_XIAOHONGSHU"
                )
                downloaded = client.get(snapshot.json()["contentLocation"])
                if downloaded.status_code != 200:
                    return self._problem(
                        download_stage, kind, downloaded, last_completed
                    )
                contents[kind] = downloaded.content
                last_completed = download_stage

            self.operations.append("DISTINCT_SNAPSHOT_IDS")
            if len(set(snapshot_ids)) != 2:
                return self._failure(
                    "DISTINCT_SNAPSHOT_IDS",
                    None,
                    last_completed,
                    CHECKPOINT_PROBLEM,
                )
            last_completed = "DISTINCT_SNAPSHOT_IDS"
            self.gates["marketing_export_immutable"] = True
            self.gates["xiaohongshu_export_immutable"] = True

            self.operations.append("UTF8_VALIDATE_MARKETING")
            try:
                self._validate_download(contents["marketing"])
            except _InjectedFailure:
                if self.failure != "UTF8_VALIDATE_MARKETING":
                    raise
                return self._failure(
                    "UTF8_VALIDATE_MARKETING",
                    "marketing",
                    last_completed,
                    CHECKPOINT_PROBLEM,
                )
            last_completed = "UTF8_VALIDATE_MARKETING"

            self.operations.append("UTF8_VALIDATE_XIAOHONGSHU")
            try:
                self._validate_download(contents["xiaohongshu"])
            except _InjectedFailure:
                if self.failure != "UTF8_VALIDATE_XIAOHONGSHU":
                    raise
                return self._failure(
                    "UTF8_VALIDATE_XIAOHONGSHU",
                    "xiaohongshu",
                    last_completed,
                    CHECKPOINT_PROBLEM,
                )
            last_completed = "UTF8_VALIDATE_XIAOHONGSHU"
            self.gates["downloads_utf8_no_bom_one_final_lf"] = True

            self.operations.append("OUTSIDE_REPO_PRESERVE")
            if self.failure == "OUTSIDE_REPO_PRESERVE":
                return self._failure(
                    "OUTSIDE_REPO_PRESERVE",
                    None,
                    last_completed,
                    CHECKPOINT_PROBLEM,
                )
            self._preserve_downloads(contents)
            last_completed = "OUTSIDE_REPO_PRESERVE"

            self.operations.append("COMPLETE")
            last_completed = "COMPLETE"
            return _HarnessMetadata(
                failed_stage=None,
                brief_kind=None,
                last_completed_stage=last_completed,
                operations=tuple(self.operations),
                problem=None,
                legacy_gate_vector=dict(self.gates),
            )

    @staticmethod
    def _validate_download(content: bytes) -> None:
        content.decode("utf-8")
        if content.startswith(b"\xef\xbb\xbf"):
            raise _InjectedFailure("download has a BOM")
        if not content.endswith(b"\n") or content.endswith(b"\n\n"):
            raise _InjectedFailure("download newline shape is invalid")

    @staticmethod
    def _preserve_downloads(contents: Mapping[str, bytes]) -> tuple[str, ...]:
        """Model the harness-only outside-repository two-file preservation."""

        if set(contents) != {"marketing", "xiaohongshu"}:
            raise _InjectedFailure("unexpected preservation keys")
        files = {
            "marketing-brief.md": contents["marketing"],
            "xiaohongshu-brief.md": contents["xiaohongshu"],
        }
        if any(not isinstance(value, bytes) for value in files.values()):
            raise _InjectedFailure("preserved content is not bytes")
        return tuple(sorted(files))

    def _failure(
        self,
        stage: Stage,
        brief_kind: str | None,
        last_completed: Stage | None,
        problem: Mapping[str, object] | None,
    ) -> _HarnessMetadata:
        return _HarnessMetadata(
            failed_stage=stage,
            brief_kind=brief_kind,
            last_completed_stage=last_completed,
            operations=tuple(self.operations),
            problem=problem,
            legacy_gate_vector=dict(self.gates),
        )

    def _problem(
        self,
        stage: Stage,
        brief_kind: str | None,
        response: Any,
        last_completed: Stage | None,
    ) -> _HarnessMetadata:
        payload = response.json()
        safe_metadata = {
            "status": response.status_code,
            "type": payload.get("type"),
            "title": payload.get("title"),
        }
        return self._failure(stage, brief_kind, last_completed, safe_metadata)


def _expected_prefix(stage: Stage) -> tuple[Stage, ...]:
    sequence: tuple[Stage, ...] = (
        "CONFIRM",
        "PREVIEW_MARKETING",
        "SNAPSHOT_MARKETING",
        "DOWNLOAD_MARKETING",
        "PREVIEW_XIAOHONGSHU",
        "SNAPSHOT_XIAOHONGSHU",
        "DOWNLOAD_XIAOHONGSHU",
        "DISTINCT_SNAPSHOT_IDS",
        "UTF8_VALIDATE_MARKETING",
        "UTF8_VALIDATE_XIAOHONGSHU",
        "OUTSIDE_REPO_PRESERVE",
        "COMPLETE",
    )
    return sequence[: sequence.index(stage) + 1]


def _expected_last_completed(stage: Stage) -> Stage | None:
    prefix = _expected_prefix(stage)
    if stage == "COMPLETE":
        return "COMPLETE"
    return prefix[-2] if len(prefix) > 1 else None


def _expected_brief_kind(stage: Stage) -> str | None:
    if "MARKETING" in stage:
        return "marketing"
    if "XIAOHONGSHU" in stage:
        return "xiaohongshu"
    return None


def test_normal_provider_free_public_path_reaches_complete() -> None:
    result = _Driver(None).run()

    assert result.failed_stage is None
    assert result.last_completed_stage == "COMPLETE"
    assert result.operations == _expected_prefix("COMPLETE")
    assert result.problem is None
    assert dict(result.legacy_gate_vector) == {
        "validated_candidates": True,
        "confirmed_result": True,
        "marketing_export_immutable": True,
        "xiaohongshu_export_immutable": True,
        "downloads_utf8_no_bom_one_final_lf": True,
    }
    assert "营销内容" not in repr(result)
    assert "小红书内容" not in repr(result)


@pytest.mark.parametrize(
    ("stage", "expected_failed_stage", "expected_last_completed"),
    [
        (
            stage,
            None if stage == "COMPLETE" else stage,
            _expected_last_completed(stage),
        )
        for stage in ALL_STAGES
    ],
)
def test_each_injected_checkpoint_has_unique_attribution_and_stops(
    stage: Stage,
    expected_failed_stage: Stage | None,
    expected_last_completed: Stage | None,
) -> None:
    result = _Driver(None if stage == "COMPLETE" else stage).run()

    assert result.failed_stage == expected_failed_stage
    assert result.brief_kind == (
        None if stage == "COMPLETE" else _expected_brief_kind(stage)
    )
    assert result.last_completed_stage == expected_last_completed
    assert result.operations == _expected_prefix(stage)
    if stage == "COMPLETE":
        assert result.problem is None
    else:
        assert result.problem is not None
        assert set(result.problem) == {"status", "type", "title"}
    assert "营销内容" not in repr(result)
    assert "小红书内容" not in repr(result)


def test_legacy_five_gate_vector_collapses_post_confirm_checkpoints() -> None:
    results = {stage: _Driver(stage).run() for stage in ALL_STAGES}
    compatible = {
        stage
        for stage, result in results.items()
        if all(
            result.legacy_gate_vector[name] == expected
            for name, expected in HISTORICAL_GATES.items()
        )
    }

    assert compatible == {
        "PREVIEW_MARKETING",
        "SNAPSHOT_MARKETING",
        "DOWNLOAD_MARKETING",
        "PREVIEW_XIAOHONGSHU",
        "SNAPSHOT_XIAOHONGSHU",
        "DOWNLOAD_XIAOHONGSHU",
        "DISTINCT_SNAPSHOT_IDS",
    }
    assert len(compatible) == 7
    assert all(results[stage].failed_stage == stage for stage in compatible)
    assert all(
        results[stage].last_completed_stage
        == _expected_last_completed(cast(Stage, stage))
        for stage in compatible
    )
