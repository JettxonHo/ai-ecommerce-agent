"""Explicit SQLAlchemy Core row-to-domain conversions for Source Evidence.

The Source Evidence tables persist only primitive values.  This adapter keeps
that representation at the infrastructure boundary and rehydrates the
existing domain values without adding defaults, aliases, or persistence
behaviour.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import cast

from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceAssociationMembershipState,
    SourceProcessingStatus,
    SourceVersion,
    SourceVersionProcessing,
    TaskSourceAssociation,
)
from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceAssociationId,
    SourceId,
    SourceVersionId,
    TaskId,
    VersionNumber,
)


def _text(row: Mapping[str, object], name: str) -> str:
    return cast(str, row[name])


def _nullable_text(row: Mapping[str, object], name: str) -> str | None:
    return cast(str | None, row[name])


def _integer(row: Mapping[str, object], name: str) -> int:
    return cast(int, row[name])


def _timestamp(row: Mapping[str, object], name: str) -> datetime:
    return cast(datetime, row[name])


def source_version_row_to_domain(row: Mapping[str, object]) -> SourceVersion:
    """Map one Source Version row to its immutable domain identity."""

    return SourceVersion(
        source_version_id=SourceVersionId(_text(row, "source_version_id")),
        source_id=SourceId(_text(row, "source_id")),
        version_number=VersionNumber(_integer(row, "version_number")),
    )


def source_version_domain_to_row(source_version: SourceVersion) -> dict[str, object]:
    """Map one Source Version to SQLAlchemy Core insert/update primitives."""

    return {
        "source_version_id": str(source_version.source_version_id),
        "source_id": str(source_version.source_id),
        "version_number": source_version.version_number.value,
    }


def source_version_processing_row_to_domain(
    row: Mapping[str, object],
) -> SourceVersionProcessing:
    """Map one processing Current Truth row to the domain value."""

    return SourceVersionProcessing(
        source_version_id=SourceVersionId(_text(row, "source_version_id")),
        status=SourceProcessingStatus(_text(row, "status")),
        revision=Revision(_integer(row, "revision")),
        failure_summary=_nullable_text(row, "failure_summary"),
        updated_at=_timestamp(row, "updated_at"),
    )


def source_version_processing_domain_to_row(
    processing: SourceVersionProcessing,
) -> dict[str, object]:
    """Map processing Current Truth to SQLAlchemy Core primitives."""

    return {
        "source_version_id": str(processing.source_version_id),
        "status": processing.status.value,
        "revision": processing.revision.value,
        "failure_summary": processing.failure_summary,
        "updated_at": processing.updated_at,
    }


def task_source_association_row_to_domain(
    row: Mapping[str, object],
) -> TaskSourceAssociation:
    """Map one Task-to-Source membership row to the domain value."""

    return TaskSourceAssociation(
        source_association_id=SourceAssociationId(_text(row, "source_association_id")),
        task_id=TaskId(_text(row, "task_id")),
        source_id=SourceId(_text(row, "source_id")),
        source_version_id=SourceVersionId(_text(row, "source_version_id")),
        membership_state=SourceAssociationMembershipState(
            _text(row, "membership_state")
        ),
        revision=Revision(_integer(row, "revision")),
        replaced_by_association_id=(
            SourceAssociationId(replacement_id)
            if (replacement_id := _nullable_text(row, "replaced_by_association_id"))
            is not None
            else None
        ),
    )


def task_source_association_domain_to_row(
    association: TaskSourceAssociation,
) -> dict[str, object]:
    """Map one Task-to-Source membership to SQLAlchemy Core primitives."""

    return {
        "source_association_id": str(association.source_association_id),
        "task_id": str(association.task_id),
        "source_id": str(association.source_id),
        "source_version_id": str(association.source_version_id),
        "membership_state": association.membership_state.value,
        "revision": association.revision.value,
        "replaced_by_association_id": (
            str(association.replaced_by_association_id)
            if association.replaced_by_association_id is not None
            else None
        ),
    }


__all__ = [
    "source_version_domain_to_row",
    "source_version_processing_domain_to_row",
    "source_version_processing_row_to_domain",
    "source_version_row_to_domain",
    "task_source_association_domain_to_row",
    "task_source_association_row_to_domain",
]
