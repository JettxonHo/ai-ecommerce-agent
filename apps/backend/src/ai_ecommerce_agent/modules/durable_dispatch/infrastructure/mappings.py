"""Explicit primitive row mappings for Durable Dispatch Work Intents."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import cast

from ai_ecommerce_agent.modules.durable_dispatch.domain.envelope import (
    WorkIntentEnvelope,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.identity import (
    DeliveryAttemptId,
    DispatchId,
    FencingToken,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.ownership import (
    LeaseHolderId,
    WorkIntentLease,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots import (
    WorkIntentSnapshot,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.status import (
    WorkIntentStatus,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ResourceReference,
    Revision,
    RunId,
)


def _text(row: Mapping[str, object], name: str) -> str:
    return cast(str, row[name])


def _nullable_text(row: Mapping[str, object], name: str) -> str | None:
    return cast(str | None, row[name])


def _integer(row: Mapping[str, object], name: str) -> int:
    return cast(int, row[name])


def _nullable_integer(row: Mapping[str, object], name: str) -> int | None:
    return cast(int | None, row[name])


def _timestamp(row: Mapping[str, object], name: str) -> datetime:
    return cast(datetime, row[name])


def _lease_from_row(
    row: Mapping[str, object],
    dispatch_id: DispatchId,
    fencing_token: FencingToken,
) -> WorkIntentLease | None:
    delivery_attempt_id = _nullable_text(row, "delivery_attempt_id")
    lease_holder_id = _nullable_text(row, "lease_holder_id")
    lease_expires_at = cast(datetime | None, row["lease_expires_at"])
    if (
        delivery_attempt_id is None
        and lease_holder_id is None
        and lease_expires_at is None
    ):
        return None
    if (
        delivery_attempt_id is None
        or lease_holder_id is None
        or lease_expires_at is None
    ):
        raise ValueError("lease columns must be all null or all non-null")
    return WorkIntentLease(
        dispatch_id,
        DeliveryAttemptId(delivery_attempt_id),
        LeaseHolderId(lease_holder_id),
        fencing_token,
        lease_expires_at,
    )


def work_intent_row_to_snapshot(
    row: Mapping[str, object],
) -> WorkIntentSnapshot:
    """Rehydrate one primitive Work Intent row through domain invariants."""

    dispatch_id = DispatchId(_text(row, "dispatch_id"))
    envelope = WorkIntentEnvelope(
        dispatch_id,
        _text(row, "intent_type"),
        _text(row, "owning_operation"),
        ResourceReference(
            _text(row, "target_resource_kind"),
            _text(row, "target_resource_id"),
        ),
        _text(row, "command_id"),
        (
            RunId(stage_run_id)
            if (stage_run_id := _nullable_text(row, "stage_run_id")) is not None
            else None
        ),
        _text(row, "input_fingerprint"),
        _text(row, "fingerprint_schema_version"),
        (
            DomainVersionId(base_version_id)
            if (base_version_id := _nullable_text(row, "base_domain_version_id"))
            is not None
            else None
        ),
        (
            Revision(expected_revision)
            if (expected_revision := _nullable_integer(row, "expected_revision"))
            is not None
            else None
        ),
        ResourceReference(
            _text(row, "payload_resource_kind"),
            _text(row, "payload_resource_id"),
        ),
        (
            DispatchId(rerun_of)
            if (rerun_of := _nullable_text(row, "rerun_of_dispatch_id")) is not None
            else None
        ),
        _nullable_text(row, "ordering_key"),
        _timestamp(row, "created_at"),
        _timestamp(row, "available_at"),
    )
    fencing_token = FencingToken(_integer(row, "fencing_token"))
    return WorkIntentSnapshot(
        envelope,
        WorkIntentStatus(_text(row, "status")),
        Revision(_integer(row, "revision")),
        cast(bool, row["cancellation_requested"]),
        _lease_from_row(row, dispatch_id, fencing_token),
    )


def work_intent_snapshot_to_insert_row(
    snapshot: WorkIntentSnapshot,
) -> dict[str, object]:
    """Project a Work Intent snapshot to the exact insert-row primitives."""

    envelope = snapshot.envelope
    lease = snapshot.current_lease
    return {
        "dispatch_id": envelope.dispatch_id.value,
        "intent_type": envelope.intent_type,
        "owning_operation": envelope.owning_operation,
        "target_resource_kind": envelope.target_scope.resource_kind,
        "target_resource_id": envelope.target_scope.resource_id,
        "command_id": envelope.command_id,
        "stage_run_id": envelope.stage_run_id.value
        if envelope.stage_run_id is not None
        else None,
        "input_fingerprint": envelope.input_fingerprint,
        "fingerprint_schema_version": envelope.fingerprint_schema_version,
        "base_domain_version_id": envelope.base_domain_version_id.value
        if envelope.base_domain_version_id is not None
        else None,
        "expected_revision": envelope.expected_revision.value
        if envelope.expected_revision is not None
        else None,
        "payload_resource_kind": envelope.payload_reference.resource_kind,
        "payload_resource_id": envelope.payload_reference.resource_id,
        "rerun_of_dispatch_id": envelope.rerun_of.value
        if envelope.rerun_of is not None
        else None,
        "ordering_key": envelope.ordering_key,
        "created_at": envelope.created_at,
        "available_at": envelope.available_at,
        "status": snapshot.status.value,
        "revision": snapshot.revision.value,
        "cancellation_requested": snapshot.cancellation_requested,
        "delivery_attempt_id": lease.delivery_attempt_id.value
        if lease is not None
        else None,
        "lease_holder_id": lease.holder_id.value if lease is not None else None,
        "fencing_token": lease.fencing_token.value
        if lease is not None
        else FencingToken.initial().value,
        "lease_expires_at": lease.lease_expires_at if lease is not None else None,
    }


def work_intent_snapshot_to_update_values(
    snapshot: WorkIntentSnapshot,
) -> dict[str, object]:
    """Project only mutable current-state values for a later CAS update."""

    lease = snapshot.current_lease
    values: dict[str, object] = {
        "status": snapshot.status.value,
        "revision": snapshot.revision.value,
        "cancellation_requested": snapshot.cancellation_requested,
        "delivery_attempt_id": (
            lease.delivery_attempt_id.value if lease is not None else None
        ),
        "lease_holder_id": lease.holder_id.value if lease is not None else None,
        "lease_expires_at": lease.lease_expires_at if lease is not None else None,
    }
    if lease is not None:
        values["fencing_token"] = lease.fencing_token.value
    return values


__all__ = [
    "work_intent_row_to_snapshot",
    "work_intent_snapshot_to_insert_row",
    "work_intent_snapshot_to_update_values",
]
