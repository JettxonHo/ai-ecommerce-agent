"""Provider-free and opt-in PostgreSQL/FastAPI P2 lifecycle coverage."""

# FastAPI/Starlette's TestClient and pytest_socket's accepted AF_UNIX adapter
# are untyped framework boundaries in this integration test.
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportPrivateUsage=false, reportUnusedFunction=false, reportCallIssue=false

from __future__ import annotations

import os
import socket
import warnings
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import NoReturn, Protocol, cast

import pytest
from fastapi import FastAPI
from pytest_socket import SocketBlockedError, _true_socket
from sqlalchemy import Engine
from starlette.exceptions import StarletteDeprecationWarning

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest,
    ModelCallResult,
)
from ai_ecommerce_agent.bootstrap import pilot_p2
from ai_ecommerce_agent.bootstrap.deterministic_result_postgres import (
    DeterministicResultPostgresComposition,
)
from ai_ecommerce_agent.entrypoints.http import FixedWorkspaceHttpConfig
from ai_ecommerce_agent.platform.model_runtime.deepseek._cost_gate import (
    DEEPSEEK_P2_RESERVATION_MICRO_USD,
    DEEPSEEK_PRICING_RECORD,
)
from ai_ecommerce_agent.platform.postgres import PostgresEngineConfig

pytestmark = pytest.mark.integration

_RUN_POSTGRES = os.environ.get("MVP0_RUN_TASK_HTTP_POSTGRES") == "1"
_DATABASE_URL_ENV = "MVP0_TASK_HTTP_DATABASE_URL"
_SCHEMA = "mvp0_p2_postgres_composition"
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
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


class _HttpResponse(Protocol):
    status_code: int
    content: bytes
    text: str

    def json(self) -> object: ...


class _HttpClient(Protocol):
    def __enter__(self) -> _HttpClient: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None: ...

    def post(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        json: object | None = None,
    ) -> _HttpResponse: ...

    def put(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        json: object | None = None,
    ) -> _HttpResponse: ...

    def get(self, url: str) -> _HttpResponse: ...


def _http_client(application: FastAPI) -> _HttpClient:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", StarletteDeprecationWarning)
        from fastapi.testclient import TestClient

    return cast(_HttpClient, TestClient(application))


@pytest.fixture(autouse=True)
def _allow_local_testclient_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    """Permit TestClient's local Unix socketpair, but keep TCP blocked."""

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
            raise SocketBlockedError("TCP/network socket blocked")

    monkeypatch.setattr(socket, "socket", LocalSocket)


def _json_object(response: _HttpResponse) -> dict[str, object]:
    payload = response.json()
    if not isinstance(payload, Mapping):
        raise AssertionError("expected JSON object")
    payload_values = cast(Mapping[object, object], payload)
    result: dict[str, object] = {}
    for key, value in payload_values.items():
        if type(key) is not str:
            raise AssertionError("JSON object key must be a string")
        result[key] = value
    return result


def _json_string(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if type(value) is not str:
        raise AssertionError(f"{key} must be a string")
    return value


def _json_int(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if type(value) is not int:
        raise AssertionError(f"{key} must be an int")
    return value


def _json_mapping(payload: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"{key} must be an object")
    return cast(Mapping[str, object], value)


def _json_list(payload: Mapping[str, object], key: str) -> list[object]:
    value = payload.get(key)
    if type(value) is not list:
        raise AssertionError(f"{key} must be a list")
    return cast(list[object], value)


@dataclass
class _FakeParticipant:
    application: object
    close_calls: int = 0

    def close(self) -> None:
        self.close_calls += 1


@dataclass
class _FakeResultParticipant(_FakeParticipant):
    export_application: object = object()
    coordinator: object = object()


@pytest.fixture(scope="module")
def postgres_engine() -> Iterator[Engine]:
    """Guarded current-head schema lifecycle; never starts a database here."""

    if not _RUN_POSTGRES:
        pytest.skip(
            "set MVP0_RUN_TASK_HTTP_POSTGRES=1 for the opt-in P2 PostgreSQL lifecycle"
        )
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import text

    from ai_ecommerce_agent.platform.postgres import create_postgres_engine

    database_url = os.environ.get(_DATABASE_URL_ENV, "").strip()
    if not database_url:
        pytest.skip("MVP0_TASK_HTTP_DATABASE_URL is required for the opt-in lifecycle")
    engine = create_postgres_engine(
        PostgresEngineConfig(
            database_url=database_url,
            pool_size=4,
            max_overflow=0,
            pool_timeout=5,
        )
    )
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{_SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA "{_SCHEMA}"'))
    config = Config(str(_BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.set_main_option("business_schema", _SCHEMA)
    config.set_main_option("version_table_schema", _SCHEMA)
    try:
        command.upgrade(config, "head")
        yield engine
    finally:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{_SCHEMA}" CASCADE'))
        engine.dispose()


def test_p2_postgres_composition_is_lazy_and_owns_existing_seams(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    composition_calls = {
        "task": 0,
        "primary": 0,
        "result": 0,
        "http": 0,
        "runtime": 0,
    }
    participants: list[_FakeParticipant] = []
    applications: list[dict[str, object]] = []

    def fake_task(_config: PostgresEngineConfig, *, schema: str) -> _FakeParticipant:
        composition_calls["task"] += 1
        participant = _FakeParticipant(application=object())
        participants.append(participant)
        assert schema == "p2"
        return participant

    def fake_primary(_config: PostgresEngineConfig, *, schema: str) -> _FakeParticipant:
        composition_calls["primary"] += 1
        participant = _FakeParticipant(application=object())
        participants.append(participant)
        assert schema == "p2"
        return participant

    def fake_result(
        _config: PostgresEngineConfig,
        *,
        schema: str,
        coordinator: object,
    ) -> _FakeResultParticipant:
        composition_calls["result"] += 1
        participant = _FakeResultParticipant(
            application=object(),
            export_application=object(),
            coordinator=coordinator,
        )
        participants.append(participant)
        assert schema == "p2"
        return participant

    def fake_http(**kwargs: object) -> object:
        composition_calls["http"] += 1
        applications.append(kwargs)
        return object()

    def never_runtime(
        _requests: tuple[ModelCallRequest, ...], _payloads: tuple[str, ...]
    ) -> NoReturn:
        composition_calls["runtime"] += 1
        raise AssertionError("runtime factory must remain lazy during composition")

    monkeypatch.setattr(pilot_p2, "compose_task_management_postgres", fake_task)
    monkeypatch.setattr(pilot_p2, "compose_primary_input_postgres", fake_primary)
    monkeypatch.setattr(pilot_p2, "compose_deterministic_result_postgres", fake_result)
    monkeypatch.setattr(pilot_p2, "create_task_http_application", fake_http)
    monkeypatch.setattr(pilot_p2, "_create_deepseek_runtime", never_runtime)

    postgres_config = PostgresEngineConfig(
        "postgresql+psycopg://user:password@127.0.0.1/p2"
    )
    http_config = FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174")
    first = pilot_p2.compose_pilot_p2_postgres(
        postgres_config,
        http_config,
        schema="p2",
        sample_id="P01",
        attempt_id="P2-P01-A1",
        owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
        pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
    )

    assert composition_calls == {
        "task": 1,
        "primary": 1,
        "result": 1,
        "http": 1,
        "runtime": 0,
    }
    assert first.application is not None
    assert first.coordinator is applications[0]["pipeline_coordinator"]
    assert applications[0]["task_application"] is first.task.application
    assert (
        applications[0]["primary_input_application"] is first.primary_input.application
    )
    assert applications[0]["result_application"] is first.result.application
    assert applications[0]["export_application"] is first.result.export_application

    second = pilot_p2.compose_pilot_p2_postgres(
        postgres_config,
        http_config,
        schema="p2",
        owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
        pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
    )
    assert composition_calls["runtime"] == 0
    first.close()
    first.close()
    second.close()
    assert all(participant.close_calls == 1 for participant in participants)


def test_p2_postgres_close_attempts_every_owned_participant_after_primary_error() -> (
    None
):
    class _RaisingParticipant:
        def __init__(self, message: str = "primary-close") -> None:
            self.calls = 0
            self.message = message

        def close(self) -> None:
            self.calls += 1
            raise RuntimeError(self.message)

    class _ClosableParticipant:
        def __init__(self) -> None:
            self.calls = 0

        def close(self) -> None:
            self.calls += 1

    coordinator = _RaisingParticipant()
    result = _ClosableParticipant()
    primary = _ClosableParticipant()
    task = _ClosableParticipant()
    composition = pilot_p2.PilotP2PostgresComposition(
        application=object(),
        task=task,  # type: ignore[arg-type]
        primary_input=primary,  # type: ignore[arg-type]
        result=result,  # type: ignore[arg-type]
        coordinator=coordinator,  # type: ignore[arg-type]
    )

    with pytest.raises(RuntimeError, match="primary-close"):
        composition.close()
    assert coordinator.calls == 1
    assert result.calls == 1
    assert primary.calls == 1
    assert task.calls == 1
    composition.close()
    assert coordinator.calls == 1
    assert result.calls == 1
    assert primary.calls == 1
    assert task.calls == 1


def test_result_participant_close_attempts_export_after_application_error() -> None:
    class _RaisingParticipant:
        def __init__(self) -> None:
            self.calls = 0

        def close(self) -> None:
            self.calls += 1
            raise RuntimeError("result-close")

    class _ClosableParticipant:
        def __init__(self) -> None:
            self.calls = 0

        def close(self) -> None:
            self.calls += 1

    application = _RaisingParticipant()
    export_application = _ClosableParticipant()
    participant = DeterministicResultPostgresComposition(
        engine=object(),  # type: ignore[arg-type]
        application=application,  # type: ignore[arg-type]
        export_application=export_application,
        coordinator=object(),  # type: ignore[arg-type]
    )
    with pytest.raises(RuntimeError, match="result-close"):
        participant.close()
    assert application.calls == 1
    assert export_application.calls == 1


@pytest.mark.parametrize("brief_kind", ("marketing", "xiaohongshu"))
@pytest.mark.skipif(
    not _RUN_POSTGRES,
    reason="set MVP0_RUN_TASK_HTTP_POSTGRES=1 for the opt-in P2 PostgreSQL lifecycle",
)
def test_p2_postgres_current_head_lifecycle_uses_real_ids_and_export_bytes(
    postgres_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    brief_kind: str,
) -> None:
    from ai_ecommerce_agent.orchestration.deterministic_pipeline import (
        build_scripted_runtime,
    )
    from ai_ecommerce_agent.orchestration.pilot_attempt_artifact import (
        CaptureExport,
        ExportContentReference,
        ExportVersionReference,
        FinalDisposition,
        FinalizationCost,
        FinalizationExecution,
        FinalizationGates,
        FinalizeAttempt,
        PilotAttemptArtifacts,
        RecordReview,
        RecordRun,
        ReserveAttempt,
        ReviewDimension,
    )

    class _RecordingRuntime:
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

    factory_calls = 0
    runtimes: list[_RecordingRuntime] = []

    def fake_create(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> _RecordingRuntime:
        nonlocal factory_calls
        factory_calls += 1
        runtime = _RecordingRuntime(requests, payloads)
        runtimes.append(runtime)
        return runtime

    monkeypatch.setattr(pilot_p2, "_create_deepseek_runtime", fake_create)
    database_url = os.environ[_DATABASE_URL_ENV]
    composition = pilot_p2.compose_pilot_p2_postgres(
        PostgresEngineConfig(database_url=database_url, pool_size=2, max_overflow=0),
        FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
        schema=_SCHEMA,
        owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
        pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
    )
    assert factory_calls == 0
    task_body = {
        "taskName": f"P2 PostgreSQL {brief_kind}",
        "productCategory": "Power bank",
        "promotionGoal": "Product launch",
    }
    with _http_client(composition.application) as client:
        created = client.post(
            "/api/v1/tasks",
            headers={"Idempotency-Key": f"p2-task-{brief_kind}"},
            json=task_body,
        )
        created_body = _json_object(created)
        task_id = _json_string(created_body, "taskId")
        saved = client.put(
            f"/api/v1/tasks/{task_id}/primary-input",
            json={
                "inputKind": "pasted_text",
                "fileName": None,
                "content": P01_SANITIZED_INPUT,
            },
        )
        saved_body = _json_object(saved)
        generated = client.post(
            f"/api/v1/tasks/{task_id}/commands/generate-result",
            headers={"Idempotency-Key": f"p2-generate-{brief_kind}"},
            json={"expectedInputRevision": _json_int(saved_body, "inputRevision")},
        )
        generated_body = _json_object(generated)
        current = client.get(f"/api/v1/tasks/{task_id}/current-result")
    assert created.status_code == 201
    assert saved.status_code == 200
    assert generated.status_code == 201
    assert _json_string(generated_body, "status") == "awaiting_review"
    assert _json_object(current) == generated_body
    result_revision = _json_int(generated_body, "resultRevision")
    task_revision = _json_int(created_body, "revision")
    assert factory_calls == 1
    assert len(runtimes) == 1
    assert [
        request.identity.model_call_id.value for request in runtimes[0].requests
    ] == [f"P2-P01-A1-stage-{index}" for index in range(1, 6)]

    composition.close()
    recomposed = pilot_p2.compose_pilot_p2_postgres(
        PostgresEngineConfig(database_url=database_url, pool_size=2, max_overflow=0),
        FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
        schema=_SCHEMA,
        owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
        pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
    )
    assert factory_calls == 1
    with _http_client(recomposed.application) as client:
        reloaded = client.get(f"/api/v1/tasks/{task_id}/current-result")
        confirmed = client.post(
            f"/api/v1/tasks/{task_id}/commands/confirm-current-result",
            headers={"Idempotency-Key": f"p2-confirm-{brief_kind}"},
            json={
                "expectedResultRevision": result_revision,
                "marketingCoreMessage": "Confirmed product message",
                "xiaohongshuTitleDirection": "Confirmed title direction",
            },
        )
        preview = client.post(
            f"/api/v1/tasks/{task_id}/export-previews",
            json={"briefKind": brief_kind},
        )
        preview_body = _json_object(preview)
        snapshot = client.post(
            "/api/v1/export-snapshots",
            headers={"Idempotency-Key": f"p2-export-{brief_kind}"},
            json={"basis": _json_mapping(preview_body, "basis")},
        )
        snapshot_body = _json_object(snapshot)
        downloaded = client.get(_json_string(snapshot_body, "contentLocation"))
    assert reloaded.status_code == 200
    reloaded_body = _json_object(reloaded)
    assert _json_int(reloaded_body, "resultRevision") == result_revision
    assert confirmed.status_code == 201
    assert preview.status_code == 200
    assert snapshot.status_code == 201
    assert downloaded.status_code == 200
    assert downloaded.content.decode("utf-8").endswith("\n")
    assert factory_calls == 1

    artifact_parent = tmp_path / f"pilot-artifacts-{brief_kind}"
    artifact_parent.mkdir()
    artifact_root = artifact_parent / "p2" / "P01" / "P2-P01-A1"
    artifacts = PilotAttemptArtifacts(
        Path(__file__).resolve().parents[3], artifact_parent
    )
    artifacts.apply(ReserveAttempt(artifact_root))
    result_id = f"{task_id}:r{result_revision}"
    call_ids = tuple(f"P2-P01-A1-stage-{index}" for index in range(1, 6))
    artifacts.apply(
        RecordRun(
            task_id=task_id,
            task_revision=task_revision,
            result_id=result_id,
            result_revision=result_revision,
            provider_id="deepseek",
            api_family="chat_completions",
            configured_model_id="deepseek-v4-pro",
            resolved_model_id="deepseek-v4-pro",
            pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
            call_count=5,
            calls=tuple(
                {"model_call_id": call_id, "latency_ms": 0} for call_id in call_ids
            ),
            gates={
                "schema": True,
                "domain": True,
                "persistence": True,
                "export": True,
            },
            cost={
                "reserved_micro_usd": DEEPSEEK_P2_RESERVATION_MICRO_USD,
                "actual_micro_usd": 0,
            },
        )
    )
    brief_version = _json_mapping(snapshot_body, "briefVersion")
    upstream_versions = tuple(
        ExportVersionReference(
            _json_string(item, "resourceVersionId"),
            _json_int(item, "versionNumber"),
        )
        for item in (
            cast(Mapping[str, object], value)
            for value in _json_list(snapshot_body, "upstreamVersions")
        )
    )
    filename = (
        "marketing-brief.md" if brief_kind == "marketing" else "xiaohongshu-brief.md"
    )
    content_reference = ExportContentReference("local_relative", f"exports/{filename}")
    artifacts.apply(
        CaptureExport(
            task_id=task_id,
            task_revision=task_revision,
            result_id=result_id,
            result_revision=result_revision,
            export_snapshot_id=_json_string(snapshot_body, "exportSnapshotId"),
            brief_kind=brief_kind,
            brief_version=ExportVersionReference(
                _json_string(brief_version, "resourceVersionId"),
                _json_int(brief_version, "versionNumber"),
            ),
            upstream_versions=upstream_versions,
            exported_at=_json_string(snapshot_body, "exportedAt"),
            file_name=filename,
            server_file_name=_json_string(snapshot_body, "fileName"),
            template_version=_json_string(snapshot_body, "templateVersion"),
            media_type=_json_string(snapshot_body, "mediaType"),
            content_reference=content_reference,
            content_bytes=downloaded.content,
        )
    )
    dimensions = tuple(
        ReviewDimension(
            name,
            "PASS"
            if name != "xiaohongshu_consistency" or brief_kind == "xiaohongshu"
            else "NOT_APPLICABLE",
            name != "xiaohongshu_consistency" or brief_kind == "xiaohongshu",
        )
        for name in (
            "product_fact_correctness",
            "mandatory_messages",
            "prohibited_claims",
            "fabrication_misleading_content",
            "marketing_brief_usability",
            "xiaohongshu_consistency",
            "markdown_delivery",
        )
    )
    reviewed_at = datetime.now(UTC)
    review = RecordReview(
        task_id=task_id,
        task_revision=task_revision,
        result_id=result_id,
        result_revision=result_revision,
        captured_export_snapshot_ids=(_json_string(snapshot_body, "exportSnapshotId"),),
        reviewed_at=reviewed_at,
        dimensions=dimensions,
        overall="APPROVED",
        rationale="approved_all_applicable_critical_dimensions_pass",
    )
    artifacts.apply(review)
    outcome = artifacts.apply(
        FinalizeAttempt(
            task_id=task_id,
            task_revision=task_revision,
            result_id=result_id,
            result_revision=result_revision,
            outcome=FinalDisposition.PASS,
            reason_code="qualifying_approved_export",
            approved_review_id=review.review_id,
            selected_export_snapshot_ids=(
                _json_string(snapshot_body, "exportSnapshotId"),
            ),
            automated_gates=FinalizationGates(),
            cost=FinalizationCost(
                actual_micro_usd=0,
                owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
                reservation_ref=DEEPSEEK_PRICING_RECORD.record_id,
            ),
            execution=FinalizationExecution(),
        )
    )
    assert outcome is not None
    assert outcome["outcome"] == "PASS"
    recomposed.close()


@pytest.mark.skipif(
    not _RUN_POSTGRES,
    reason="set MVP0_RUN_TASK_HTTP_POSTGRES=1 for the opt-in P2 PostgreSQL lifecycle",
)
def test_p2_postgres_http_rejects_wrong_frozen_identity_before_runtime(
    postgres_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Persisted content mismatches fail before cost admission or runtime calls."""

    from ai_ecommerce_agent.orchestration.deterministic_pipeline import (
        build_scripted_runtime,
    )

    factory_calls = 0

    class _RecordingRuntime:
        def __init__(
            self,
            requests: tuple[ModelCallRequest, ...],
            payloads: tuple[str, ...],
        ) -> None:
            self._delegate = build_scripted_runtime(requests, payloads)

        def execute(self, request: ModelCallRequest) -> ModelCallResult:
            return self._delegate.execute(request)

    def fake_create(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> _RecordingRuntime:
        nonlocal factory_calls
        factory_calls += 1
        return _RecordingRuntime(requests, payloads)

    monkeypatch.setattr(pilot_p2, "_create_deepseek_runtime", fake_create)
    database_url = os.environ[_DATABASE_URL_ENV]
    composition = pilot_p2.compose_pilot_p2_postgres(
        PostgresEngineConfig(database_url=database_url, pool_size=2, max_overflow=0),
        FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
        schema=_SCHEMA,
        owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
        pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
    )
    invalid_input = P01_SANITIZED_INPUT.replace(
        "product: Anker Nano Power Bank", "product: Not The Admitted Product"
    )
    try:
        with _http_client(composition.application) as client:
            created = client.post(
                "/api/v1/tasks",
                headers={"Idempotency-Key": "p2-invalid-task"},
                json={
                    "taskName": "P2 invalid identity",
                    "productCategory": "Power bank",
                    "promotionGoal": "Product launch",
                },
            )
            created_body = _json_object(created)
            task_id = _json_string(created_body, "taskId")
            saved = client.put(
                f"/api/v1/tasks/{task_id}/primary-input",
                json={
                    "inputKind": "pasted_text",
                    "fileName": None,
                    "content": invalid_input,
                },
            )
            saved_body = _json_object(saved)
            generated = client.post(
                f"/api/v1/tasks/{task_id}/commands/generate-result",
                headers={"Idempotency-Key": "test"},
                json={"expectedInputRevision": _json_int(saved_body, "inputRevision")},
            )
            current = client.get(f"/api/v1/tasks/{task_id}/current-result")
        assert created.status_code == 201
        assert saved.status_code == 200
        assert generated.status_code >= 400
        assert current.status_code == 404
        assert factory_calls == 0
    finally:
        composition.close()


@pytest.mark.skipif(
    not _RUN_POSTGRES,
    reason="set MVP0_RUN_TASK_HTTP_POSTGRES=1 for the opt-in P2 operator lifecycle",
)
def test_p2_operator_binder_drives_full_provider_free_postgres_lifecycle(
    postgres_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The production binder owns Start, resume, review and finalization."""

    del postgres_engine
    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import (
        ConfirmAndCapture,
        FinalizeAttempt,
        PilotP2Operator,
        StartAttempt,
        SubmitHumanReview,
    )
    from ai_ecommerce_agent.orchestration.deterministic_pipeline import (
        build_scripted_runtime,
    )

    class _RecordingRuntime:
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

    runtimes: list[_RecordingRuntime] = []

    def fake_create(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> _RecordingRuntime:
        runtime = _RecordingRuntime(requests, payloads)
        runtimes.append(runtime)
        return runtime

    monkeypatch.setattr(pilot_p2, "_create_deepseek_runtime", fake_create)
    database_url = os.environ[_DATABASE_URL_ENV]
    inputs_root = tmp_path / "operator-inputs"
    inputs_root.mkdir()
    input_path = inputs_root / "p01-public.txt"
    input_path.write_text(P01_SANITIZED_INPUT, encoding="utf-8")
    artifact_parent = tmp_path / "operator-artifacts"
    artifact_parent.mkdir()
    artifact_root = artifact_parent / "p2" / "P01" / "P2-P01-A1"
    repository_root = Path(__file__).resolve().parents[3]
    operator = PilotP2Operator(
        repository_root=repository_root,
        approved_inputs_root=inputs_root,
        approved_artifact_parent=artifact_parent,
        postgres_config=PostgresEngineConfig(
            database_url=database_url,
            pool_size=2,
            max_overflow=0,
        ),
        http_config=FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
        schema=_SCHEMA,
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
    reviewed = operator.apply(SubmitHumanReview(overall="APPROVED"))
    export_id = str(resumed.exports[0]["export_snapshot_id"])
    assert reviewed.review_record is not None
    review_record = reviewed.review_record
    finalized = operator.apply(
        FinalizeAttempt(
            outcome="PASS",
            reason_code="qualifying_approved_export",
            approved_review_id=str(review_record["review_id"]),
            selected_export_snapshot_ids=(export_id,),
        )
    )

    assert started.status == "AWAITING_CONFIRMATION"
    assert started.task_id is not None
    assert started.result_id == f"{started.task_id}:r{started.result_revision}"
    assert started.attempted_call_count == 5
    assert started.completed_call_count == 5
    assert len(runtimes) == 1
    assert [
        request.identity.model_call_id.value for request in runtimes[0].requests
    ] == [f"P2-P01-A1-stage-{index}" for index in range(1, 6)]
    assert resumed.status == "PENDING_HUMAN_REVIEW"
    assert resumed.review_status == "PENDING"
    assert len(resumed.exports) == 1
    assert reviewed.review_status == "APPROVED"
    assert finalized.status == "PASS"
    assert finalized.outcome == "PASS"
    assert finalized.run is not None
    assert cast(Mapping[str, object], finalized.run["gates"])["export"] is False
    assert cast(Mapping[str, object], finalized.run["cost"])["actual_micro_usd"] in {
        "NOT_EXPOSED",
        "NOT_DERIVABLE",
    }
