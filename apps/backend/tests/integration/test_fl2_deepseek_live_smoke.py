"""One explicit DeepSeek Task-to-export smoke seam.

This module is an opt-in operator handoff only.  Provider credential
resolution stays inside the private adapter factory; this test module never
reads the credential environment variable or prints its value.
"""

# FastAPI/Starlette's TestClient is an untyped framework boundary in the
# accepted runtime tuple; this test focuses on the one operator-visible flow.
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportPrivateUsage=false, reportCallIssue=false

from __future__ import annotations

import os
import subprocess
import warnings
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, text
from sqlalchemy.engine import URL
from starlette.exceptions import StarletteDeprecationWarning

import ai_ecommerce_agent.platform.model_runtime as _runtime_package
from ai_ecommerce_agent.application.model_runtime import ModelCallRequest
from ai_ecommerce_agent.bootstrap.deterministic_result_postgres import (
    DeterministicResultPostgresComposition,
    compose_deterministic_result_postgres,
)
from ai_ecommerce_agent.entrypoints.http import (
    FixedWorkspaceHttpConfig,
    create_task_http_application,
)
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
from ai_ecommerce_agent.modules.source_evidence.application.primary_input_services import (  # noqa: E501
    PrimaryInputApplicationService,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.primary_input_uow import (  # noqa: E501
    PrimaryInputPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.task_management.application.services import (
    TaskManagementApplicationService,
)
from ai_ecommerce_agent.modules.task_management.infrastructure.uow import (
    TaskManagementPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.xiaohongshu_adapter.application.skills import (
    xiaohongshu_brief_mapping,
)
from ai_ecommerce_agent.orchestration.deterministic_pipeline import (
    DeterministicPipelineCoordinator,
)
from ai_ecommerce_agent.platform.model_runtime.deepseek._runtime import (
    DeepSeekModelRuntime,
    create_deepseek_runtime,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses._live_evidence import (
    serialize_live_smoke_evidence,
    write_live_smoke_evidence,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)
from fixtures.mvp0_loader import load_manifest

_runtime_package.__dict__.pop("deepseek", None)

warnings.filterwarnings("ignore", category=StarletteDeprecationWarning)
from fastapi.testclient import TestClient  # noqa: E402

pytestmark = [pytest.mark.integration, pytest.mark.live]

_RUN_DEEPSEEK = os.environ.get("RUN_DEEPSEEK_LIVE_SMOKE") == "1"
_RUN_POSTGRES = os.environ.get("MVP0_RUN_TASK_HTTP_POSTGRES") == "1"
if not (_RUN_DEEPSEEK and _RUN_POSTGRES):
    pytest.skip(
        "set both explicit DeepSeek and PostgreSQL live controls for this smoke",
        allow_module_level=True,
    )

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_REPOSITORY_ROOT = _BACKEND_ROOT.parents[1]
_SCHEMA = "mvp0_fl2_deepseek_live"
_URL_ENV = "MVP0_TASK_HTTP_DATABASE_URL"
_DEFAULT_URL = URL.create(
    "postgresql+psycopg",
    username="mvp0_business",
    password="mvp0_business_local_only",
    host="127.0.0.1",
    port=55432,
    database="ecommerce_business",
).render_as_string(hide_password=False)

_SPEC_FACTORIES = (
    product_intake_fact_extraction.product_intake_candidate_output_spec,
    customer_insight_analysis.customer_insight_candidate_output_spec,
    product_positioning.product_positioning_candidate_output_spec,
    marketing_brief_generation.marketing_brief_candidate_output_spec,
    xiaohongshu_brief_mapping.xiaohongshu_brief_candidate_output_spec,
)
_FALSE_GATES = {
    "validated_candidates": False,
    "confirmed_result": False,
    "marketing_export_immutable": False,
    "xiaohongshu_export_immutable": False,
    "downloads_utf8_no_bom_one_final_lf": False,
}


def _validated_commit() -> str:
    configured = os.environ.get("GIT_COMMIT", "").strip()
    if not configured:
        pytest.fail("the live smoke requires an operator-selected GIT_COMMIT")
    try:
        actual = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=_REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except Exception:
        pytest.fail("the live smoke could not verify the repository commit")
    if configured != actual:
        pytest.fail("GIT_COMMIT does not match the exact reviewed repository head")
    return configured


def _evidence_path() -> Path:
    configured = os.environ.get("FL2_DEEPSEEK_LIVE_EVIDENCE_PATH", "").strip()
    if not configured:
        pytest.fail("the live smoke requires an operator-selected evidence path")
    path = Path(configured).expanduser()
    if not path.is_absolute():
        pytest.fail("the live evidence path must be absolute")
    resolved = path.resolve()
    try:
        resolved.relative_to(_REPOSITORY_ROOT)
    except ValueError:
        pass
    else:
        pytest.fail("the live evidence path must be outside tracked source")
    if resolved.exists():
        pytest.fail("the live evidence path must not already exist")
    return resolved


_COMMIT = _validated_commit()
_EVIDENCE_PATH = _evidence_path()


def _database_url() -> str:
    return os.environ.get(_URL_ENV, _DEFAULT_URL).strip()


def _alembic_config(database_url: str) -> Config:
    config = Config(str(_BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.set_main_option("business_schema", _SCHEMA)
    config.set_main_option("version_table_schema", _SCHEMA)
    return config


@pytest.fixture(scope="module")
def live_runtime_preflight() -> Iterator[None]:
    """Resolve operator configuration before opening PostgreSQL."""

    runtime = create_deepseek_runtime()
    try:
        yield
    finally:
        runtime.close()


@pytest.fixture(scope="module")
def postgres_engine(live_runtime_preflight: None) -> Iterator[Engine]:
    """Own one isolated schema, migrate it, and remove it afterwards."""

    del live_runtime_preflight
    database_url = _database_url()
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
    try:
        command.upgrade(_alembic_config(database_url), "head")
        yield engine
    finally:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{_SCHEMA}" CASCADE'))
        engine.dispose()


def _fixture_input() -> str:
    fixture = load_manifest().fixture("fixture-sufficient-v1")
    return "\n\n".join(
        path.read_text(encoding="utf-8") for path in fixture.source_paths
    )


def _result_client(
    engine: Engine,
    runtimes: list[DeepSeekModelRuntime],
) -> tuple[TestClient, DeterministicResultPostgresComposition]:
    task_factory = TaskManagementPostgresUnitOfWorkFactory.from_engine(
        engine, schema=_SCHEMA
    )
    input_factory = PrimaryInputPostgresUnitOfWorkFactory.from_engine(
        engine, schema=_SCHEMA
    )

    def runtime_factory(
        _requests: tuple[ModelCallRequest, ...], _payloads: tuple[str, ...]
    ) -> DeepSeekModelRuntime:
        runtime = create_deepseek_runtime()
        runtimes.append(runtime)
        return runtime

    coordinator = DeterministicPipelineCoordinator(
        _SPEC_FACTORIES,
        runtime_factory=runtime_factory,
    )
    composition = compose_deterministic_result_postgres(
        PostgresEngineConfig(
            database_url=_database_url(),
            pool_size=2,
            max_overflow=0,
            pool_timeout=5,
        ),
        schema=_SCHEMA,
        coordinator=coordinator,
    )
    return (
        TestClient(
            create_task_http_application(
                config=FixedWorkspaceHttpConfig(
                    workspace_id="workspace-demo",
                    workbench_origin="http://127.0.0.1:5173",
                ),
                task_application=TaskManagementApplicationService(task_factory),
                primary_input_application=PrimaryInputApplicationService(input_factory),
                result_application=composition.application,
                pipeline_coordinator=composition.coordinator,
                export_application=composition.export_application,
            )
        ),
        composition,
    )


def _write_evidence(
    *,
    started_at: datetime,
    started_clock: float,
    disposition: str,
    reason: str,
    runtimes: list[DeepSeekModelRuntime],
    behavior_gates: dict[str, bool],
) -> None:
    metadata = tuple(item for runtime in runtimes for item in runtime.metadata_records)
    serialized = serialize_live_smoke_evidence(
        commit=_COMMIT,
        started_at_utc=started_at.isoformat().replace("+00:00", "Z"),
        duration_ms=max(0, int((monotonic() - started_clock) * 1000)),
        disposition=disposition,
        reason=reason,
        calls=metadata,
        retry_count=sum(runtime.retry_count for runtime in runtimes),
        recovery_count=0,
        behavior_gates=behavior_gates,
    )
    write_live_smoke_evidence(_EVIDENCE_PATH, serialized)


def test_one_deepseek_task_to_export_smoke(postgres_engine: Engine) -> None:
    """Run exactly one fictional sufficient-input path with five calls."""

    started_at = datetime.now(UTC)
    started_clock = monotonic()
    runtimes: list[DeepSeekModelRuntime] = []
    gates = dict(_FALSE_GATES)
    composition: DeterministicResultPostgresComposition | None = None
    try:
        client, composition = _result_client(postgres_engine, runtimes)
        with client:
            created = client.post(
                "/api/v1/tasks",
                headers={"Idempotency-Key": "fl2-deepseek-task-create"},
                json={
                    "taskName": "FL-2 DeepSeek live Anchor smoke",
                    "productCategory": "Backpack",
                    "promotionGoal": "Awareness",
                },
            )
            assert created.status_code == 201, created.text
            task_id = created.json()["taskId"]
            saved = client.put(
                f"/api/v1/tasks/{task_id}/primary-input",
                json={
                    "inputKind": "pasted_text",
                    "fileName": None,
                    "content": _fixture_input(),
                },
            )
            assert saved.status_code == 200, saved.text
            generated = client.post(
                f"/api/v1/tasks/{task_id}/commands/generate-result",
                headers={"Idempotency-Key": "fl2-deepseek-result"},
                json={"expectedInputRevision": 0},
            )
            assert generated.status_code == 201, generated.text
            assert generated.json()["status"] == "awaiting_review"
            awaiting = client.get(f"/api/v1/tasks/{task_id}/current-result")
            assert awaiting.status_code == 200, awaiting.text
            assert awaiting.json()["status"] == "awaiting_review"
            assert all(
                awaiting.json()[name] is not None
                for name in (
                    "productIntake",
                    "customerInsight",
                    "productPositioning",
                    "marketingBrief",
                    "xiaohongshuBrief",
                )
            )
            gates["validated_candidates"] = True
            confirmed = client.post(
                f"/api/v1/tasks/{task_id}/commands/confirm-current-result",
                headers={"Idempotency-Key": "fl2-deepseek-confirm"},
                json={
                    "expectedResultRevision": 0,
                    "marketingCoreMessage": (
                        "Confirmed DeepSeek commuter storage message"
                    ),
                    "xiaohongshuTitleDirection": (
                        "Confirmed DeepSeek commuter title direction"
                    ),
                },
            )
            assert confirmed.status_code == 201, confirmed.text
            assert confirmed.json()["status"] == "confirmed"
            gates["confirmed_result"] = True

            downloads: dict[str, bytes] = {}
            snapshot_ids: set[str] = set()
            for brief_kind in ("marketing", "xiaohongshu"):
                preview = client.post(
                    f"/api/v1/tasks/{task_id}/export-previews",
                    json={"briefKind": brief_kind},
                )
                assert preview.status_code == 200, preview.text
                snapshot = client.post(
                    "/api/v1/export-snapshots",
                    headers={"Idempotency-Key": f"fl2-deepseek-export-{brief_kind}"},
                    json={"basis": preview.json()["basis"]},
                )
                assert snapshot.status_code == 201, snapshot.text
                snapshot_ids.add(snapshot.json()["snapshotId"])
                downloaded = client.get(snapshot.json()["contentLocation"])
                assert downloaded.status_code == 200, downloaded.text
                downloads[brief_kind] = downloaded.content
            assert len(snapshot_ids) == 2
            gates["marketing_export_immutable"] = True
            gates["xiaohongshu_export_immutable"] = True
            for content in downloads.values():
                content.decode("utf-8")
                assert not content.startswith(b"\xef\xbb\xbf")
                assert content.endswith(b"\n")
                assert not content.endswith(b"\n\n")
            gates["downloads_utf8_no_bom_one_final_lf"] = True
            metadata = tuple(
                item for runtime in runtimes for item in runtime.metadata_records
            )
            assert len(metadata) == 5
            assert [item.version_tuple.provider_id for item in metadata] == [
                "deepseek"
            ] * 5
            assert [item.version_tuple.execution_profile_id for item in metadata] == [
                "product_intake_v1",
                "customer_insight_v1",
                "product_positioning_v1",
                "marketing_brief_v1",
                "xiaohongshu_mapping_v1",
            ]
        _write_evidence(
            started_at=started_at,
            started_clock=started_clock,
            disposition="PASS",
            reason="automated gates passed; operator must record human result",
            runtimes=runtimes,
            behavior_gates=gates,
        )
    except Exception:
        _write_evidence(
            started_at=started_at,
            started_clock=started_clock,
            disposition="FAIL",
            reason="automated smoke failed; operator review required",
            runtimes=runtimes,
            behavior_gates=gates,
        )
        raise
    finally:
        for runtime in runtimes:
            runtime.close()
        if composition is not None:
            composition.close()
