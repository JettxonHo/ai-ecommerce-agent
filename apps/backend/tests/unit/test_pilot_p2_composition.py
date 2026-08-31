"""Provider-free P2 composition behavior for the first permitted sample."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, NoReturn, cast

import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest,
    ModelCallResult,
)
from ai_ecommerce_agent.bootstrap import pilot_p2
from ai_ecommerce_agent.entrypoints.http import FixedWorkspaceHttpConfig
from ai_ecommerce_agent.modules.customer_insight.application.skills import (
    customer_insight_analysis,
)
from ai_ecommerce_agent.modules.marketing_brief.application.skills import (
    marketing_brief_generation,
)
from ai_ecommerce_agent.modules.product_intake.application.skills import (
    product_intake_fact_extraction,
)
from ai_ecommerce_agent.modules.product_positioning.application.skills import (
    product_positioning,
)
from ai_ecommerce_agent.modules.xiaohongshu_adapter.application.skills import (
    xiaohongshu_brief_mapping,
)
from ai_ecommerce_agent.orchestration.deterministic_pipeline import (
    DeterministicPipelineCoordinator,
    PipelineInvocation,
    SpecFactory,
    build_scripted_runtime,
)
from ai_ecommerce_agent.platform.model_runtime.deepseek._cost_gate import (
    DEEPSEEK_P2_RESERVATION_MICRO_USD,
    DEEPSEEK_PRICING_RECORD,
    DeepSeekRuntimeAdmissionGate,
)
from ai_ecommerce_agent.platform.postgres import PostgresEngineConfig

pytestmark = pytest.mark.unit

P01_SANITIZED_INPUT = """\
sample_id: P01
attempt_id: P2-P01-A1
product: Anker Nano Power Bank
model/designation: A1259
color: Black Stone
variant: 42733233766550
category: A
sanitized permitted public product identity only
"""

SPEC_FACTORIES: tuple[SpecFactory, ...] = (
    product_intake_fact_extraction.product_intake_candidate_output_spec,
    customer_insight_analysis.customer_insight_candidate_output_spec,
    product_positioning.product_positioning_candidate_output_spec,
    marketing_brief_generation.marketing_brief_candidate_output_spec,
    xiaohongshu_brief_mapping.xiaohongshu_brief_candidate_output_spec,
)


def test_operator_binder_start_persists_observed_generation_without_review(
    tmp_path: Path,
) -> None:
    """The production operator seam owns one provider-free Start lifecycle."""

    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import (
        PilotP2Operator,
        StartAttempt,
    )

    inputs_root = tmp_path / "inputs"
    inputs_root.mkdir()
    input_path = inputs_root / "p01-public.txt"
    input_path.write_text(P01_SANITIZED_INPUT, encoding="utf-8")
    artifact_parent = tmp_path / "artifacts"
    artifact_parent.mkdir()
    artifact_root = artifact_parent / "p2" / "P01" / "P2-P01-A1"
    repository_root = Path(__file__).resolve().parents[4]

    class _FakeClient:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []
            self._input_revision = 0

        def create_task(self, *, idempotency_key: str) -> dict[str, object]:
            del idempotency_key
            self.calls.append(("POST", "/api/v1/tasks"))
            return {"taskId": "task-real-01", "revision": 1}

        def save_primary_input(
            self, *, task_id: str, content: str, file_name: str
        ) -> dict[str, object]:
            assert task_id == "task-real-01"
            assert content == P01_SANITIZED_INPUT
            assert file_name == input_path.name
            self.calls.append(("PUT", "/api/v1/tasks/task-real-01/primary-input"))
            self._input_revision = 1
            return {"taskId": task_id, "inputRevision": 1}

        def generate_result(
            self, *, task_id: str, input_revision: int, idempotency_key: str
        ) -> dict[str, object]:
            del idempotency_key
            assert task_id == "task-real-01"
            assert input_revision == self._input_revision
            self.calls.append(
                ("POST", "/api/v1/tasks/task-real-01/commands/generate-result")
            )
            return {
                "taskId": task_id,
                "resultRevision": 1,
                "inputRevision": input_revision,
                "status": "awaiting_review",
            }

    client = _FakeClient()

    class _FakeComposition:
        application = object()
        observation = {
            "attempted_count": 5,
            "completed_count": 5,
            "calls": tuple(
                {
                    "model_call_id": f"P2-P01-A1-stage-{index}",
                    "status": "COMPLETED",
                }
                for index in range(1, 6)
            ),
            "provider_id": "deepseek",
            "configured_model_id": "deepseek-v4-pro",
            "resolved_model_id": "deepseek-v4-pro",
        }
        close_calls = 0

        def close(self) -> None:
            self.close_calls += 1

    def compose_fake(*_args: object, **_kwargs: object) -> _FakeComposition:
        return _FakeComposition()

    operator = PilotP2Operator(
        repository_root=repository_root,
        approved_inputs_root=inputs_root,
        approved_artifact_parent=artifact_parent,
        postgres_config=PostgresEngineConfig(
            "postgresql+psycopg://user:password@127.0.0.1/p2"
        ),
        http_config=FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
        composition_factory=compose_fake,
        http_client_factory=lambda _application: client,
    )

    snapshot = operator.apply(
        StartAttempt(
            input_path=input_path,
            artifact_root=artifact_root,
            authorized_commit="cb77de2f96954a2d63ef00eead2f93bea1197649",
            owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
            pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
        )
    )

    assert snapshot.status == "AWAITING_CONFIRMATION"
    assert snapshot.task_id == "task-real-01"
    assert snapshot.result_id == "task-real-01:r1"
    assert snapshot.result_revision == 1
    assert snapshot.observation["attempted_count"] == 5
    assert snapshot.observation["completed_count"] == 5
    assert [method for method, _path in client.calls] == ["POST", "PUT", "POST"]
    assert snapshot.review_status == "PENDING"
    assert snapshot.outcome is None


def test_operator_binder_stage_three_failure_is_durable_and_terminal(
    tmp_path: Path,
) -> None:
    """A mid-stage failure records only safe attempted/completed evidence."""

    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import (
        PilotP2Operator,
        StartAttempt,
    )

    inputs_root = tmp_path / "inputs"
    inputs_root.mkdir()
    input_path = inputs_root / "p01-public.txt"
    input_path.write_text(P01_SANITIZED_INPUT, encoding="utf-8")
    artifact_parent = tmp_path / "artifacts"
    artifact_parent.mkdir()
    artifact_root = artifact_parent / "p2" / "P01" / "P2-P01-A1"
    repository_root = Path(__file__).resolve().parents[4]

    class _FailingClient:
        calls: list[tuple[str, str]] = []

        def create_task(self, *, idempotency_key: str) -> dict[str, object]:
            del idempotency_key
            self.calls.append(("POST", "/api/v1/tasks"))
            return {"taskId": "task-real-03", "revision": 1}

        def save_primary_input(
            self, *, task_id: str, content: str, file_name: str
        ) -> dict[str, object]:
            del content, file_name
            self.calls.append(("PUT", f"/api/v1/tasks/{task_id}/primary-input"))
            return {"taskId": task_id, "inputRevision": 1}

        def generate_result(
            self, *, task_id: str, input_revision: int, idempotency_key: str
        ) -> dict[str, object]:
            del task_id, input_revision, idempotency_key
            self.calls.append(("POST", "/commands/generate-result"))
            raise ValueError("synthetic stage three failure")

    client = _FailingClient()

    class _FailingComposition:
        application = object()
        observation = {
            "attempted_count": 3,
            "completed_count": 2,
            "calls": (
                {"model_call_id": "P2-P01-A1-stage-1", "status": "COMPLETED"},
                {"model_call_id": "P2-P01-A1-stage-2", "status": "COMPLETED"},
                {
                    "model_call_id": "P2-P01-A1-stage-3",
                    "status": "FAILED",
                    "error_category": "invalid_candidate",
                },
            ),
            "provider_id": "deepseek",
            "configured_model_id": "deepseek-v4-pro",
            "resolved_model_id": "deepseek-v4-pro",
        }

        def close(self) -> None:
            return None

    def compose_fake(*_args: object, **_kwargs: object) -> _FailingComposition:
        return _FailingComposition()

    snapshot = PilotP2Operator(
        repository_root=repository_root,
        approved_inputs_root=inputs_root,
        approved_artifact_parent=artifact_parent,
        postgres_config=PostgresEngineConfig(
            "postgresql+psycopg://user:password@127.0.0.1/p2"
        ),
        http_config=FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
        composition_factory=compose_fake,
        http_client_factory=lambda _application: client,
    ).apply(
        StartAttempt(
            input_path=input_path,
            artifact_root=artifact_root,
            authorized_commit="cb77de2f96954a2d63ef00eead2f93bea1197649",
            owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
            pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
        )
    )

    assert snapshot.status == "FAIL"
    assert snapshot.attempted_call_count == 3
    assert snapshot.completed_call_count == 2
    assert snapshot.run is not None
    assert snapshot.run["call_count"] == 3
    assert len(cast(Sequence[object], snapshot.run["calls"])) == 3
    assert snapshot.review_status == "PENDING"
    assert snapshot.exports == ()
    assert snapshot.outcome == "FAIL"
    assert snapshot.outcome_record is not None
    assert snapshot.outcome_record["reason_code"] == "execution_not_qualified"
    assert "traceback" not in str(snapshot.outcome_record).casefold()
    assert [method for method, _path in client.calls] == ["POST", "PUT", "POST"]


@pytest.mark.parametrize(
    ("field", "value", "expected_code"),
    (
        ("authorized_commit", "not-the-current-head", "git_head_mismatch"),
        ("owner_cap_micro_usd", None, "owner_cap_invalid"),
        (
            "owner_cap_micro_usd",
            DEEPSEEK_P2_RESERVATION_MICRO_USD - 1,
            "owner_cap_underfunded",
        ),
        ("pricing_record_id", "wrong-pricing-record", "pricing_record_mismatch"),
    ),
)
def test_operator_binder_rejects_controls_before_any_side_effect(
    tmp_path: Path,
    field: str,
    value: object,
    expected_code: str,
) -> None:
    """Every exact pre-call control rejects before artifact/PG/runtime/client."""

    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import (
        PilotP2Operator,
        PilotP2OperatorError,
        StartAttempt,
    )

    inputs_root = tmp_path / "inputs"
    inputs_root.mkdir()
    input_path = inputs_root / "p01-public.txt"
    input_path.write_text(P01_SANITIZED_INPUT, encoding="utf-8")
    artifact_parent = tmp_path / "artifacts"
    artifact_parent.mkdir()
    artifact_root = artifact_parent / "p2" / "P01" / "P2-P01-A1"
    repository_root = Path(__file__).resolve().parents[4]
    composition_calls = 0
    client_calls = 0

    def never_compose(*_args: object, **_kwargs: object) -> NoReturn:
        nonlocal composition_calls
        composition_calls += 1
        raise AssertionError("composition must not run after pre-call rejection")

    def never_client(_application: object) -> NoReturn:
        nonlocal client_calls
        client_calls += 1
        raise AssertionError("HTTP client must not run after pre-call rejection")

    start_kwargs: dict[str, object] = {
        "input_path": input_path,
        "artifact_root": artifact_root,
        "authorized_commit": "cb77de2f96954a2d63ef00eead2f93bea1197649",
        "owner_cap_micro_usd": DEEPSEEK_P2_RESERVATION_MICRO_USD,
        "pricing_record_id": DEEPSEEK_PRICING_RECORD.record_id,
    }
    start_kwargs[field] = value
    operator = PilotP2Operator(
        repository_root=repository_root,
        approved_inputs_root=inputs_root,
        approved_artifact_parent=artifact_parent,
        postgres_config=PostgresEngineConfig(
            "postgresql+psycopg://user:password@127.0.0.1/p2"
        ),
        http_config=FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
        composition_factory=never_compose,
        http_client_factory=never_client,
    )

    with pytest.raises(PilotP2OperatorError) as error:
        operator.apply(StartAttempt(**cast(Any, start_kwargs)))
    assert error.value.code == expected_code
    assert not artifact_root.exists()
    assert composition_calls == 0
    assert client_calls == 0


def test_operator_binder_rejects_wrong_artifact_root_before_composition(
    tmp_path: Path,
) -> None:
    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import (
        PilotP2Operator,
        PilotP2OperatorError,
        StartAttempt,
    )

    inputs_root = tmp_path / "inputs"
    inputs_root.mkdir()
    input_path = inputs_root / "p01-public.txt"
    input_path.write_text(P01_SANITIZED_INPUT, encoding="utf-8")
    artifact_parent = tmp_path / "artifacts"
    artifact_parent.mkdir()
    repository_root = Path(__file__).resolve().parents[4]
    composition_calls = 0

    def never_compose(*_args: object, **_kwargs: object) -> NoReturn:
        nonlocal composition_calls
        composition_calls += 1
        raise AssertionError("composition must not run after root rejection")

    operator = PilotP2Operator(
        repository_root=repository_root,
        approved_inputs_root=inputs_root,
        approved_artifact_parent=artifact_parent,
        postgres_config=PostgresEngineConfig(
            "postgresql+psycopg://user:password@127.0.0.1/p2"
        ),
        http_config=FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
        composition_factory=never_compose,
    )
    with pytest.raises(PilotP2OperatorError) as error:
        operator.apply(
            StartAttempt(
                input_path=input_path,
                artifact_root=artifact_parent / "wrong-root",
                authorized_commit="cb77de2f96954a2d63ef00eead2f93bea1197649",
                owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
                pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
            )
        )
    assert error.value.code == "artifact_root_invalid"
    assert composition_calls == 0


def test_operator_binder_rejects_mismatched_caller_head_even_with_authorized_commit(
    tmp_path: Path,
) -> None:
    """All supplied head assertions must agree with the repository reader."""

    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import (
        PilotP2Operator,
        PilotP2OperatorError,
        StartAttempt,
    )

    inputs_root = tmp_path / "inputs"
    inputs_root.mkdir()
    input_path = inputs_root / "p01-public.txt"
    input_path.write_text(P01_SANITIZED_INPUT, encoding="utf-8")
    artifact_parent = tmp_path / "artifacts"
    artifact_parent.mkdir()
    artifact_root = artifact_parent / "p2" / "P01" / "P2-P01-A1"
    repository_root = Path(__file__).resolve().parents[4]

    def never_compose(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("composition must not run before caller-head validation")

    operator = PilotP2Operator(
        repository_root=repository_root,
        approved_inputs_root=inputs_root,
        approved_artifact_parent=artifact_parent,
        postgres_config=PostgresEngineConfig(
            "postgresql+psycopg://user:password@127.0.0.1/p2"
        ),
        http_config=FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
        composition_factory=never_compose,
    )

    with pytest.raises(PilotP2OperatorError) as error:
        operator.apply(
            StartAttempt(
                input_path=input_path,
                artifact_root=artifact_root,
                authorized_commit="cb77de2f96954a2d63ef00eead2f93bea1197649",
                git_commit="caller-supplied-wrong-head",
                owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
                pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
            )
        )
    assert error.value.code == "git_head_mismatch"
    assert not artifact_root.exists()


def test_operator_binder_confirm_and_capture_recomposes_without_runtime_calls(
    tmp_path: Path,
) -> None:
    """Resume captures one immutable export and leaves Human Review pending."""

    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import (
        ConfirmAndCapture,
        PilotP2Operator,
        StartAttempt,
    )

    inputs_root = tmp_path / "inputs"
    inputs_root.mkdir()
    input_path = inputs_root / "p01-public.txt"
    input_path.write_text(P01_SANITIZED_INPUT, encoding="utf-8")
    artifact_parent = tmp_path / "artifacts"
    artifact_parent.mkdir()
    artifact_root = artifact_parent / "p2" / "P01" / "P2-P01-A1"
    repository_root = Path(__file__).resolve().parents[4]

    class _ResumeClient:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []

        def create_task(self, *, idempotency_key: str) -> dict[str, object]:
            del idempotency_key
            self.calls.append(("POST", "/api/v1/tasks"))
            return {"taskId": "task-resume-01", "revision": 1}

        def save_primary_input(
            self, *, task_id: str, content: str, file_name: str
        ) -> dict[str, object]:
            del content, file_name
            self.calls.append(("PUT", f"/api/v1/tasks/{task_id}/primary-input"))
            return {"taskId": task_id, "inputRevision": 1}

        def generate_result(
            self, *, task_id: str, input_revision: int, idempotency_key: str
        ) -> dict[str, object]:
            del input_revision, idempotency_key
            self.calls.append(
                ("POST", f"/api/v1/tasks/{task_id}/commands/generate-result")
            )
            return {
                "taskId": task_id,
                "resultRevision": 1,
                "inputRevision": 1,
                "status": "awaiting_review",
            }

        def current_result(self, *, task_id: str) -> dict[str, object]:
            self.calls.append(("GET", f"/api/v1/tasks/{task_id}/current-result"))
            return {"taskId": task_id, "resultRevision": 1, "status": "awaiting_review"}

        def confirm_result(
            self,
            *,
            task_id: str,
            result_revision: int,
            marketing_core_message: str,
            xiaohongshu_title_direction: str,
            idempotency_key: str,
        ) -> dict[str, object]:
            del (
                result_revision,
                marketing_core_message,
                xiaohongshu_title_direction,
                idempotency_key,
            )
            self.calls.append(
                ("POST", f"/api/v1/tasks/{task_id}/commands/confirm-current-result")
            )
            return {"taskId": task_id, "resultRevision": 1, "status": "confirmed"}

        def preview_export(self, *, task_id: str, brief_kind: str) -> dict[str, object]:
            self.calls.append(("POST", f"/api/v1/tasks/{task_id}/export-previews"))
            return {
                "basis": {
                    "taskId": task_id,
                    "taskRevision": 1,
                    "briefKind": brief_kind,
                    "briefVersion": {
                        "resourceKind": f"{brief_kind}_brief",
                        "resourceVersionId": "brief-resume-01",
                        "versionNumber": 1,
                    },
                    "upstreamVersions": [],
                    "hypotheses": [],
                    "evidenceLimitations": [],
                    "risks": [],
                },
                "templateVersion": "mvp0-markdown-v1",
                "fileName": f"task-{task_id}-{brief_kind}-v1-20260831T000000Z.md",
                "mediaType": "text/markdown; charset=utf-8",
            }

        def create_export_snapshot(
            self, *, basis: Mapping[str, object], idempotency_key: str
        ) -> dict[str, object]:
            del idempotency_key
            task_id = str(basis["taskId"])
            brief_kind = str(basis["briefKind"])
            self.calls.append(("POST", "/api/v1/export-snapshots"))
            return {
                "exportSnapshotId": f"export-{brief_kind}-resume-01",
                "taskId": task_id,
                "briefKind": brief_kind,
                "briefVersion": basis["briefVersion"],
                "upstreamVersions": [],
                "exportedAt": "2026-08-31T00:02:00Z",
                "fileName": f"task-{task_id}-{brief_kind}-v1-20260831T000000Z.md",
                "mediaType": "text/markdown; charset=utf-8",
                "contentLocation": (
                    f"/api/v1/export-snapshots/export-{brief_kind}-resume-01/content"
                ),
                "templateVersion": "mvp0-markdown-v1",
            }

        def download_export(self, *, content_location: str) -> bytes:
            self.calls.append(("GET", content_location))
            return b"# Marketing Brief\n"

    client = _ResumeClient()

    class _ResumeComposition:
        application = object()
        observation = {
            "attempted_count": 5,
            "completed_count": 5,
            "calls": tuple(
                {
                    "model_call_id": f"P2-P01-A1-stage-{index}",
                    "status": "COMPLETED",
                }
                for index in range(1, 6)
            ),
            "provider_id": "deepseek",
            "configured_model_id": "deepseek-v4-pro",
            "resolved_model_id": "deepseek-v4-pro",
        }

        def close(self) -> None:
            return None

    def compose_fake(*_args: object, **_kwargs: object) -> _ResumeComposition:
        return _ResumeComposition()

    operator = PilotP2Operator(
        repository_root=repository_root,
        approved_inputs_root=inputs_root,
        approved_artifact_parent=artifact_parent,
        postgres_config=PostgresEngineConfig(
            "postgresql+psycopg://user:password@127.0.0.1/p2"
        ),
        http_config=FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
        composition_factory=compose_fake,
        http_client_factory=lambda _application: client,
    )
    started = operator.apply(
        StartAttempt(
            input_path=input_path,
            artifact_root=artifact_root,
            authorized_commit="cb77de2f96954a2d63ef00eead2f93bea1197649",
            owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
            pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
        )
    )
    resumed = operator.apply(ConfirmAndCapture(brief_kinds=("marketing",)))

    assert started.status == "AWAITING_CONFIRMATION"
    assert resumed.status == "PENDING_HUMAN_REVIEW"
    assert resumed.review_status == "PENDING"
    assert resumed.outcome is None
    assert resumed.result_id == "task-resume-01:r1"
    assert resumed.exports[0]["export_snapshot_id"] == "export-marketing-resume-01"
    assert (
        artifact_root / "exports" / "marketing-brief.md"
    ).read_bytes() == b"# Marketing Brief\n"
    assert [method for method, _path in client.calls] == [
        "POST",
        "PUT",
        "POST",
        "GET",
        "POST",
        "POST",
        "POST",
        "GET",
    ]


def test_operator_binder_explicit_review_and_finalize_qualifies_unknown_actual_cost(
    tmp_path: Path,
) -> None:
    """PASS derives export qualification from sidecars, not run evidence."""

    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import (
        FinalizeAttempt,
        PilotP2Operator,
        SubmitHumanReview,
    )
    from ai_ecommerce_agent.orchestration.pilot_attempt_artifact import (
        CaptureExport,
        ExportContentReference,
        ExportVersionReference,
        PilotAttemptArtifacts,
        RecordRun,
        ReserveAttempt,
    )

    inputs_root = tmp_path / "inputs"
    inputs_root.mkdir()
    input_path = inputs_root / "p01-public.txt"
    input_path.write_text(P01_SANITIZED_INPUT, encoding="utf-8")
    artifact_parent = tmp_path / "artifacts"
    artifact_parent.mkdir()
    artifact_root = artifact_parent / "p2" / "P01" / "P2-P01-A1"
    repository_root = Path(__file__).resolve().parents[4]
    artifacts = PilotAttemptArtifacts(repository_root, artifact_parent)
    artifacts.apply(ReserveAttempt(artifact_root))
    task_id = "task-review-01"
    result_id = f"{task_id}:r1"
    artifacts.apply(
        RecordRun(
            task_id=task_id,
            task_revision=1,
            result_id=result_id,
            result_revision=1,
            provider_id="deepseek",
            api_family="chat_completions",
            configured_model_id="deepseek-v4-pro",
            resolved_model_id="deepseek-v4-pro",
            pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
            call_count=5,
            calls=tuple(
                {
                    "model_call_id": f"P2-P01-A1-stage-{index}",
                    "status": "COMPLETED",
                }
                for index in range(1, 6)
            ),
            gates={
                "schema": True,
                "domain": True,
                "persistence": True,
                # Export is absent until ConfirmAndCapture sidecars exist.
                "export": False,
            },
            cost={
                "reserved_micro_usd": DEEPSEEK_P2_RESERVATION_MICRO_USD,
                "actual_micro_usd": None,
            },
        )
    )
    artifacts.apply(
        CaptureExport(
            task_id=task_id,
            task_revision=1,
            result_id=result_id,
            result_revision=1,
            export_snapshot_id="export-review-01",
            brief_version=ExportVersionReference("brief-review-01", 1),
            content_reference=ExportContentReference(
                "local_relative", "exports/marketing-brief.md"
            ),
            content_bytes=b"# Marketing Brief\n",
        )
    )
    operator = PilotP2Operator(
        repository_root=repository_root,
        approved_inputs_root=inputs_root,
        approved_artifact_parent=artifact_parent,
        postgres_config=PostgresEngineConfig(
            "postgresql+psycopg://user:password@127.0.0.1/p2"
        ),
        http_config=FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
        owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
        pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
    )
    reviewed = operator.apply(SubmitHumanReview(overall="APPROVED"))
    finalized = operator.apply(
        FinalizeAttempt(
            outcome="PASS",
            reason_code="qualifying_approved_export",
            approved_review_id="review-P2-P01-A1",
            selected_export_snapshot_ids=("export-review-01",),
        )
    )

    assert reviewed.status == "REVIEW_SUBMITTED"
    assert reviewed.review_status == "APPROVED"
    assert finalized.status == "PASS"
    assert finalized.outcome == "PASS"
    assert finalized.run is not None
    assert cast(Mapping[str, object], finalized.run["gates"])["export"] is False
    assert (
        cast(Mapping[str, object], finalized.run["cost"])["actual_micro_usd"]
        == "NOT_EXPOSED"
    )


def test_operator_binder_rejected_review_finalizes_fail_without_auto_approval(
    tmp_path: Path,
) -> None:
    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import (
        FinalizeAttempt,
        PilotP2Operator,
        SubmitHumanReview,
    )
    from ai_ecommerce_agent.orchestration.pilot_attempt_artifact import (
        CaptureExport,
        ExportContentReference,
        ExportVersionReference,
        PilotAttemptArtifacts,
        RecordRun,
        ReserveAttempt,
        ReviewDimension,
    )

    inputs_root = tmp_path / "inputs"
    inputs_root.mkdir()
    artifact_parent = tmp_path / "artifacts"
    artifact_parent.mkdir()
    artifact_root = artifact_parent / "p2" / "P01" / "P2-P01-A1"
    repository_root = Path(__file__).resolve().parents[4]
    artifacts = PilotAttemptArtifacts(repository_root, artifact_parent)
    artifacts.apply(ReserveAttempt(artifact_root))
    task_id = "task-review-rejected"
    result_id = f"{task_id}:r1"
    artifacts.apply(
        RecordRun(
            task_id=task_id,
            task_revision=1,
            result_id=result_id,
            result_revision=1,
            pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
            call_count=5,
            calls=tuple(
                {
                    "model_call_id": f"P2-P01-A1-stage-{index}",
                    "status": "COMPLETED",
                }
                for index in range(1, 6)
            ),
            gates={
                "schema": True,
                "domain": True,
                "persistence": True,
                "export": False,
            },
            cost={
                "reserved_micro_usd": DEEPSEEK_P2_RESERVATION_MICRO_USD,
                "actual_micro_usd": None,
            },
        )
    )
    artifacts.apply(
        CaptureExport(
            task_id=task_id,
            task_revision=1,
            result_id=result_id,
            result_revision=1,
            export_snapshot_id="export-review-rejected",
            brief_version=ExportVersionReference("brief-review-rejected", 1),
            content_reference=ExportContentReference(
                "local_relative", "exports/marketing-brief.md"
            ),
            content_bytes=b"# Marketing Brief\n",
        )
    )
    operator = PilotP2Operator(
        repository_root=repository_root,
        approved_inputs_root=inputs_root,
        approved_artifact_parent=artifact_parent,
        postgres_config=PostgresEngineConfig(
            "postgresql+psycopg://user:password@127.0.0.1/p2"
        ),
        http_config=FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
        owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
        pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
    )
    rejected_dimensions = (
        ReviewDimension("product_fact_correctness", "FAIL", True),
        ReviewDimension("mandatory_messages", "PASS", True),
        ReviewDimension("prohibited_claims", "PASS", True),
        ReviewDimension("fabrication_misleading_content", "PASS", True),
        ReviewDimension("marketing_brief_usability", "PASS", True),
        ReviewDimension("xiaohongshu_consistency", "NOT_APPLICABLE", False),
        ReviewDimension("markdown_delivery", "PASS", True),
    )
    reviewed = operator.apply(
        SubmitHumanReview(
            overall="REJECTED",
            dimensions=rejected_dimensions,
            captured_export_snapshot_ids=("export-review-rejected",),
        )
    )
    finalized = operator.apply(
        FinalizeAttempt(
            outcome="FAIL",
            reason_code="review_rejected",
        )
    )

    assert reviewed.review_status == "REJECTED"
    assert finalized.status == "FAIL"
    assert finalized.outcome == "FAIL"
    assert finalized.outcome_record is not None
    assert finalized.outcome_record["reason_code"] == "review_rejected"


class _FakeDeepSeekRuntime:
    """Interface-shaped fake that records ordered calls without network I/O."""

    def __init__(
        self,
        requests: tuple[ModelCallRequest, ...],
        payloads: tuple[str, ...],
    ) -> None:
        self._delegate = build_scripted_runtime(requests, payloads)
        self.requests: list[ModelCallRequest] = []

    def execute(self, request: ModelCallRequest) -> ModelCallResult:
        self.requests.append(request)
        return self._delegate.execute(request)


def test_p2_p01_non_anchor_input_reaches_five_ordered_deepseek_calls() -> None:
    runtime: _FakeDeepSeekRuntime | None = None

    def runtime_factory(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> _FakeDeepSeekRuntime:
        nonlocal runtime
        runtime = _FakeDeepSeekRuntime(requests, payloads)
        return runtime

    cost_gate = DeepSeekRuntimeAdmissionGate(
        runtime_factory=runtime_factory,
        owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
        pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
    )

    result = DeterministicPipelineCoordinator(
        SPEC_FACTORIES,
        runtime_factory=cost_gate.runtime_factory,
        input_preflight=lambda _input_text: (),
        pipeline_invocation=PipelineInvocation(
            sample_id="P01",
            attempt_id="P2-P01-A1",
            context_assembly_version="pilot-p2-v1",
        ),
        runtime_admission_gate=cost_gate.authorize,
    ).generate(input_text=P01_SANITIZED_INPUT)

    assert result.status == "awaiting_review"
    assert result.missing_information == ()
    assert [name for name, _ in result.candidates] == [
        "productIntake",
        "customerInsight",
        "productPositioning",
        "marketingBrief",
        "xiaohongshuBrief",
    ]
    assert runtime is not None
    assert [request.identity.model_call_id.value for request in runtime.requests] == [
        "P2-P01-A1-stage-1",
        "P2-P01-A1-stage-2",
        "P2-P01-A1-stage-3",
        "P2-P01-A1-stage-4",
        "P2-P01-A1-stage-5",
    ]
    assert [
        request.execution_profile.execution_profile_id for request in runtime.requests
    ] == [
        "product_intake_v1",
        "customer_insight_v1",
        "product_positioning_v1",
        "marketing_brief_v1",
        "xiaohongshu_mapping_v1",
    ]
    assert [
        request.execution_profile.execution_profile_version
        for request in runtime.requests
    ] == ["v1", "v1", "v1", "v1", "v2"]
    assert [
        request.contract_versions.context_assembly_version
        for request in runtime.requests
    ] == ["pilot-p2-v1"] * 5
    assert all(
        P01_SANITIZED_INPUT == request.context.to_mapping()["primary_input"]
        for request in runtime.requests
    )
    assert all(
        request.context.to_mapping()["pipeline_invocation"]
        == {
            "sample_id": "P01",
            "attempt_id": "P2-P01-A1",
            "context_assembly_version": "pilot-p2-v1",
        }
        for request in runtime.requests
    )


def test_p2_bootstrap_is_lazy_and_runs_exact_deepseek_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory_calls = 0
    close_calls = 0
    runtime: _FakeDeepSeekRuntime | None = None

    class _ClosableFakeRuntime(_FakeDeepSeekRuntime):
        def close(self) -> None:
            nonlocal close_calls
            close_calls += 1

    def fake_create(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> _ClosableFakeRuntime:
        nonlocal factory_calls, runtime
        factory_calls += 1
        runtime = _ClosableFakeRuntime(requests, payloads)
        return runtime

    monkeypatch.setattr(pilot_p2, "_create_deepseek_runtime", fake_create)
    composition = pilot_p2.compose_pilot_p2_pipeline(
        sample_id="P01",
        attempt_id="P2-P01-A1",
        input_text=P01_SANITIZED_INPUT,
        owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
        pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
    )

    assert factory_calls == 0
    assert close_calls == 0
    result = composition.generate()

    assert result.status == "awaiting_review"
    assert result.missing_information == ()
    assert len(result.candidates) == 5
    assert factory_calls == 1
    assert close_calls == 1
    assert runtime is not None
    assert [request.identity.model_call_id.value for request in runtime.requests] == [
        "P2-P01-A1-stage-1",
        "P2-P01-A1-stage-2",
        "P2-P01-A1-stage-3",
        "P2-P01-A1-stage-4",
        "P2-P01-A1-stage-5",
    ]
    assert [
        request.contract_versions.context_assembly_version
        for request in runtime.requests
    ] == ["pilot-p2-v1"] * 5
    assert all(
        request.context.to_mapping()["pipeline_invocation"]
        == {
            "sample_id": "P01",
            "attempt_id": "P2-P01-A1",
            "context_assembly_version": "pilot-p2-v1",
        }
        for request in runtime.requests
    )


def test_p2_bootstrap_rejects_identity_or_cost_before_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory_calls = 0

    def never_create(
        _requests: tuple[ModelCallRequest, ...], _payloads: tuple[str, ...]
    ) -> NoReturn:
        nonlocal factory_calls
        factory_calls += 1
        raise AssertionError("DeepSeek factory must not run after bootstrap rejection")

    monkeypatch.setattr(pilot_p2, "_create_deepseek_runtime", never_create)
    invalid_inputs: tuple[tuple[str, str, str, int, str], ...] = (
        (
            "P02",
            "P2-P01-A1",
            P01_SANITIZED_INPUT,
            DEEPSEEK_P2_RESERVATION_MICRO_USD,
            DEEPSEEK_PRICING_RECORD.record_id,
        ),
        (
            "P01",
            "P2-P02-A1",
            P01_SANITIZED_INPUT,
            DEEPSEEK_P2_RESERVATION_MICRO_USD,
            DEEPSEEK_PRICING_RECORD.record_id,
        ),
        (
            "P01",
            "P2-P01-A1",
            P01_SANITIZED_INPUT,
            DEEPSEEK_P2_RESERVATION_MICRO_USD - 1,
            DEEPSEEK_PRICING_RECORD.record_id,
        ),
    )
    for (
        sample_id,
        attempt_id,
        input_text,
        owner_cap,
        pricing_record_id,
    ) in invalid_inputs:
        with pytest.raises((ValueError, TypeError)):
            pilot_p2.compose_pilot_p2_pipeline(
                sample_id=sample_id,
                attempt_id=attempt_id,
                input_text=input_text,
                owner_cap_micro_usd=owner_cap,
                pricing_record_id=pricing_record_id,
            )

    assert factory_calls == 0


@pytest.mark.parametrize(
    ("label", "wrong_line"),
    (
        ("product", "product: Anker Nano Power Bankx"),
        ("model", "model/designation: A1258"),
        ("color", "color: White"),
        ("variant", "variant: 42733233766551"),
        ("category", "category: B"),
    ),
)
def test_p2_rejects_wrong_frozen_product_identity_before_cost_gate(
    monkeypatch: pytest.MonkeyPatch, label: str, wrong_line: str
) -> None:
    """The P01 content contract is checked before any cost/runtime seam."""

    del label
    factory_calls = 0

    def never_create(
        _requests: tuple[ModelCallRequest, ...], _payloads: tuple[str, ...]
    ) -> NoReturn:
        nonlocal factory_calls
        factory_calls += 1
        raise AssertionError("runtime factory must not run for an identity mismatch")

    monkeypatch.setattr(pilot_p2, "_create_deepseek_runtime", never_create)
    input_text = P01_SANITIZED_INPUT
    original_line = next(
        line
        for line in input_text.splitlines()
        if line.split(":", 1)[0] in wrong_line.split(":", 1)[0]
    )
    invalid_input = input_text.replace(original_line, wrong_line)

    with pytest.raises(ValueError, match="P2 input identity"):
        pilot_p2.compose_pilot_p2_pipeline(
            sample_id="P01",
            attempt_id="P2-P01-A1",
            input_text=invalid_input,
            owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
            pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
        )

    assert factory_calls == 0


def test_non_pilot_scripted_coordinator_remains_valid() -> None:
    result = DeterministicPipelineCoordinator(
        SPEC_FACTORIES,
        runtime_factory=build_scripted_runtime,
        input_preflight=lambda _input_text: (),
    ).generate(input_text=P01_SANITIZED_INPUT)

    assert result.status == "awaiting_review"
    assert result.missing_information == ()
    assert len(result.candidates) == 5


def test_default_coordinator_keeps_anchor_preflight_for_non_anchor_p01() -> None:
    result = DeterministicPipelineCoordinator(SPEC_FACTORIES).generate(
        input_text=P01_SANITIZED_INPUT
    )

    assert result.status == "insufficient_input"
    assert result.candidates == ()


class _RuntimeAdmissionRejected(RuntimeError):
    """Safe fake rejection for the provider-admission seam."""


def test_p2_runtime_admission_rejects_before_factory_or_client() -> None:
    events: list[str] = []
    planned_request_counts: list[int] = []
    runtime_factory_calls = 0
    secret_resolution_calls = 0
    client_construction_calls = 0

    def runtime_admission_gate(requests: tuple[ModelCallRequest, ...]) -> None:
        events.append("runtime_admission_gate")
        planned_request_counts.append(len(requests))
        raise _RuntimeAdmissionRejected("P2 runtime admission rejected")

    def runtime_factory(
        _requests: tuple[ModelCallRequest, ...], _payloads: tuple[str, ...]
    ) -> NoReturn:
        nonlocal runtime_factory_calls, secret_resolution_calls
        nonlocal client_construction_calls
        runtime_factory_calls += 1
        secret_resolution_calls += 1
        client_construction_calls += 1
        raise AssertionError("runtime factory must not run after admission rejection")

    coordinator = DeterministicPipelineCoordinator(
        SPEC_FACTORIES,
        runtime_factory=runtime_factory,
        input_preflight=lambda _input_text: (),
        pipeline_invocation=PipelineInvocation(
            sample_id="P01",
            attempt_id="P2-P01-A1",
            context_assembly_version="pilot-p2-v1",
        ),
        runtime_admission_gate=runtime_admission_gate,
    )

    with pytest.raises(_RuntimeAdmissionRejected, match="P2 runtime admission"):
        coordinator.generate(input_text=P01_SANITIZED_INPUT)

    assert events == ["runtime_admission_gate"]
    assert planned_request_counts == [5]
    assert runtime_factory_calls == 0
    assert secret_resolution_calls == 0
    assert client_construction_calls == 0


def test_p2_missing_runtime_admission_fails_closed_before_factory_or_calls() -> None:
    runtime: _FakeDeepSeekRuntime | None = None
    runtime_factory_calls = 0

    def runtime_factory(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> _FakeDeepSeekRuntime:
        nonlocal runtime, runtime_factory_calls
        runtime_factory_calls += 1
        runtime = _FakeDeepSeekRuntime(requests, payloads)
        return runtime

    try:
        result = DeterministicPipelineCoordinator(
            SPEC_FACTORIES,
            runtime_factory=runtime_factory,
            input_preflight=lambda _input_text: (),
            pipeline_invocation=PipelineInvocation(
                sample_id="P01",
                attempt_id="P2-P01-A1",
                context_assembly_version="pilot-p2-v1",
            ),
        ).generate(input_text=P01_SANITIZED_INPUT)
    except Exception:
        completed_without_error = False
    else:
        completed_without_error = result.status == "awaiting_review"

    runtime_calls = 0 if runtime is None else len(runtime.requests)
    assert (completed_without_error, runtime_factory_calls, runtime_calls) == (
        False,
        0,
        0,
    )


def test_p2_composition_preserves_generation_error_when_runtime_close_also_fails() -> (
    None
):
    class _FailingCoordinator:
        def generate(self, *, input_text: str) -> object:
            del input_text
            raise RuntimeError("generation-primary")

    class _FailingRuntime:
        def close(self) -> None:
            raise RuntimeError("close-secondary")

    composition = pilot_p2.PilotP2Composition(
        sample_id="P01",
        attempt_id="P2-P01-A1",
        input_text=P01_SANITIZED_INPUT,
        _coordinator=_FailingCoordinator(),  # type: ignore[arg-type]
        _runtime_holder=[_FailingRuntime()],  # type: ignore[list-item]
    )
    with pytest.raises(RuntimeError, match="generation-primary"):
        composition.generate()
