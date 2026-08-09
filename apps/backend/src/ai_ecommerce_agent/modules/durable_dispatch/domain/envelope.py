"""Immutable, reference-only description of planned Durable Dispatch work."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ResourceReference,
    Revision,
    RunId,
)

from .identity import DispatchId


def _require_exact_non_empty_string(value: object, field_name: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{field_name} must be a string")
    if not value.strip():
        raise ValueError(f"{field_name} must be non-empty")


def _require_instance(
    value: object, expected_type: type[object], field_name: str
) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(f"{field_name} must be a {expected_type.__name__}")


@dataclass(frozen=True, slots=True)
class WorkIntentEnvelope:
    """Immutable identity, version and reference context for planned work."""

    dispatch_id: DispatchId
    intent_type: str
    owning_operation: str
    target_scope: ResourceReference
    command_id: str
    stage_run_id: RunId | None
    input_fingerprint: str
    fingerprint_schema_version: str
    base_domain_version_id: DomainVersionId | None
    expected_revision: Revision | None
    payload_reference: ResourceReference
    rerun_of: DispatchId | None
    ordering_key: str | None
    created_at: datetime
    available_at: datetime

    def __post_init__(self) -> None:
        _require_instance(self.dispatch_id, DispatchId, "dispatch_id")
        for field_name, value in (
            ("intent_type", self.intent_type),
            ("owning_operation", self.owning_operation),
            ("command_id", self.command_id),
            ("input_fingerprint", self.input_fingerprint),
            ("fingerprint_schema_version", self.fingerprint_schema_version),
        ):
            _require_exact_non_empty_string(value, field_name)

        _require_instance(self.target_scope, ResourceReference, "target_scope")
        if self.stage_run_id is not None:
            _require_instance(self.stage_run_id, RunId, "stage_run_id")
        if self.base_domain_version_id is not None:
            _require_instance(
                self.base_domain_version_id,
                DomainVersionId,
                "base_domain_version_id",
            )
        if self.expected_revision is not None:
            _require_instance(self.expected_revision, Revision, "expected_revision")
        _require_instance(
            self.payload_reference,
            ResourceReference,
            "payload_reference",
        )
        if self.rerun_of is not None:
            _require_instance(self.rerun_of, DispatchId, "rerun_of")
            if self.rerun_of == self.dispatch_id:
                raise ValueError("rerun_of must differ from dispatch_id")
        if self.ordering_key is not None:
            _require_exact_non_empty_string(self.ordering_key, "ordering_key")

        _require_instance(self.created_at, datetime, "created_at")
        _require_instance(self.available_at, datetime, "available_at")
        try:
            is_earlier = self.available_at < self.created_at
        except TypeError as error:
            raise ValueError(
                "created_at and available_at must be comparable datetimes"
            ) from error
        if is_earlier:
            raise ValueError("available_at must not be earlier than created_at")
