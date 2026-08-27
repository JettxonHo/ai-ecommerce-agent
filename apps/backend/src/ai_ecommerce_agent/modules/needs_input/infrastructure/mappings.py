"""Row ↔ immutable Needs Input snapshot mappings."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from typing import cast

from ai_ecommerce_agent.shared_kernel import Revision, TaskId

from ..domain.snapshots import (
    NeedsInputActionRequestSnapshot,
    NeedsInputExpectedRecovery,
    NeedsInputStatus,
)


def _text(row: Mapping[str, object], name: str) -> str:
    return cast(str, row[name])


def _timestamp(row: Mapping[str, object], name: str) -> datetime:
    return cast(datetime, row[name])


def _json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _json_array(row: Mapping[str, object], name: str) -> list[object]:
    decoded = json.loads(_text(row, name))
    if not isinstance(decoded, list):
        raise ValueError(f"{name} must contain a JSON array")
    return cast(list[object], decoded)


def _mapping_array(
    row: Mapping[str, object], name: str
) -> tuple[Mapping[str, object], ...]:
    values = _json_array(row, name)
    result: list[Mapping[str, object]] = []
    for value in values:
        if not isinstance(value, Mapping):
            raise ValueError(f"{name} must contain JSON objects")
        result.append(dict(cast(Mapping[str, object], value)))
    return tuple(result)


def _nullable_json_mapping(
    row: Mapping[str, object], name: str
) -> Mapping[str, object] | None:
    value = row.get(name)
    if value is None:
        return None
    decoded = json.loads(cast(str, value))
    if not isinstance(decoded, Mapping):
        raise ValueError(f"{name} must contain a JSON object")
    return dict(cast(Mapping[str, object], decoded))


def request_row_to_snapshot(
    row: Mapping[str, object],
) -> NeedsInputActionRequestSnapshot:
    superseded = row.get("superseded_by_action_request_id")
    return NeedsInputActionRequestSnapshot(
        action_request_id=_text(row, "action_request_id"),
        task_id=TaskId(_text(row, "task_id")),
        revision=Revision(int(cast(int, row["revision"]))),
        status=NeedsInputStatus(_text(row, "status")),
        reason_type=_text(row, "reason_type"),
        reason_summary=_text(row, "reason_summary"),
        affected_stages=tuple(
            str(value) for value in _json_array(row, "affected_stages")
        ),
        source_references=_mapping_array(row, "source_references"),
        conflict_values=_mapping_array(row, "conflict_values"),
        allowed_resolution_types=tuple(
            str(value) for value in _json_array(row, "allowed_resolution_types")
        ),
        expected_recovery=NeedsInputExpectedRecovery(_text(row, "expected_recovery")),
        superseded_by=str(superseded) if superseded is not None else None,
        created_at=_timestamp(row, "created_at"),
        updated_at=_timestamp(row, "updated_at"),
        resolution_idempotency_key=(
            str(row["resolution_idempotency_key"])
            if row.get("resolution_idempotency_key") is not None
            else None
        ),
        resolution_type=(
            str(row["resolution_type"])
            if row.get("resolution_type") is not None
            else None
        ),
        resolution_payload=_nullable_json_mapping(row, "resolution_payload"),
        resolved_at=(
            cast(datetime, row["resolved_at"])
            if row.get("resolved_at") is not None
            else None
        ),
    )


def request_snapshot_to_row(
    request: NeedsInputActionRequestSnapshot,
) -> dict[str, object]:
    return {
        "action_request_id": request.action_request_id,
        "task_id": str(request.task_id),
        "revision": request.revision.value,
        "status": request.status.value,
        "reason_type": request.reason_type,
        "reason_summary": request.reason_summary,
        "affected_stages": _json_text(list(request.affected_stages)),
        "source_references": _json_text(list(request.source_references)),
        "conflict_values": _json_text(list(request.conflict_values)),
        "allowed_resolution_types": _json_text(list(request.allowed_resolution_types)),
        "expected_recovery": request.expected_recovery.value,
        "superseded_by_action_request_id": request.superseded_by,
        "resolution_idempotency_key": request.resolution_idempotency_key,
        "resolution_type": request.resolution_type,
        "resolution_payload": (
            _json_text(request.resolution_payload)
            if request.resolution_payload is not None
            else None
        ),
        "resolved_at": request.resolved_at,
        "created_at": request.created_at,
        "updated_at": request.updated_at,
    }


__all__ = ["request_row_to_snapshot", "request_snapshot_to_row"]
