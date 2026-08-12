"""Minimal PostgreSQL participant for the deterministic current result."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import cast

from sqlalchemy import Engine, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

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
from ai_ecommerce_agent.modules.task_management.infrastructure.tables import (
    TASK_MANAGEMENT_SCHEMA_TOKEN,
    TASK_PRIMARY_INPUTS_FOR_RESULT_TABLE,
    TASK_RESULTS_TABLE,
    TASKS_TABLE,
)
from ai_ecommerce_agent.modules.xiaohongshu_adapter.application.skills import (
    xiaohongshu_brief_mapping,
)
from ai_ecommerce_agent.orchestration.deterministic_pipeline import (
    DeterministicPipelineCoordinator,
    PipelineResult,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)
from ai_ecommerce_agent.shared_kernel import TaskId


class DeterministicResultError(Exception):
    """Safe application error for the current-result HTTP adapter."""

    def __init__(self, error_code: str, message: str, *, retryability: bool = False):
        self.error_code = error_code
        self.retryability = retryability
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class DeterministicResultSnapshot:
    """Immutable projection returned to the HTTP adapter."""

    task_id: TaskId
    result_revision: int
    input_revision: int
    status: str
    generated_at: datetime
    missing_information: tuple[str, ...]
    candidates: Mapping[str, Mapping[str, object] | None]


def _row(value: object) -> Mapping[str, object]:
    return cast(Mapping[str, object], value)


def _int(value: object) -> int:
    return int(cast(str | int, value))


def _json_mapping(value: object) -> Mapping[str, object] | None:
    if value is None:
        return None
    try:
        decoded = json.loads(str(value))
    except (TypeError, ValueError) as error:
        raise DeterministicResultError(
            "persistence_error",
            "The current result is unavailable",
            retryability=True,
        ) from error
    if not isinstance(decoded, Mapping):
        raise DeterministicResultError(
            "persistence_error",
            "The current result is unavailable",
            retryability=True,
        )
    return cast(Mapping[str, object], decoded)


def _snapshot(row: Mapping[str, object]) -> DeterministicResultSnapshot:
    try:
        missing_raw = json.loads(str(row["missing_information"]))
        missing = tuple(str(item) for item in missing_raw)
        candidates = {
            "productIntake": _json_mapping(row["product_intake"]),
            "customerInsight": _json_mapping(row["customer_insight"]),
            "productPositioning": _json_mapping(row["product_positioning"]),
            "marketingBrief": _json_mapping(row["marketing_brief"]),
            "xiaohongshuBrief": _json_mapping(row["xiaohongshu_brief"]),
        }
        return DeterministicResultSnapshot(
            task_id=TaskId(str(row["task_id"])),
            result_revision=_int(row["result_revision"]),
            input_revision=_int(row["input_revision"]),
            status=str(row["status"]),
            generated_at=cast(datetime, row["generated_at"]),
            missing_information=missing,
            candidates=candidates,
        )
    except DeterministicResultError:
        raise
    except (KeyError, TypeError, ValueError) as error:
        raise DeterministicResultError(
            "persistence_error", "The current result is unavailable", retryability=True
        ) from error


class DeterministicResultApplication:
    """Read and atomically publish one Task-owned deterministic result."""

    def __init__(self, engine: Engine, *, schema: str = "public") -> None:
        self._engine = engine.execution_options(
            schema_translate_map={TASK_MANAGEMENT_SCHEMA_TOKEN: schema}
        )
        self._sessions: sessionmaker[Session] = sessionmaker(
            bind=self._engine, class_=Session, expire_on_commit=False
        )

    def close(self) -> None:
        self._engine.dispose()

    def _read_existing_key(
        self, task_id: TaskId, idempotency_key: str
    ) -> DeterministicResultSnapshot | None:
        try:
            with self._sessions() as session:
                row = (
                    session.execute(
                        select(TASK_RESULTS_TABLE).where(
                            TASK_RESULTS_TABLE.c.task_id == str(task_id),
                            TASK_RESULTS_TABLE.c.idempotency_key == idempotency_key,
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                return _snapshot(_row(row)) if row is not None else None
        except DeterministicResultError:
            raise
        except SQLAlchemyError as error:
            raise DeterministicResultError(
                "persistence_error",
                "The result service is temporarily unavailable",
                retryability=True,
            ) from error

    def _read_input(
        self, task_id: TaskId, expected_input_revision: int
    ) -> tuple[str, int]:
        try:
            with self._sessions() as session:
                task = (
                    session.execute(
                        select(TASKS_TABLE.c.task_id).where(
                            TASKS_TABLE.c.task_id == str(task_id)
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                if task is None:
                    raise DeterministicResultError(
                        "not_found", "The requested Task was not found."
                    )
                value = (
                    session.execute(
                        select(
                            TASK_PRIMARY_INPUTS_FOR_RESULT_TABLE.c.content,
                            TASK_PRIMARY_INPUTS_FOR_RESULT_TABLE.c.revision,
                        ).where(
                            TASK_PRIMARY_INPUTS_FOR_RESULT_TABLE.c.task_id
                            == str(task_id)
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                if value is None:
                    raise DeterministicResultError(
                        "not_found", "The requested primary input was not found."
                    )
                row = _row(value)
                revision = _int(row["revision"])
                if revision != expected_input_revision:
                    raise DeterministicResultError(
                        "revision_conflict",
                        "The primary input changed; refresh before generating again.",
                    )
                return str(row["content"]), revision
        except DeterministicResultError:
            raise
        except SQLAlchemyError as error:
            raise DeterministicResultError(
                "persistence_error",
                "The result service is temporarily unavailable",
                retryability=True,
            ) from error

    def _next_revision(self, session: Session, task_id: TaskId) -> int:
        current = session.scalar(
            select(func.max(TASK_RESULTS_TABLE.c.result_revision)).where(
                TASK_RESULTS_TABLE.c.task_id == str(task_id)
            )
        )
        return 0 if current is None else int(current) + 1

    def generate_result(
        self,
        *,
        task_id: TaskId,
        idempotency_key: str,
        expected_input_revision: int,
        coordinator: DeterministicPipelineCoordinator,
    ) -> tuple[DeterministicResultSnapshot, bool]:
        """Generate outside a transaction, then publish with a locked recheck."""

        existing = self._read_existing_key(task_id, idempotency_key)
        if existing is not None:
            if existing.input_revision != expected_input_revision:
                raise DeterministicResultError(
                    "idempotency_conflict",
                    "The retry key belongs to another input revision.",
                )
            return existing, True

        input_text, _ = self._read_input(task_id, expected_input_revision)
        try:
            generated = coordinator.generate(input_text=input_text)
        except Exception as error:
            # Preserve a safe boundary: runtime candidates and tracebacks never
            # reach the HTTP adapter or the result table.
            raise DeterministicResultError(
                "generation_failed", "The deterministic result could not be generated."
            ) from error

        return self._commit(
            task_id=task_id,
            idempotency_key=idempotency_key,
            expected_input_revision=expected_input_revision,
            generated=generated,
        )

    def _commit(
        self,
        *,
        task_id: TaskId,
        idempotency_key: str,
        expected_input_revision: int,
        generated: PipelineResult,
    ) -> tuple[DeterministicResultSnapshot, bool]:
        candidate_map = dict(generated.candidates)
        values = {
            "task_id": str(task_id),
            "input_revision": expected_input_revision,
            "idempotency_key": idempotency_key,
            "status": generated.status,
            "generated_at": datetime.now().astimezone(),
            "missing_information": json.dumps(
                list(generated.missing_information), ensure_ascii=False
            ),
            "product_intake": (
                json.dumps(
                    candidate_map["productIntake"].to_mapping(), ensure_ascii=False
                )
                if candidate_map.get("productIntake") is not None
                else None
            ),
            "customer_insight": (
                json.dumps(
                    candidate_map["customerInsight"].to_mapping(), ensure_ascii=False
                )
                if candidate_map.get("customerInsight") is not None
                else None
            ),
            "product_positioning": (
                json.dumps(
                    candidate_map["productPositioning"].to_mapping(),
                    ensure_ascii=False,
                )
                if candidate_map.get("productPositioning") is not None
                else None
            ),
            "marketing_brief": (
                json.dumps(
                    candidate_map["marketingBrief"].to_mapping(), ensure_ascii=False
                )
                if candidate_map.get("marketingBrief") is not None
                else None
            ),
            "xiaohongshu_brief": (
                json.dumps(
                    candidate_map["xiaohongshuBrief"].to_mapping(),
                    ensure_ascii=False,
                )
                if candidate_map.get("xiaohongshuBrief") is not None
                else None
            ),
        }
        try:
            with self._sessions() as session:
                with session.begin():
                    task = (
                        session.execute(
                            select(TASKS_TABLE.c.task_id)
                            .where(TASKS_TABLE.c.task_id == str(task_id))
                            .with_for_update()
                        )
                        .mappings()
                        .one_or_none()
                    )
                    if task is None:
                        raise DeterministicResultError(
                            "not_found", "The requested Task was not found."
                        )
                    current_input = (
                        session.execute(
                            select(TASK_PRIMARY_INPUTS_FOR_RESULT_TABLE.c.revision)
                            .where(
                                TASK_PRIMARY_INPUTS_FOR_RESULT_TABLE.c.task_id
                                == str(task_id)
                            )
                            .with_for_update()
                        )
                        .mappings()
                        .one_or_none()
                    )
                    if current_input is None:
                        raise DeterministicResultError(
                            "not_found", "The requested primary input was not found."
                        )
                    current_revision = _int(_row(current_input)["revision"])
                    existing_key = (
                        session.execute(
                            select(TASK_RESULTS_TABLE)
                            .where(
                                TASK_RESULTS_TABLE.c.task_id == str(task_id),
                                TASK_RESULTS_TABLE.c.idempotency_key == idempotency_key,
                            )
                            .with_for_update()
                        )
                        .mappings()
                        .one_or_none()
                    )
                    if existing_key is not None:
                        replay = _snapshot(_row(existing_key))
                        if replay.input_revision != expected_input_revision:
                            raise DeterministicResultError(
                                "idempotency_conflict",
                                "The retry key belongs to another input revision.",
                            )
                        return replay, True
                    if current_revision != expected_input_revision:
                        raise DeterministicResultError(
                            "revision_conflict",
                            "The primary input changed; refresh before generating "
                            "again.",
                        )
                    # A second key cannot publish another result for the same
                    # input revision; preserve one immutable result per input.
                    existing_input = (
                        session.execute(
                            select(TASK_RESULTS_TABLE)
                            .where(
                                TASK_RESULTS_TABLE.c.task_id == str(task_id),
                                TASK_RESULTS_TABLE.c.input_revision
                                == expected_input_revision,
                            )
                            .with_for_update()
                        )
                        .mappings()
                        .one_or_none()
                    )
                    if existing_input is not None:
                        raise DeterministicResultError(
                            "idempotency_conflict",
                            "A result already exists for this input revision.",
                        )
                    values["result_revision"] = self._next_revision(session, task_id)
                    session.execute(TASK_RESULTS_TABLE.insert().values(values))
                    inserted = (
                        session.execute(
                            select(TASK_RESULTS_TABLE).where(
                                TASK_RESULTS_TABLE.c.task_id == str(task_id),
                                TASK_RESULTS_TABLE.c.result_revision
                                == values["result_revision"],
                            )
                        )
                        .mappings()
                        .one()
                    )
                    return _snapshot(_row(inserted)), False
        except DeterministicResultError:
            raise
        except (IntegrityError, SQLAlchemyError) as error:
            raise DeterministicResultError(
                "persistence_error",
                "The result service is temporarily unavailable",
                retryability=True,
            ) from error

    def get_current_result(
        self, *, task_id: TaskId
    ) -> DeterministicResultSnapshot | None:
        try:
            with self._sessions() as session:
                task = session.scalar(
                    select(TASKS_TABLE.c.task_id).where(
                        TASKS_TABLE.c.task_id == str(task_id)
                    )
                )
                if task is None:
                    raise DeterministicResultError(
                        "not_found", "The requested Task was not found."
                    )
                row = (
                    session.execute(
                        select(TASK_RESULTS_TABLE)
                        .where(TASK_RESULTS_TABLE.c.task_id == str(task_id))
                        .order_by(TASK_RESULTS_TABLE.c.result_revision.desc())
                        .limit(1)
                    )
                    .mappings()
                    .one_or_none()
                )
                return _snapshot(_row(row)) if row is not None else None
        except DeterministicResultError:
            raise
        except SQLAlchemyError as error:
            raise DeterministicResultError(
                "persistence_error",
                "The result service is temporarily unavailable",
                retryability=True,
            ) from error


@dataclass(frozen=True, slots=True)
class DeterministicResultPostgresComposition:
    """Process-lifetime engine and result application participant."""

    engine: Engine
    application: DeterministicResultApplication
    coordinator: DeterministicPipelineCoordinator

    def close(self) -> None:
        self.application.close()


def compose_deterministic_result_postgres(
    config: PostgresEngineConfig,
    *,
    schema: str = "public",
    coordinator: DeterministicPipelineCoordinator | None = None,
) -> DeterministicResultPostgresComposition:
    """Build the result participant without reading process configuration."""

    engine = create_postgres_engine(config)
    application = DeterministicResultApplication(engine, schema=schema)
    bound_coordinator = coordinator or DeterministicPipelineCoordinator(
        spec_factories=(
            product_intake_fact_extraction.product_intake_candidate_output_spec,
            customer_insight_analysis.customer_insight_candidate_output_spec,
            product_positioning.product_positioning_candidate_output_spec,
            marketing_brief_generation.marketing_brief_candidate_output_spec,
            xiaohongshu_brief_mapping.xiaohongshu_brief_candidate_output_spec,
        )
    )
    return DeterministicResultPostgresComposition(
        engine, application, bound_coordinator
    )


__all__ = [
    "DeterministicResultApplication",
    "DeterministicResultError",
    "DeterministicResultPostgresComposition",
    "DeterministicResultSnapshot",
    "compose_deterministic_result_postgres",
]
