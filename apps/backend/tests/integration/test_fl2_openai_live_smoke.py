"""One explicit FL-2 Task-to-export smoke through FastAPI and PostgreSQL.

The module is skipped unless both the existing local PostgreSQL opt-in and
``RUN_LIVE_MODEL_SMOKE=1`` are set.  Once both flags are set, the private
adapter factory owns Secret resolution and fails fast on a missing or blank
key before the PostgreSQL fixture is opened; the key value is never printed
or included in evidence.
"""

# FastAPI/Starlette's TestClient is an untyped framework boundary in the
# accepted runtime tuple; this test focuses on the one operator-visible flow.
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportPrivateUsage=false, reportCallIssue=false

from __future__ import annotations

import os
import tempfile
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
from ai_ecommerce_agent.platform.model_runtime.openai_responses._live_evidence import (
    serialize_live_smoke_evidence,
    write_live_smoke_evidence,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses._runtime import (
    OpenAIResponsesModelRuntime,
    create_openai_responses_runtime,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)
from fixtures.mvp0_loader import load_manifest

warnings.filterwarnings("ignore", category=StarletteDeprecationWarning)
from fastapi.testclient import TestClient  # noqa: E402

pytestmark = [pytest.mark.integration, pytest.mark.live]

_RUN_LIVE = os.environ.get("RUN_LIVE_MODEL_SMOKE") == "1"
_RUN_POSTGRES = os.environ.get("MVP0_RUN_TASK_HTTP_POSTGRES") == "1"
if _RUN_LIVE and not os.environ.get("GIT_COMMIT", "").strip():
    pytest.fail(
        "RUN_LIVE_MODEL_SMOKE=1 requires GIT_COMMIT for evidence; "
        "value is not displayed"
    )
if not (_RUN_LIVE and _RUN_POSTGRES):
    pytest.skip(
        "set MVP0_RUN_TASK_HTTP_POSTGRES=1 and RUN_LIVE_MODEL_SMOKE=1 for the "
        "single FL-2 OpenAI smoke",
        allow_module_level=True,
    )

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mvp0_fl2_openai_live"
URL_ENV = "MVP0_TASK_HTTP_DATABASE_URL"
DEFAULT_URL = URL.create(
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


def _database_url() -> str:
    return os.environ.get(URL_ENV, DEFAULT_URL).strip()


def _alembic_config(database_url: str) -> Config:
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.set_main_option("business_schema", SCHEMA)
    config.set_main_option("version_table_schema", SCHEMA)
    return config


@pytest.fixture(scope="module")
def live_runtime_preflight() -> Iterator[None]:
    """Let the adapter own Secret validation before PostgreSQL setup."""

    runtime = create_openai_responses_runtime()
    try:
        yield
    finally:
        runtime.close()


@pytest.fixture(scope="module")
def postgres_engine(live_runtime_preflight: None) -> Iterator[Engine]:
    """Own one schema, migrate to the current head, and clean it afterwards."""

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
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA "{SCHEMA}"'))
    try:
        command.upgrade(_alembic_config(database_url), "head")
        yield engine
    finally:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        engine.dispose()


def _evidence_path(started_at: datetime) -> Path:
    configured = os.environ.get("FL2_LIVE_EVIDENCE_PATH", "").strip()
    if configured:
        return Path(configured)
    stamp = started_at.strftime("%Y%m%dT%H%M%S%fZ")
    return Path(tempfile.gettempdir()) / f"ai-ecommerce-agent-fl2-{stamp}.json"


def _fixture_input() -> str:
    fixture = load_manifest().fixture("fixture-sufficient-v1")
    return "\n\n".join(
        path.read_text(encoding="utf-8") for path in fixture.source_paths
    )


def _result_client(
    engine: Engine,
    runtimes: list[OpenAIResponsesModelRuntime],
) -> tuple[TestClient, DeterministicResultPostgresComposition]:
    task_factory = TaskManagementPostgresUnitOfWorkFactory.from_engine(
        engine, schema=SCHEMA
    )
    input_factory = PrimaryInputPostgresUnitOfWorkFactory.from_engine(
        engine, schema=SCHEMA
    )

    def runtime_factory(
        _requests: tuple[ModelCallRequest, ...], _payloads: tuple[str, ...]
    ) -> OpenAIResponsesModelRuntime:
        runtime = create_openai_responses_runtime()
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
        schema=SCHEMA,
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
    path: Path,
    started_at: datetime,
    started_clock: float,
    disposition: str,
    reason: str,
    runtimes: list[OpenAIResponsesModelRuntime],
    behavior_gates: dict[str, bool],
) -> None:
    metadata = tuple(item for runtime in runtimes for item in runtime.metadata_records)
    serialized = serialize_live_smoke_evidence(
        commit=os.environ["GIT_COMMIT"].strip(),
        started_at_utc=started_at.isoformat().replace("+00:00", "Z"),
        duration_ms=max(0, int((monotonic() - started_clock) * 1000)),
        disposition=disposition,
        reason=reason,
        calls=metadata,
        retry_count=sum(runtime.retry_count for runtime in runtimes),
        recovery_count=0,
        behavior_gates=behavior_gates,
    )
    write_live_smoke_evidence(path, serialized)


def test_one_real_task_to_export_smoke(postgres_engine: Engine) -> None:
    """Run exactly one sufficient Anchor SKU path with five real calls."""

    started_at = datetime.now(UTC)
    started_clock = monotonic()
    evidence_path = _evidence_path(started_at)
    runtimes: list[OpenAIResponsesModelRuntime] = []
    gates = dict(_FALSE_GATES)
    composition: DeterministicResultPostgresComposition | None = None
    try:
        client, composition = _result_client(postgres_engine, runtimes)
        input_text = _fixture_input()
        with client:
            created = client.post(
                "/api/v1/tasks",
                headers={"Idempotency-Key": "fl2-live-task-create"},
                json={
                    "taskName": "FL-2 live Anchor smoke",
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
                    "content": input_text,
                },
            )
            assert saved.status_code == 200, saved.text
            generated = client.post(
                f"/api/v1/tasks/{task_id}/commands/generate-result",
                headers={"Idempotency-Key": "fl2-live-result"},
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
                headers={"Idempotency-Key": "fl2-live-confirm"},
                json={
                    "expectedResultRevision": 0,
                    "marketingCoreMessage": "Confirmed live commuter storage message",
                    "xiaohongshuTitleDirection": (
                        "Confirmed live commuter title direction"
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
                    headers={"Idempotency-Key": f"fl2-live-export-{brief_kind}"},
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
            assert [item.version_tuple.execution_profile_id for item in metadata] == [
                "product_intake_v1",
                "customer_insight_v1",
                "product_positioning_v1",
                "marketing_brief_v1",
                "xiaohongshu_mapping_v1",
            ]
        _write_evidence(
            path=evidence_path,
            started_at=started_at,
            started_clock=started_clock,
            disposition="PASS",
            reason="automated gates passed; operator must record human result",
            runtimes=runtimes,
            behavior_gates=gates,
        )
    except Exception:
        _write_evidence(
            path=evidence_path,
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
