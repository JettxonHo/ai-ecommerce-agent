"""PostgreSQL participant for bounded review confirmation and Markdown export."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import cast

from sqlalchemy import Engine, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from ai_ecommerce_agent.modules.export_delivery.application.markdown_renderer import (
    render_export_markdown,
)
from ai_ecommerce_agent.modules.export_delivery.public import (
    ConfirmExportRequest,
    ExportBasis,
    ExportBriefKind,
    ExportPreview,
    ExportSnapshot,
)
from ai_ecommerce_agent.modules.marketing_brief.public import (
    MarketingBriefSemanticGroup,
    MarketingBriefSemanticGroupName,
    MarketingBriefVersionSnapshot,
)
from ai_ecommerce_agent.modules.task_management.infrastructure.tables import (
    EXPORT_SNAPSHOTS_TABLE,
    TASK_MANAGEMENT_SCHEMA_TOKEN,
    TASK_PRIMARY_INPUTS_FOR_RESULT_TABLE,
    TASK_RESULTS_TABLE,
    TASKS_TABLE,
)
from ai_ecommerce_agent.modules.task_management.public import DomainVersionReference
from ai_ecommerce_agent.modules.xiaohongshu_adapter.public import (
    XiaohongshuBriefSemanticGroup,
    XiaohongshuBriefSemanticGroupName,
    XiaohongshuBriefVersionSnapshot,
)
from ai_ecommerce_agent.shared_kernel import (
    ContentOrigin,
    DomainVersionId,
    ExportSnapshotId,
    ResourceReference,
    Revision,
    StructuredContent,
    TaskId,
    VersionNumber,
)

from .deterministic_result_postgres import (
    DeterministicResultSnapshot,
    row_mapping,
    snapshot_from_row,
)


class ReviewExportError(Exception):
    """Safe application error for preview, confirmation, and download."""

    def __init__(self, error_code: str, message: str, *, retryability: bool = False):
        self.error_code = error_code
        self.retryability = retryability
        super().__init__(message)


_TEMPLATE_VERSION = "mvp0-markdown-v1"
_MEDIA_TYPE = "text/markdown; charset=utf-8"
_SAFE_SLUG = re.compile(r"[^A-Za-z0-9]+")


def _timestamp(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _nonblank(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReviewExportError("validation_failed", "The export basis is invalid.")
    return value.strip()


def _mapping(
    value: object, message: str = "The current result is malformed."
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ReviewExportError("validation_failed", message)
    return cast(Mapping[str, object], value)


def _strings(value: object) -> tuple[str, ...]:
    if not isinstance(value, list | tuple):
        return ()
    items = cast(list[object] | tuple[object, ...], value)
    return tuple(
        item.strip() for item in items if isinstance(item, str) and item.strip()
    )


def _version_reference(value: object, kind: str) -> DomainVersionReference:
    text = _nonblank(value)
    return DomainVersionReference(DomainVersionId(text), VersionNumber.initial())


def _candidate_mapping(
    result: DeterministicResultSnapshot, brief_kind: ExportBriefKind
) -> tuple[Mapping[str, object], Mapping[str, object]]:
    key = (
        "marketingBrief"
        if brief_kind is ExportBriefKind.MARKETING
        else "xiaohongshuBrief"
    )
    wrapper = _mapping(result.candidates.get(key))
    root_key = (
        "brief_candidate"
        if brief_kind is ExportBriefKind.MARKETING
        else "xiaohongshu_brief_candidate"
    )
    workflow_key = (
        "version_and_workflow_context"
        if brief_kind is ExportBriefKind.MARKETING
        else "workflow_and_version_context"
    )
    return _mapping(wrapper.get(root_key)), _mapping(wrapper.get(workflow_key))


def _safe_filename(
    task_id: TaskId, kind: ExportBriefKind, generated_at: datetime
) -> str:
    slug = _SAFE_SLUG.sub("-", str(task_id)).strip("-") or "task"
    moment = _timestamp(generated_at).astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"task-{slug}-{kind.value}-v1-{moment}.md"


def _upstream_versions(
    workflow: Mapping[str, object], brief_kind: ExportBriefKind
) -> tuple[DomainVersionReference, ...]:
    keys = (
        ("approved_strategy_version_id", "facts_version_id", "insights_version_id")
        if brief_kind is ExportBriefKind.MARKETING
        else (
            "marketing_brief_version_id",
            "approved_strategy_version_id",
            "facts_version_id",
        )
    )
    refs: list[DomainVersionReference] = []
    for key in keys:
        value = workflow.get(key)
        if isinstance(value, str) and value.strip():
            refs.append(_version_reference(value, key))
    return tuple(refs)


def _brief_snapshot(
    result: DeterministicResultSnapshot,
    *,
    brief_kind: ExportBriefKind,
    task_revision: int,
) -> tuple[
    object,
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[DomainVersionReference, ...],
]:
    candidate, workflow = _candidate_mapping(result, brief_kind)
    if brief_kind is ExportBriefKind.MARKETING:
        expected = tuple(MarketingBriefSemanticGroupName)
        groups = tuple(
            MarketingBriefSemanticGroup(
                group=name,
                content=StructuredContent.from_mapping(
                    _mapping(
                        workflow
                        if name
                        is MarketingBriefSemanticGroupName.VERSION_AND_WORKFLOW_CONTEXT
                        else candidate.get(name.value)
                    )
                ),
                origin=(
                    ContentOrigin.USER
                    if name is MarketingBriefSemanticGroupName.MESSAGE_ARCHITECTURE
                    else ContentOrigin.MODEL
                ),
            )
            for name in expected
        )
        confirmation = _mapping(result.confirmation)
        marketing_version = _mapping(confirmation.get("marketingBriefVersion"))
        brief_id = _nonblank(marketing_version.get("resourceVersionId"))
        limitations = _strings(
            _mapping(candidate.get("constraints_and_honesty")).get(
                "evidence_limitations"
            )
        )
        hypotheses = _strings(
            _mapping(candidate.get("constraints_and_honesty")).get("hypotheses_to_test")
        ) + _strings(
            _mapping(candidate.get("constraints_and_honesty")).get(
                "accepted_hypotheses"
            )
        )
        risks = _strings(
            _mapping(candidate.get("constraints_and_honesty")).get("risk_notes")
        )
        snapshot = MarketingBriefVersionSnapshot(
            brief_version_id=DomainVersionId(brief_id),
            task_id=result.task_id,
            version_number=VersionNumber.initial(),
            valid=True,
            created_at=_timestamp(result.generated_at),
            upstream_versions=_upstream_versions(workflow, brief_kind),
            semantic_groups=groups,
            hypotheses=hypotheses,
            evidence_limitations=limitations,
            risks=risks,
            evidence_references=(
                ResourceReference(
                    "task_primary_input", f"{result.task_id}:r{result.input_revision}"
                ),
            ),
        )
    else:
        expected = tuple(XiaohongshuBriefSemanticGroupName)
        workflow_group = XiaohongshuBriefSemanticGroupName.WORKFLOW_AND_VERSION_CONTEXT
        groups = tuple(
            XiaohongshuBriefSemanticGroup(
                group=name,
                content=StructuredContent.from_mapping(
                    _mapping(
                        workflow
                        if name is workflow_group
                        else candidate.get(name.value)
                    )
                ),
                origin=(
                    ContentOrigin.USER
                    if name
                    is XiaohongshuBriefSemanticGroupName.CREATIVE_STRUCTURE_DIRECTIONS
                    else ContentOrigin.MODEL
                ),
            )
            for name in expected
        )
        confirmation = _mapping(result.confirmation)
        brief_id = _nonblank(
            _mapping(confirmation.get("xiaohongshuBriefVersion")).get(
                "resourceVersionId"
            )
        )
        evidence = _mapping(candidate.get("evidence_and_platform_constraints"))
        limitations = _strings(evidence.get("evidence_limitations"))
        hypotheses = _strings(evidence.get("hypotheses"))
        risks = _strings(evidence.get("platform_risk_notes"))
        snapshot = XiaohongshuBriefVersionSnapshot(
            brief_version_id=DomainVersionId(brief_id),
            task_id=result.task_id,
            version_number=VersionNumber.initial(),
            valid=True,
            created_at=_timestamp(result.generated_at),
            upstream_versions=_upstream_versions(workflow, brief_kind),
            semantic_groups=groups,
            hypotheses=hypotheses,
            evidence_limitations=limitations,
            risks=risks,
            evidence_references=(
                ResourceReference(
                    "task_primary_input", f"{result.task_id}:r{result.input_revision}"
                ),
            ),
        )
    return (
        snapshot,
        snapshot.hypotheses,
        snapshot.evidence_limitations,
        snapshot.risks,
        snapshot.upstream_versions,
    )


def _basis_for(
    result: DeterministicResultSnapshot,
    *,
    task_revision: int,
    brief_kind: ExportBriefKind,
) -> tuple[ExportBasis, object]:
    if result.status != "confirmed" or result.confirmation is None:
        raise ReviewExportError(
            "capability_conflict",
            "Only a confirmed current result can be exported.",
        )
    brief, hypotheses, limitations, risks, upstream = _brief_snapshot(
        result, brief_kind=brief_kind, task_revision=task_revision
    )
    confirmation = _mapping(result.confirmation)
    version_key = (
        "marketingBriefVersion"
        if brief_kind is ExportBriefKind.MARKETING
        else "xiaohongshuBriefVersion"
    )
    version_payload = _mapping(confirmation.get(version_key))
    basis = ExportBasis(
        task_id=result.task_id,
        task_revision=Revision(task_revision),
        brief_kind=brief_kind,
        brief_version=DomainVersionReference(
            DomainVersionId(_nonblank(version_payload.get("resourceVersionId"))),
            VersionNumber(_int(version_payload.get("versionNumber", 1))),
        ),
        upstream_versions=upstream,
        hypotheses=hypotheses,
        evidence_limitations=limitations,
        risks=risks,
    )
    return basis, brief


def _basis_json(
    basis: ExportBasis, *, result_revision: int, input_revision: int
) -> str:
    payload = {
        "taskId": str(basis.task_id),
        "taskRevision": basis.task_revision.value,
        "briefKind": basis.brief_kind.value,
        "briefVersion": {
            "resourceKind": basis.brief_kind.value + "_brief",
            "resourceVersionId": basis.brief_version.version_id.value,
            "versionNumber": basis.brief_version.version_number.value,
        },
        "upstreamVersions": [
            {
                "resourceKind": "domain_version",
                "resourceVersionId": item.version_id.value,
                "versionNumber": item.version_number.value,
            }
            for item in basis.upstream_versions
        ],
        "hypotheses": list(basis.hypotheses),
        "evidenceLimitations": list(basis.evidence_limitations),
        "risks": list(basis.risks),
        "resultRevision": result_revision,
        "inputRevision": input_revision,
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _snapshot_projection(row: Mapping[str, object]) -> ExportSnapshot:
    return ExportSnapshot(
        export_snapshot_id=ExportSnapshotId(str(row["export_snapshot_id"])),
        task_id=TaskId(str(row["task_id"])),
        brief_kind=ExportBriefKind(str(row["brief_kind"])),
        brief_version=DomainVersionReference(
            DomainVersionId(str(row["brief_version_id"])),
            VersionNumber(_int(row["brief_version_number"])),
        ),
        upstream_versions=tuple(
            DomainVersionReference(
                DomainVersionId(str(item["resourceVersionId"])),
                VersionNumber(_int(item["versionNumber"])),
            )
            for item in cast(
                list[Mapping[str, object]], json.loads(str(row["upstream_versions"]))
            )
        ),
        exported_at=_timestamp(cast(datetime, row["exported_at"])),
        file_name=str(row["file_name"]),
        media_type=str(row["media_type"]),
        content_location=str(row["content_location"]),
        template_version=str(row["template_version"]),
    )


def _int(value: object) -> int:
    return int(cast(str | int, value))


class ReviewExportApplication:
    """Task-owned preview, immutable snapshot, and stored-content adapter."""

    def __init__(self, engine: Engine, *, schema: str = "public") -> None:
        self._engine = engine.execution_options(
            schema_translate_map={TASK_MANAGEMENT_SCHEMA_TOKEN: schema}
        )
        self._sessions: sessionmaker[Session] = sessionmaker(
            bind=self._engine, class_=Session, expire_on_commit=False
        )

    def close(self) -> None:
        self._engine.dispose()

    def _current(
        self, session: Session, task_id: TaskId, *, lock: bool = False
    ) -> tuple[int, int, DeterministicResultSnapshot]:
        task_statement = select(TASKS_TABLE.c.revision).where(
            TASKS_TABLE.c.task_id == str(task_id)
        )
        if lock:
            task_statement = task_statement.with_for_update()
        task_row = session.execute(task_statement).scalar_one_or_none()
        if task_row is None:
            raise ReviewExportError("not_found", "The requested Task was not found.")
        input_statement = select(TASK_PRIMARY_INPUTS_FOR_RESULT_TABLE.c.revision).where(
            TASK_PRIMARY_INPUTS_FOR_RESULT_TABLE.c.task_id == str(task_id)
        )
        if lock:
            input_statement = input_statement.with_for_update()
        input_row = session.execute(input_statement).mappings().one_or_none()
        if input_row is None:
            raise ReviewExportError(
                "not_found", "The requested primary input was not found."
            )
        statement = (
            select(TASK_RESULTS_TABLE)
            .where(TASK_RESULTS_TABLE.c.task_id == str(task_id))
            .order_by(TASK_RESULTS_TABLE.c.result_revision.desc())
            .limit(1)
        )
        if lock:
            statement = statement.with_for_update()
        result_row = session.execute(statement).mappings().one_or_none()
        if result_row is None:
            raise ReviewExportError("not_found", "The current result was not found.")
        return (
            _int(task_row),
            _int(row_mapping(input_row)["revision"]),
            snapshot_from_row(row_mapping(result_row)),
        )

    def preview_export(
        self, *, task_id: TaskId, brief_kind: ExportBriefKind
    ) -> ExportPreview:
        try:
            with self._sessions() as session:
                task_revision, input_revision, result = self._current(session, task_id)
                if result.input_revision != input_revision:
                    raise ReviewExportError(
                        "revision_conflict",
                        "The current result is stale; refresh before exporting.",
                    )
                basis, brief = _basis_for(
                    result, task_revision=task_revision, brief_kind=brief_kind
                )
                filename = _safe_filename(task_id, brief_kind, result.generated_at)
                preview_snapshot = ExportSnapshot(
                    export_snapshot_id=ExportSnapshotId("preview"),
                    task_id=task_id,
                    brief_kind=brief_kind,
                    brief_version=basis.brief_version,
                    upstream_versions=basis.upstream_versions,
                    exported_at=_timestamp(result.generated_at),
                    file_name=filename,
                    media_type=_MEDIA_TYPE,
                    content_location="/api/v1/export-snapshots/preview/content",
                    template_version=_TEMPLATE_VERSION,
                )
                render_export_markdown(
                    export_snapshot=preview_snapshot,
                    brief_snapshot=cast(
                        MarketingBriefVersionSnapshot | XiaohongshuBriefVersionSnapshot,
                        brief,
                    ),
                )
                return ExportPreview(
                    basis=basis,
                    template_version=_TEMPLATE_VERSION,
                    file_name=filename,
                    media_type=_MEDIA_TYPE,
                )
        except ReviewExportError:
            raise
        except (ValueError, TypeError, KeyError) as error:
            raise ReviewExportError(
                "validation_failed", "The current result cannot be exported."
            ) from error
        except SQLAlchemyError as error:
            raise ReviewExportError(
                "persistence_error",
                "The export service is temporarily unavailable.",
                retryability=True,
            ) from error

    def create_export_snapshot(
        self, *, idempotency_key: str, request: ConfirmExportRequest
    ) -> tuple[ExportSnapshot, bool]:
        key = idempotency_key.strip()
        if not key:
            raise ReviewExportError(
                "validation_failed", "The export retry key is invalid."
            )
        basis = request.basis
        try:
            with self._sessions() as session:
                with session.begin():
                    task_revision, input_revision, result = self._current(
                        session, basis.task_id, lock=True
                    )
                    if result.input_revision != input_revision:
                        raise ReviewExportError(
                            "revision_conflict",
                            "The current result is stale; refresh before exporting.",
                        )
                    existing = (
                        session.execute(
                            select(EXPORT_SNAPSHOTS_TABLE)
                            .where(
                                EXPORT_SNAPSHOTS_TABLE.c.task_id == str(basis.task_id),
                                EXPORT_SNAPSHOTS_TABLE.c.idempotency_key == key,
                            )
                            .with_for_update()
                        )
                        .mappings()
                        .one_or_none()
                    )
                    if existing is not None:
                        stored = json.loads(str(row_mapping(existing)["basis"]))
                        expected_stored = json.loads(
                            _basis_json(
                                basis,
                                result_revision=_int(
                                    row_mapping(existing)["result_revision"]
                                ),
                                input_revision=_int(
                                    row_mapping(existing)["input_revision"]
                                ),
                            )
                        )
                        if stored != expected_stored:
                            raise ReviewExportError(
                                "idempotency_conflict",
                                "The retry key belongs to another export basis.",
                            )
                        return _snapshot_projection(row_mapping(existing)), True
                    current_basis, brief = _basis_for(
                        result,
                        task_revision=task_revision,
                        brief_kind=basis.brief_kind,
                    )
                    if current_basis != basis:
                        raise ReviewExportError(
                            "revision_conflict",
                            "The current Brief changed; refresh the export preview.",
                        )
                    export_id = ExportSnapshotId.new()
                    exported_at = datetime.now(UTC)
                    filename = _safe_filename(
                        basis.task_id, basis.brief_kind, exported_at
                    )
                    location = f"/api/v1/export-snapshots/{export_id}/content"
                    export = ExportSnapshot(
                        export_snapshot_id=export_id,
                        task_id=basis.task_id,
                        brief_kind=basis.brief_kind,
                        brief_version=basis.brief_version,
                        upstream_versions=basis.upstream_versions,
                        exported_at=exported_at,
                        file_name=filename,
                        media_type=_MEDIA_TYPE,
                        content_location=location,
                        template_version=_TEMPLATE_VERSION,
                    )
                    content = render_export_markdown(
                        export_snapshot=export,
                        brief_snapshot=cast(
                            MarketingBriefVersionSnapshot
                            | XiaohongshuBriefVersionSnapshot,
                            brief,
                        ),
                    )
                    session.execute(
                        EXPORT_SNAPSHOTS_TABLE.insert().values(
                            export_snapshot_id=str(export_id),
                            task_id=str(basis.task_id),
                            task_revision=task_revision,
                            result_revision=result.result_revision,
                            input_revision=input_revision,
                            idempotency_key=key,
                            brief_kind=basis.brief_kind.value,
                            brief_version_id=basis.brief_version.version_id.value,
                            brief_version_number=basis.brief_version.version_number.value,
                            upstream_versions=json.dumps(
                                [
                                    {
                                        "resourceVersionId": item.version_id.value,
                                        "versionNumber": item.version_number.value,
                                    }
                                    for item in basis.upstream_versions
                                ],
                                ensure_ascii=False,
                            ),
                            hypotheses=json.dumps(
                                list(basis.hypotheses), ensure_ascii=False
                            ),
                            evidence_limitations=json.dumps(
                                list(basis.evidence_limitations), ensure_ascii=False
                            ),
                            risks=json.dumps(list(basis.risks), ensure_ascii=False),
                            basis=_basis_json(
                                basis,
                                result_revision=result.result_revision,
                                input_revision=input_revision,
                            ),
                            exported_at=exported_at,
                            file_name=filename,
                            media_type=_MEDIA_TYPE,
                            content_location=location,
                            template_version=_TEMPLATE_VERSION,
                            content=content,
                        )
                    )
                    return export, False
        except ReviewExportError:
            raise
        except IntegrityError as error:
            raise ReviewExportError(
                "persistence_error",
                "The export service is temporarily unavailable.",
                retryability=True,
            ) from error
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            raise ReviewExportError(
                "validation_failed", "The export basis is invalid."
            ) from error
        except SQLAlchemyError as error:
            raise ReviewExportError(
                "persistence_error",
                "The export service is temporarily unavailable.",
                retryability=True,
            ) from error

    def get_export_content(
        self, *, export_snapshot_id: ExportSnapshotId
    ) -> tuple[ExportSnapshot, str]:
        try:
            with self._sessions() as session:
                row = (
                    session.execute(
                        select(EXPORT_SNAPSHOTS_TABLE).where(
                            EXPORT_SNAPSHOTS_TABLE.c.export_snapshot_id
                            == str(export_snapshot_id)
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                if row is None:
                    raise ReviewExportError(
                        "not_found", "The requested export snapshot was not found."
                    )
                snapshot = _snapshot_projection(row_mapping(row))
                content = str(row_mapping(row)["content"])
                if not content.endswith("\n") or "\r" in content:
                    raise ReviewExportError(
                        "persistence_error",
                        "The export snapshot is unavailable.",
                        retryability=True,
                    )
                return snapshot, content
        except ReviewExportError:
            raise
        except SQLAlchemyError as error:
            raise ReviewExportError(
                "persistence_error",
                "The export service is temporarily unavailable.",
                retryability=True,
            ) from error


__all__ = ["ReviewExportApplication", "ReviewExportError"]
