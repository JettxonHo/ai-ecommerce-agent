"""Small, provider-neutral persistence seam for one P2 pilot attempt.

This seam records immutable attempt identity/run evidence, bounded Markdown
export capture, explicit Human Review, and terminal outcome records.  The module
has no provider, database, or application-runtime dependency and only writes to
an explicitly approved local directory.
"""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Final, cast
from urllib.parse import urlsplit

__all__ = [
    "ArtifactErrorCode",
    "AttemptArtifactError",
    "AttemptArtifactSnapshot",
    "ArtifactReference",
    "CallRecord",
    "CaptureExport",
    "CostSummary",
    "ExportContentReference",
    "ExportVersionReference",
    "FinalDisposition",
    "FinalizationCost",
    "FinalizationExecution",
    "FinalizationGates",
    "GateSummary",
    "FinalizeAttempt",
    "PilotAttemptArtifacts",
    "PricingReference",
    "RecordReview",
    "RecordRun",
    "ReserveAttempt",
    "ReviewDimension",
    "TaskReference",
    "ResultReference",
    "UsageSummary",
    "UnknownValue",
]


class ArtifactErrorCode(StrEnum):
    """Fixed safe error codes exposed by the artifact seam."""

    INVALID_COMMAND = "invalid_command"
    INVALID_ROOT = "invalid_root"
    ROOT_NOT_ALLOWED = "root_not_allowed"
    ROOT_EXISTS = "root_exists"
    ATTEMPT_NOT_FOUND = "attempt_not_found"
    IDENTITY_MISMATCH = "identity_mismatch"
    RECORD_EXISTS = "record_exists"
    ARTIFACT_IO_ERROR = "artifact_io_error"
    ARTIFACT_CORRUPT = "artifact_corrupt"


class AttemptArtifactError(Exception):
    """Stable, path-free artifact error.

    The original OS exception is deliberately not retained in the message or
    public attributes.  Callers receive only a fixed code and a short safe
    operation label.
    """

    def __init__(self, code: ArtifactErrorCode | str, operation: str) -> None:
        if type(code) is ArtifactErrorCode:
            value = code.value
        elif type(code) is str and code in {item.value for item in ArtifactErrorCode}:
            value = code
        else:
            raise TypeError("code must be an ArtifactErrorCode")
        if type(operation) is not str or not operation or not operation.isascii():
            raise TypeError("operation must be a safe ASCII label")
        self.error_code = value
        self.code = value
        self.operation = operation
        super().__init__(f"{value}:{operation}")

    def __str__(self) -> str:
        return f"{self.error_code}:{self.operation}"


class UnknownValue(StrEnum):
    """Typed values for metadata that is unavailable or cannot be derived."""

    UNKNOWN = "UNKNOWN"
    NOT_EXPOSED = "NOT_EXPOSED"
    NOT_DERIVABLE = "NOT_DERIVABLE"


_UNKNOWN_VALUES: Final[frozenset[str]] = frozenset(
    value.value for value in UnknownValue
)


_SAMPLE_ID: Final[str] = "P01"
_ATTEMPT_ID: Final[str] = "P2-P01-A1"
_IDENTITY_RECORD_TYPE: Final[str] = "attempt_identity"
_RUN_RECORD_TYPE: Final[str] = "attempt_run"
_SCHEMA_VERSION: Final[str] = "pilot-attempt-artifact-v1"
_EXPORT_RECORD_TYPE: Final[str] = "marketing_export_capture"
_EXPORT_CAPTURE_METHOD: Final[str] = "local_filesystem"
_EXPORT_TEMPLATE_VERSION: Final[str] = "mvp0-markdown-v1"
_EXPORT_MEDIA_TYPE: Final[str] = "text/markdown; charset=utf-8"
_EXPORT_SERVER_FILE_NAME_MAX_LENGTH: Final[int] = 128
_EXPORT_FILE_NAMES: Final[dict[str, str]] = {
    "marketing": "marketing-brief.md",
    "xiaohongshu": "xiaohongshu-brief.md",
}
_EXPORT_METADATA_FILE_NAMES: Final[dict[str, str]] = {
    kind: f"{kind}-export.json" for kind in _EXPORT_FILE_NAMES
}
_REVIEW_RECORD_TYPE: Final[str] = "human_review"
_REVIEW_ROLES: Final[frozenset[str]] = frozenset(
    {"author_operator", "non_author_trial_operator"}
)
_REVIEW_STATES: Final[frozenset[str]] = frozenset({"APPROVED", "REJECTED"})
_REVIEW_DIMENSION_NAMES: Final[tuple[str, ...]] = (
    "product_fact_correctness",
    "mandatory_messages",
    "prohibited_claims",
    "fabrication_misleading_content",
    "marketing_brief_usability",
    "xiaohongshu_consistency",
    "markdown_delivery",
)
_REVIEW_DECISIONS: Final[frozenset[str]] = frozenset({"PASS", "FAIL", "NOT_APPLICABLE"})
_REVIEW_RATIONALES: Final[frozenset[str]] = frozenset(
    {
        "approved_all_applicable_critical_dimensions_pass",
        "rejected_critical_dimension_or_export",
    }
)
_FINAL_REASON_CODES: Final[frozenset[str]] = frozenset(
    {
        "qualifying_approved_export",
        "review_rejected",
        "automated_gate_failed",
        "cost_cap_exceeded",
        "execution_not_qualified",
        "missing_export",
    }
)
_SAFE_ID_CHARS: Final[str] = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:-"
)
_GATE_KEY_CHARS: Final[str] = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:-"
)
_SENSITIVE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "prompt",
        "prompts",
        "context",
        "payload",
        "raw_payload",
        "raw_provider_payload",
        "response",
        "raw_response",
        "traceback",
        "secret",
        "api_key",
        "cookie",
        "pii",
        "personal_data",
        "absolute_path",
        "path",
    }
)


def _exact_text(value: object, field_name: str, *, allow_empty: bool = False) -> str:
    if type(value) is not str:
        raise TypeError(f"{field_name} must be an exact string")
    if not allow_empty and not value.strip():
        raise ValueError(f"{field_name} must not be blank")
    return value


def _safe_id(value: object, field_name: str) -> str:
    text = _exact_text(value, field_name)
    if any(character not in _SAFE_ID_CHARS for character in text):
        raise ValueError(f"{field_name} contains unsupported characters")
    if text in {".", ".."}:
        raise ValueError(f"{field_name} is not a safe identity")
    return text


def _optional_id(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    return _safe_id(value, field_name)


def _nonnegative_int(value: object, field_name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{field_name} must be an exact int")
    if value < 0:
        raise ValueError(f"{field_name} must not be negative")
    return value


def _optional_nonnegative_int(value: object, field_name: str) -> int | None:
    if value is None:
        return None
    return _nonnegative_int(value, field_name)


def _observed_value(value: object, field_name: str) -> int | UnknownValue:
    if value is None:
        return UnknownValue.NOT_EXPOSED
    if isinstance(value, UnknownValue):
        return value
    if type(value) is str and value in _UNKNOWN_VALUES:
        return UnknownValue(value)
    return _nonnegative_int(value, field_name)


def _serialize_observed(value: int | UnknownValue | None) -> int | str:
    if value is None:
        return UnknownValue.UNKNOWN.value
    return value.value if isinstance(value, UnknownValue) else value


def _serialize_unknown(value: str | UnknownValue | None) -> str:
    if value is None:
        return UnknownValue.UNKNOWN.value
    return value.value if isinstance(value, UnknownValue) else value


def _timestamp(value: object, field_name: str) -> str | None:
    """Normalize an explicitly supplied aware timestamp; never invent one."""

    if value is None:
        return None
    if type(value) is datetime:
        moment = value
        if moment.tzinfo is None or moment.utcoffset() is None:
            raise ValueError(f"{field_name} must be timezone-aware")
        return moment.astimezone(UTC).isoformat().replace("+00:00", "Z")
    text = _exact_text(value, field_name)
    if text.endswith("Z"):
        candidate = text[:-1] + "+00:00"
    else:
        candidate = text
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _safe_url(value: object, field_name: str) -> str:
    text = _exact_text(value, field_name)
    parsed = urlsplit(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{field_name} must be an absolute HTTP(S) URL")
    if any(character in text for character in "\r\n\x00"):
        raise ValueError(f"{field_name} contains unsupported characters")
    return text


def _as_mapping(value: object, field_name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} must be a mapping")
    source = cast(Mapping[object, object], value)
    result: dict[str, object] = {}
    for key, item in source.items():
        if type(key) is not str:
            raise TypeError(f"{field_name} keys must be exact strings")
        lowered = key.casefold()
        if lowered in _SENSITIVE_KEYS or any(
            sensitive in lowered
            for sensitive in ("password", "credential", "authorization")
        ):
            raise ValueError(f"{field_name} contains a prohibited key")
        result[key] = item
    return result


@dataclass(frozen=True, slots=True)
class TaskReference:
    """Sanitized Task identity carried by a run record."""

    task_id: str | None = None
    revision: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "task_id", _optional_id(self.task_id, "task_id"))
        object.__setattr__(
            self, "revision", _optional_nonnegative_int(self.revision, "task_revision")
        )

    def to_mapping(self) -> dict[str, object]:
        return {"task_id": self.task_id, "revision": self.revision}


@dataclass(frozen=True, slots=True)
class ResultReference:
    """Sanitized result identity carried by a run record."""

    result_id: str | None = None
    revision: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "result_id", _optional_id(self.result_id, "result_id"))
        object.__setattr__(
            self,
            "revision",
            _optional_nonnegative_int(self.revision, "result_revision"),
        )

    def to_mapping(self) -> dict[str, object]:
        return {"result_id": self.result_id, "revision": self.revision}


@dataclass(frozen=True, slots=True)
class PricingReference:
    """Versioned, provider-neutral pricing reference (not a price guess)."""

    record_id: str | None = None
    source_url: str | None = None
    model_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "record_id", _optional_id(self.record_id, "pricing_record_id")
        )
        if self.source_url is not None:
            object.__setattr__(
                self, "source_url", _safe_url(self.source_url, "pricing_source_url")
            )
        object.__setattr__(
            self, "model_id", _optional_id(self.model_id, "pricing_model_id")
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "record_id": self.record_id,
            "source_url": self.source_url,
            "model_id": self.model_id,
        }


@dataclass(frozen=True, slots=True)
class GateSummary:
    """Fixed-shape boolean gate projection without arbitrary text."""

    values: tuple[tuple[str, bool], ...] = ()

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for key, value in self.values:
            _exact_text(key, "gate name")
            if any(character not in _GATE_KEY_CHARS for character in key):
                raise ValueError("gate names contain unsupported characters")
            if key in seen:
                raise ValueError("gate names must be unique")
            if type(value) is not bool:
                raise TypeError("gate values must be bool")
            seen.add(key)

    @classmethod
    def from_value(cls, value: object) -> GateSummary | None:
        if value is None:
            return None
        if isinstance(value, GateSummary):
            return value
        mapping = _as_mapping(value, "gates")
        values: list[tuple[str, bool]] = []
        for key, item in mapping.items():
            if type(key) is not str or type(item) is not bool:
                raise TypeError("gates must map strings to bool")
            values.append((key, item))
        return cls(tuple(sorted(values)))

    def to_mapping(self) -> dict[str, bool] | None:
        return None if not self.values else dict(self.values)


@dataclass(frozen=True, slots=True)
class UsageSummary:
    """Optional observed token usage; absent values remain ``None``."""

    input_tokens: int | UnknownValue | None = UnknownValue.NOT_EXPOSED
    output_tokens: int | UnknownValue | None = UnknownValue.NOT_EXPOSED
    total_tokens: int | UnknownValue | None = UnknownValue.NOT_EXPOSED

    def __post_init__(self) -> None:
        for field_name in ("input_tokens", "output_tokens", "total_tokens"):
            object.__setattr__(
                self,
                field_name,
                _observed_value(getattr(self, field_name), field_name),
            )

    @classmethod
    def from_value(cls, value: object) -> UsageSummary | None:
        if value is None:
            return None
        if isinstance(value, UsageSummary):
            return value
        mapping = _as_mapping(value, "usage")
        allowed = {"input_tokens", "output_tokens", "total_tokens"}
        if set(mapping) - allowed:
            raise ValueError("usage contains unsupported fields")
        return cls(
            input_tokens=cast(int | UnknownValue | None, mapping.get("input_tokens")),
            output_tokens=cast(int | UnknownValue | None, mapping.get("output_tokens")),
            total_tokens=cast(int | UnknownValue | None, mapping.get("total_tokens")),
        )

    def to_mapping(self) -> dict[str, int | str]:
        return {
            "input_tokens": _serialize_observed(self.input_tokens),
            "output_tokens": _serialize_observed(self.output_tokens),
            "total_tokens": _serialize_observed(self.total_tokens),
        }


@dataclass(frozen=True, slots=True)
class CostSummary:
    """Optional integer micro-USD reservation/observation."""

    reserved_micro_usd: int | UnknownValue | None = UnknownValue.UNKNOWN
    actual_micro_usd: int | UnknownValue | None = UnknownValue.NOT_EXPOSED
    currency: str | UnknownValue | None = UnknownValue.NOT_DERIVABLE

    def __post_init__(self) -> None:
        for field_name in ("reserved_micro_usd", "actual_micro_usd"):
            object.__setattr__(
                self,
                field_name,
                _observed_value(getattr(self, field_name), field_name),
            )
        if type(self.currency) is str and self.currency in _UNKNOWN_VALUES:
            object.__setattr__(self, "currency", UnknownValue(self.currency))
        elif type(self.currency) is str:
            object.__setattr__(self, "currency", _safe_id(self.currency, "currency"))
        elif self.currency is None:
            object.__setattr__(self, "currency", UnknownValue.NOT_DERIVABLE)
        elif not isinstance(self.currency, UnknownValue):
            raise TypeError("currency must be a safe id or typed unknown")

    @classmethod
    def from_value(cls, value: object) -> CostSummary | None:
        if value is None:
            return None
        if isinstance(value, CostSummary):
            return value
        mapping = _as_mapping(value, "cost")
        allowed = {"reserved_micro_usd", "actual_micro_usd", "currency"}
        if set(mapping) - allowed:
            raise ValueError("cost contains unsupported fields")
        return cls(
            reserved_micro_usd=cast(
                int | UnknownValue | None, mapping.get("reserved_micro_usd")
            ),
            actual_micro_usd=cast(
                int | UnknownValue | None, mapping.get("actual_micro_usd")
            ),
            currency=cast(str | UnknownValue | None, mapping.get("currency")),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "reserved_micro_usd": _serialize_observed(self.reserved_micro_usd),
            "actual_micro_usd": _serialize_observed(self.actual_micro_usd),
            "currency": _serialize_unknown(self.currency),
        }


@dataclass(frozen=True, slots=True)
class ArtifactReference:
    """A bounded reference to an external or persisted record."""

    kind: str
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", _safe_id(self.kind, "reference kind"))
        object.__setattr__(self, "value", _safe_id(self.value, "reference value"))

    def to_mapping(self) -> dict[str, str]:
        return {"kind": self.kind, "value": self.value}


@dataclass(frozen=True, slots=True)
class CallRecord:
    """Sanitized metadata for one bounded model call."""

    model_call_id: str | None = None
    provider_attempt_ids: tuple[str, ...] = ()
    provider_response_id: str | None = None
    provider_request_id: str | None = None
    latency_ms: int | None = None
    status: str | None = None
    usage: UsageSummary | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "model_call_id", _optional_id(self.model_call_id, "model_call_id")
        )
        if type(self.provider_attempt_ids) is not tuple:
            raise TypeError("provider_attempt_ids must be an exact tuple")
        object.__setattr__(
            self,
            "provider_attempt_ids",
            tuple(
                _safe_id(value, "provider_attempt_id")
                for value in self.provider_attempt_ids
            ),
        )
        object.__setattr__(
            self,
            "provider_response_id",
            _optional_id(self.provider_response_id, "provider_response_id"),
        )
        object.__setattr__(
            self,
            "provider_request_id",
            _optional_id(self.provider_request_id, "provider_request_id"),
        )
        object.__setattr__(
            self,
            "latency_ms",
            _optional_nonnegative_int(self.latency_ms, "latency_ms"),
        )
        if self.status is not None:
            object.__setattr__(self, "status", _safe_id(self.status, "call status"))
        object.__setattr__(self, "usage", UsageSummary.from_value(self.usage))

    @classmethod
    def from_value(cls, value: object) -> CallRecord:
        if isinstance(value, CallRecord):
            return value
        mapping = _as_mapping(value, "call")
        allowed = {
            "model_call_id",
            "provider_attempt_ids",
            "provider_response_id",
            "provider_request_id",
            "latency_ms",
            "status",
            "usage",
        }
        if set(mapping) - allowed:
            raise ValueError("call record contains unsupported fields")
        provider_attempt_ids_value = mapping.get("provider_attempt_ids", ())
        if type(provider_attempt_ids_value) is not tuple:
            if type(provider_attempt_ids_value) is list:
                provider_attempt_ids = tuple(
                    cast(str, item)
                    for item in cast(list[object], provider_attempt_ids_value)
                )
            else:
                raise TypeError("provider_attempt_ids must be a tuple or list")
        else:
            provider_attempt_ids = tuple(
                cast(str, item)
                for item in cast(tuple[object, ...], provider_attempt_ids_value)
            )
        return cls(
            model_call_id=cast(str | None, mapping.get("model_call_id")),
            provider_attempt_ids=provider_attempt_ids,
            provider_response_id=cast(str | None, mapping.get("provider_response_id")),
            provider_request_id=cast(str | None, mapping.get("provider_request_id")),
            latency_ms=cast(int | None, mapping.get("latency_ms")),
            status=cast(str | None, mapping.get("status")),
            usage=cast(UsageSummary | None, mapping.get("usage")),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "model_call_id": self.model_call_id,
            "provider_attempt_ids": list(self.provider_attempt_ids),
            "provider_response_id": self.provider_response_id,
            "provider_request_id": self.provider_request_id,
            "latency_ms": self.latency_ms,
            "status": self.status,
            "usage": UsageSummary().to_mapping()
            if self.usage is None
            else self.usage.to_mapping(),
        }


@dataclass(frozen=True, slots=True)
class ReserveAttempt:
    """Command that reserves exactly one immutable attempt directory."""

    artifact_root: Path
    sample_id: str = _SAMPLE_ID
    attempt_id: str = _ATTEMPT_ID

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "artifact_root", _path_value(self.artifact_root, "artifact_root")
        )
        object.__setattr__(self, "sample_id", _safe_id(self.sample_id, "sample_id"))
        object.__setattr__(self, "attempt_id", _safe_id(self.attempt_id, "attempt_id"))


@dataclass(frozen=True, slots=True)
class RecordRun:
    """Command that exclusively creates the one run record for an attempt."""

    sample_id: str = _SAMPLE_ID
    attempt_id: str = _ATTEMPT_ID
    task_id: str | None = None
    task_revision: int | None = None
    result_id: str | None = None
    result_revision: int | None = None
    provider_id: str | None = None
    api_family: str | None = None
    configured_model_id: str | None = None
    resolved_model_id: str | None = None
    base_url: str | None = None
    reasoning_effort: str | None = None
    pricing_record_id: str | None = None
    pricing_source_url: str | None = None
    pricing_model_id: str | None = None
    started_at_utc: datetime | str | None = None
    completed_at_utc: datetime | str | None = None
    gates: GateSummary | Mapping[str, bool] | None = None
    call_count: int | None = None
    calls: (
        tuple[CallRecord | Mapping[str, object], ...]
        | Sequence[CallRecord | Mapping[str, object]]
    ) = ()
    usage: UsageSummary | Mapping[str, object] | None = None
    cost: CostSummary | Mapping[str, object] | None = None
    refs: (
        tuple[ArtifactReference | Mapping[str, object], ...]
        | Sequence[ArtifactReference | Mapping[str, object]]
    ) = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "sample_id", _safe_id(self.sample_id, "sample_id"))
        object.__setattr__(self, "attempt_id", _safe_id(self.attempt_id, "attempt_id"))
        for field_name in (
            "task_id",
            "result_id",
            "provider_id",
            "api_family",
            "configured_model_id",
            "resolved_model_id",
            "reasoning_effort",
            "pricing_record_id",
            "pricing_model_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _optional_id(getattr(self, field_name), field_name),
            )
        if self.base_url is not None:
            object.__setattr__(self, "base_url", _safe_url(self.base_url, "base_url"))
        if self.pricing_source_url is not None:
            object.__setattr__(
                self,
                "pricing_source_url",
                _safe_url(self.pricing_source_url, "pricing_source_url"),
            )
        object.__setattr__(
            self,
            "task_revision",
            _optional_nonnegative_int(self.task_revision, "task_revision"),
        )
        object.__setattr__(
            self,
            "result_revision",
            _optional_nonnegative_int(self.result_revision, "result_revision"),
        )
        object.__setattr__(
            self, "started_at_utc", _timestamp(self.started_at_utc, "started_at_utc")
        )
        object.__setattr__(
            self,
            "completed_at_utc",
            _timestamp(self.completed_at_utc, "completed_at_utc"),
        )
        object.__setattr__(self, "gates", GateSummary.from_value(self.gates))
        object.__setattr__(
            self, "call_count", _optional_nonnegative_int(self.call_count, "call_count")
        )
        if type(self.calls) not in (tuple, list):
            raise TypeError("calls must be a tuple or list")
        object.__setattr__(
            self, "calls", tuple(CallRecord.from_value(value) for value in self.calls)
        )
        object.__setattr__(self, "usage", UsageSummary.from_value(self.usage))
        object.__setattr__(self, "cost", CostSummary.from_value(self.cost))
        if type(self.refs) not in (tuple, list):
            raise TypeError("refs must be a tuple or list")
        references: list[ArtifactReference] = []
        for value in self.refs:
            if isinstance(value, ArtifactReference):
                references.append(value)
                continue
            mapping = _as_mapping(value, "refs")
            if set(mapping) != {"kind", "value"}:
                raise ValueError("refs must contain bounded kind/value references")
            kind = mapping["kind"]
            reference_value = mapping["value"]
            if type(kind) is not str or type(reference_value) is not str:
                raise TypeError("reference kind/value must be exact strings")
            references.append(ArtifactReference(kind, reference_value))
        object.__setattr__(self, "refs", tuple(references))

    def to_mapping(self) -> dict[str, object]:
        """Return the fixed sanitized run projection."""

        task = TaskReference(self.task_id, self.task_revision)
        result = ResultReference(self.result_id, self.result_revision)
        pricing = PricingReference(
            self.pricing_record_id, self.pricing_source_url, self.pricing_model_id
        )
        gates = GateSummary.from_value(self.gates)
        usage = UsageSummary.from_value(self.usage)
        cost = CostSummary.from_value(self.cost)
        call_records = cast(tuple[CallRecord, ...], self.calls)
        references = cast(tuple[ArtifactReference, ...], self.refs)
        return {
            "schema_version": _SCHEMA_VERSION,
            "record_type": _RUN_RECORD_TYPE,
            "sample_id": self.sample_id,
            "attempt_id": self.attempt_id,
            "immutable": True,
            "task": task.to_mapping(),
            "result": result.to_mapping(),
            "provider": {
                "provider_id": self.provider_id,
                "api_family": self.api_family,
            },
            "model": {
                "configured_model_id": self.configured_model_id,
                "resolved_model_id": self.resolved_model_id,
            },
            "base": {"base_url": self.base_url},
            "reasoning": {"effort": self.reasoning_effort},
            "pricing": pricing.to_mapping(),
            "timestamps": {
                "started_at_utc": self.started_at_utc,
                "completed_at_utc": self.completed_at_utc,
            },
            "gates": None if gates is None else gates.to_mapping(),
            "call_count": self.call_count,
            "calls": [value.to_mapping() for value in call_records],
            "usage": UsageSummary().to_mapping()
            if usage is None
            else usage.to_mapping(),
            "cost": CostSummary().to_mapping() if cost is None else cost.to_mapping(),
            "refs": [value.to_mapping() for value in references],
        }


@dataclass(frozen=True, slots=True)
class ExportVersionReference:
    """Typed immutable version reference carried by an export capture."""

    version_id: str
    version_number: int

    def to_mapping(self) -> dict[str, object]:
        return {
            "version_id": self.version_id,
            "version_number": self.version_number,
        }


@dataclass(frozen=True, slots=True)
class ExportContentReference:
    """Typed local-relative file reference for one captured export."""

    kind: str = "local_relative"
    value: str = "exports/marketing-brief.md"

    def to_mapping(self) -> dict[str, str]:
        return {"kind": self.kind, "value": self.value}


def _validate_version_reference(value: ExportVersionReference) -> None:
    _safe_id(value.version_id, "version_id")
    if value.version_number < 1 or type(value.version_number) is not int:
        raise ValueError("version_number must be a positive int")


def _validate_server_file_name(value: object, brief_kind: str) -> None:
    if (
        type(value) is not str
        or not value
        or len(value) > _EXPORT_SERVER_FILE_NAME_MAX_LENGTH
    ):
        raise ValueError("server_file_name must be a bounded basename")
    if value in {".", ".."} or "/" in value or "\\" in value:
        raise ValueError("server_file_name must be a basename")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError("server_file_name contains control characters")
    if not value.lower().endswith(".md"):
        raise ValueError("server_file_name must be Markdown")
    marker = "marketing" if brief_kind == "marketing" else "xiaohongshu"
    if marker not in value.casefold():
        raise ValueError("server_file_name does not match the brief kind")


@dataclass(frozen=True, slots=True)
class CaptureExport:
    """Command carrying one sanitized immutable Markdown export capture."""

    sample_id: str = _SAMPLE_ID
    attempt_id: str = _ATTEMPT_ID
    task_id: str | None = None
    task_revision: int | None = None
    result_id: str | None = None
    result_revision: int | None = None
    export_snapshot_id: str = "export-P2-P01-A1"
    brief_kind: str = "marketing"
    brief_version: ExportVersionReference = field(
        default_factory=lambda: ExportVersionReference("brief-P01-v1", 1)
    )
    upstream_versions: tuple[ExportVersionReference, ...] = ()
    exported_at: datetime | str = "2026-08-31T00:02:00Z"
    file_name: str = "marketing-brief.md"
    server_file_name: str = "marketing-brief.md"
    template_version: str = _EXPORT_TEMPLATE_VERSION
    media_type: str = _EXPORT_MEDIA_TYPE
    content_reference: ExportContentReference = field(
        default_factory=ExportContentReference
    )
    content_bytes: bytes = b"# Marketing Brief\n"
    capture_method: str = _EXPORT_CAPTURE_METHOD
    record_type: str = _EXPORT_RECORD_TYPE
    immutable: bool = True

    def to_mapping(self) -> dict[str, object]:
        """Return export metadata without content bytes or filesystem paths."""

        return {
            "record_type": self.record_type,
            "sample_id": self.sample_id,
            "attempt_id": self.attempt_id,
            "task": {
                "task_id": self.task_id,
                "revision": self.task_revision,
            },
            "result": {
                "result_id": self.result_id,
                "revision": self.result_revision,
            },
            "export_snapshot_id": self.export_snapshot_id,
            "brief_kind": self.brief_kind,
            "brief_version": self.brief_version.to_mapping(),
            "upstream_versions": tuple(
                value.to_mapping() for value in self.upstream_versions
            ),
            "exported_at": _timestamp(self.exported_at, "exported_at"),
            "file_name": self.file_name,
            "server_file_name": self.server_file_name,
            "template_version": self.template_version,
            "media_type": self.media_type,
            "content_reference": self.content_reference.to_mapping(),
            "byte_count": len(self.content_bytes),
            "capture_method": self.capture_method,
            "immutable": self.immutable,
        }


@dataclass(frozen=True, slots=True)
class ReviewDimension:
    """One independently scored P0 human-review dimension."""

    name: str
    decision: str
    critical: bool

    def to_mapping(self) -> dict[str, object]:
        return {
            "name": self.name,
            "decision": self.decision,
            "critical": self.critical,
        }


@dataclass(frozen=True, slots=True)
class RecordReview:
    """Command carrying one immutable, sanitized P0 human review."""

    sample_id: str = _SAMPLE_ID
    attempt_id: str = _ATTEMPT_ID
    task_id: str | None = None
    task_revision: int | None = None
    result_id: str | None = None
    result_revision: int | None = None
    review_id: str = "review-P2-P01-A1"
    captured_export_snapshot_ids: tuple[str, ...] = ()
    reviewer_role: str = "author_operator"
    reviewed_at: datetime | str = "2026-08-31T00:03:00Z"
    dimensions: tuple[ReviewDimension, ...] | None = None
    overall: str | None = None
    rationale: str | None = None
    notes: tuple[str, ...] = ()
    material_edits: tuple[str, ...] = ()
    record_type: str = _REVIEW_RECORD_TYPE
    immutable: bool = True

    def to_mapping(self) -> dict[str, object]:
        return {
            "record_type": self.record_type,
            "sample_id": self.sample_id,
            "attempt_id": self.attempt_id,
            "task": {
                "task_id": self.task_id,
                "revision": self.task_revision,
            },
            "result": {
                "result_id": self.result_id,
                "revision": self.result_revision,
            },
            "review_id": self.review_id,
            "captured_export_snapshot_ids": list(self.captured_export_snapshot_ids),
            "reviewer_role": self.reviewer_role,
            "reviewed_at": _timestamp(self.reviewed_at, "reviewed_at"),
            "dimensions": []
            if self.dimensions is None
            else [value.to_mapping() for value in self.dimensions],
            "overall": self.overall,
            "rationale": self.rationale,
            "notes": list(self.notes),
            "material_edits": list(self.material_edits),
            "immutable": self.immutable,
        }


class FinalDisposition(StrEnum):
    """Explicit terminal P2 classifications; no exclusion disposition exists."""

    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class FinalizationGates:
    """Fixed automated gates required before a qualifying PASS."""

    schema: bool = True
    domain: bool = True
    persistence: bool = True
    export: bool = True


@dataclass(frozen=True, slots=True)
class FinalizationCost:
    """Known actual cost and owner cap bound to one pricing reservation."""

    actual_micro_usd: int | UnknownValue
    owner_cap_micro_usd: int | None
    reservation_ref: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "actual_micro_usd",
            _observed_value(self.actual_micro_usd, "actual_micro_usd"),
        )
        owner_cap = _nonnegative_int(self.owner_cap_micro_usd, "owner_cap_micro_usd")
        if owner_cap <= 0:
            raise ValueError("owner_cap_micro_usd must be positive")
        object.__setattr__(self, "owner_cap_micro_usd", owner_cap)
        object.__setattr__(
            self, "reservation_ref", _safe_id(self.reservation_ref, "reservation_ref")
        )


@dataclass(frozen=True, slots=True)
class FinalizationExecution:
    """Bounded execution counters; retries and recovery cannot be hidden."""

    call_count: int = 5
    retry_count: int = 0
    recovery_count: int = 0
    replay_count: int = 0
    fallback_count: int = 0
    manual_intervention_count: int = 0


@dataclass(frozen=True, slots=True)
class FinalizeAttempt:
    """Command carrying one explicit terminal attempt classification."""

    sample_id: str = _SAMPLE_ID
    attempt_id: str = _ATTEMPT_ID
    task_id: str | None = None
    task_revision: int | None = None
    result_id: str | None = None
    result_revision: int | None = None
    outcome: FinalDisposition | str | None = None
    reason_code: str | None = None
    approved_review_id: str | None = None
    selected_export_snapshot_ids: tuple[str, ...] = ()
    automated_gates: FinalizationGates | None = None
    cost: FinalizationCost | None = None
    execution: FinalizationExecution | None = None
    immutable: bool = True

    def to_mapping(self) -> dict[str, object]:
        outcome = (
            self.outcome.value
            if isinstance(self.outcome, FinalDisposition)
            else self.outcome
        )
        return {
            "record_type": "attempt_outcome",
            "sample_id": self.sample_id,
            "attempt_id": self.attempt_id,
            "task": {
                "task_id": self.task_id,
                "revision": self.task_revision,
            },
            "result": {
                "result_id": self.result_id,
                "revision": self.result_revision,
            },
            "outcome": outcome,
            "reason_code": self.reason_code,
            "approved_review_id": self.approved_review_id,
            "selected_export_snapshot_ids": list(self.selected_export_snapshot_ids),
            "automated_gates": None
            if self.automated_gates is None
            else {
                "schema": self.automated_gates.schema,
                "domain": self.automated_gates.domain,
                "persistence": self.automated_gates.persistence,
                "export": self.automated_gates.export,
            },
            "cost": {
                "actual_micro_usd": _serialize_observed(
                    UnknownValue.NOT_EXPOSED
                    if self.cost is None
                    else self.cost.actual_micro_usd
                ),
                "owner_cap_micro_usd": _serialize_observed(
                    None if self.cost is None else self.cost.owner_cap_micro_usd
                ),
                "reservation_ref": _serialize_unknown(
                    None if self.cost is None else self.cost.reservation_ref
                ),
            },
            "execution": None
            if self.execution is None
            else {
                "call_count": self.execution.call_count,
                "retry_count": self.execution.retry_count,
                "recovery_count": self.execution.recovery_count,
                "replay_count": self.execution.replay_count,
                "fallback_count": self.execution.fallback_count,
                "manual_intervention_count": self.execution.manual_intervention_count,
            },
            "immutable": self.immutable,
        }


def _final_disposition(value: FinalDisposition | str) -> FinalDisposition:
    if isinstance(value, FinalDisposition):
        return value
    if type(value) is str:
        try:
            return FinalDisposition(value)
        except ValueError:
            pass
    raise ValueError("outcome must be PASS, FAIL, or BLOCKED")


def _empty_exports() -> dict[str, Mapping[str, object]]:
    return {}


@dataclass(frozen=True, slots=True)
class AttemptArtifactSnapshot(Mapping[str, object]):
    """Immutable projection returned by :meth:`PilotAttemptArtifacts.read`."""

    identity: Mapping[str, object]
    run: Mapping[str, object] | None
    review: str = "PENDING"
    artifact_root: Path | None = field(default=None, repr=False, compare=False)
    exports: Mapping[str, Mapping[str, object]] = field(default_factory=_empty_exports)
    review_record: Mapping[str, object] | None = None
    outcome: str | None = None
    outcome_record: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "identity", MappingProxyType(dict(self.identity)))
        if self.run is not None:
            object.__setattr__(self, "run", MappingProxyType(dict(self.run)))
        object.__setattr__(self, "exports", _freeze_mapping(self.exports))
        if self.review not in {"PENDING", "APPROVED", "REJECTED"}:
            raise ValueError("review must be PENDING, APPROVED, or REJECTED")
        if self.review_record is not None:
            object.__setattr__(
                self, "review_record", _freeze_mapping(self.review_record)
            )
        if self.outcome is not None and self.outcome not in {
            value.value for value in FinalDisposition
        }:
            raise ValueError("outcome must be PASS, FAIL, or BLOCKED")
        if self.outcome_record is not None:
            object.__setattr__(
                self, "outcome_record", _freeze_mapping(self.outcome_record)
            )
        if (self.outcome is None) != (self.outcome_record is None):
            raise ValueError("outcome and outcome_record must be paired")

    def __getitem__(self, key: str) -> object:
        values: dict[str, object] = {
            "identity": self.identity,
            "run": self.run,
            "review": self.review,
            "exports": self.exports,
            "review_record": self.review_record,
            "outcome": self.outcome,
            "outcome_record": self.outcome_record,
        }
        return values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(
            (
                "identity",
                "run",
                "review",
                "exports",
                "review_record",
                "outcome",
                "outcome_record",
            )
        )

    def __len__(self) -> int:
        return 7

    @property
    def review_status(self) -> str:
        return self.review


def _freeze_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    """Recursively freeze an in-memory sanitized projection."""

    frozen: dict[str, object] = {}
    for key, item in value.items():
        if type(key) is not str:
            raise TypeError("projection keys must be exact strings")
        if isinstance(item, Mapping):
            nested = cast(Mapping[str, object], item)
            frozen[key] = _freeze_mapping(nested)
        elif isinstance(item, list):
            entries = cast(list[object], item)
            frozen[key] = tuple(
                _freeze_mapping(cast(Mapping[str, object], entry))
                if isinstance(entry, Mapping)
                else entry
                for entry in entries
            )
        elif isinstance(item, tuple):
            entries = cast(tuple[object, ...], item)
            frozen[key] = tuple(
                _freeze_mapping(cast(Mapping[str, object], entry))
                if isinstance(entry, Mapping)
                else entry
                for entry in entries
            )
        else:
            frozen[key] = item
    return MappingProxyType(frozen)


def _path_value(value: object, field_name: str) -> Path:
    if isinstance(value, Path):
        return value
    if type(value) is str:
        return Path(value)
    raise TypeError(f"{field_name} must be a Path or string")


def _json_bytes(value: Mapping[str, object]) -> bytes:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError):
        raise ValueError("artifact record contains unsupported values") from None
    return (encoded + "\n").encode("utf-8")


def _is_symlink(path: Path) -> bool:
    try:
        return stat.S_ISLNK(os.lstat(path).st_mode)
    except FileNotFoundError:
        return False
    except OSError:
        raise AttemptArtifactError(
            ArtifactErrorCode.ARTIFACT_IO_ERROR, "inspect"
        ) from None


def _safe_read_json(path: Path) -> dict[str, object]:
    try:
        raw = path.read_bytes()
        parsed = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read") from None
    if not isinstance(parsed, dict):
        raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
    return cast(dict[str, object], parsed)


class PilotAttemptArtifacts:
    """Reserve and inspect one exact P2 attempt artifact root."""

    def __init__(
        self, repository_root: Path | str, approved_parent: Path | str
    ) -> None:
        self._repository_root = self._validate_directory(
            repository_root, "repository_root", require_exists=True
        )
        self._approved_parent = self._validate_directory(
            approved_parent, "approved_parent", require_exists=True
        )
        if (
            self._approved_parent == self._repository_root
            or self._approved_parent.is_relative_to(self._repository_root)
        ):
            raise AttemptArtifactError(ArtifactErrorCode.ROOT_NOT_ALLOWED, "configure")
        self._roots: dict[str, Path] = {}
        self._exports: dict[tuple[str, str], Mapping[str, object]] = {}

    @staticmethod
    def _validate_directory(
        value: Path | str, field_name: str, *, require_exists: bool
    ) -> Path:
        path = _path_value(value, field_name)
        if not path.is_absolute():
            raise AttemptArtifactError(ArtifactErrorCode.INVALID_ROOT, "configure")
        if _is_symlink(path):
            raise AttemptArtifactError(ArtifactErrorCode.ROOT_NOT_ALLOWED, "configure")
        if require_exists and (not path.exists() or not path.is_dir()):
            raise AttemptArtifactError(ArtifactErrorCode.INVALID_ROOT, "configure")
        try:
            resolved = path.resolve(strict=require_exists)
        except OSError:
            raise AttemptArtifactError(
                ArtifactErrorCode.ROOT_NOT_ALLOWED, "configure"
            ) from None
        if _is_symlink(resolved):
            raise AttemptArtifactError(ArtifactErrorCode.ROOT_NOT_ALLOWED, "configure")
        return resolved

    def apply(
        self,
        command: ReserveAttempt
        | RecordRun
        | CaptureExport
        | RecordReview
        | FinalizeAttempt,
    ) -> AttemptArtifactSnapshot | None:
        """Apply one typed reservation, run, export, review, or finalization."""

        if type(command) is ReserveAttempt:
            return self._reserve(command)
        if type(command) is RecordRun:
            self._record_run(command)
            return None
        if type(command) is CaptureExport:
            return self._capture_export(command)
        if type(command) is RecordReview:
            return self._record_review(command)
        if type(command) is FinalizeAttempt:
            return self._finalize_attempt(command)
        raise AttemptArtifactError(ArtifactErrorCode.INVALID_COMMAND, "apply")

    def read(self, attempt_id: str) -> AttemptArtifactSnapshot:
        """Read durable identity/run/export/review/outcome metadata."""

        safe_attempt_id = _safe_id(attempt_id, "attempt_id")
        root = self._roots.get(safe_attempt_id)
        if root is None:
            root = self._find_root(safe_attempt_id)
        if root is None:
            raise AttemptArtifactError(ArtifactErrorCode.ATTEMPT_NOT_FOUND, "read")
        identity = _safe_read_json(root / "identity.json")
        run_path = root / "run.json"
        run = None if not run_path.exists() else _safe_read_json(run_path)
        exports = self._load_exports(root, safe_attempt_id)
        review_path = root / "review.json"
        review_record: dict[str, object] | None = None
        review_state = "PENDING"
        if review_path.exists() or _is_symlink(review_path):
            if _is_symlink(review_path):
                raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
            review_record = _safe_read_json(review_path)
            candidate_state = review_record.get("overall")
            if candidate_state not in _REVIEW_STATES:
                raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
            review_state = cast(str, candidate_state)
        outcome_path = root / "outcome.json"
        outcome_record: dict[str, object] | None = None
        outcome: str | None = None
        if outcome_path.exists() or _is_symlink(outcome_path):
            if _is_symlink(outcome_path):
                raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
            outcome_record = _safe_read_json(outcome_path)
            candidate_outcome = outcome_record.get("outcome")
            if candidate_outcome not in {value.value for value in FinalDisposition}:
                raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
            outcome = cast(str, candidate_outcome)
        return AttemptArtifactSnapshot(
            identity,
            run,
            review_state,
            root,
            exports,
            review_record,
            outcome,
            outcome_record,
        )

    def _reserve(self, command: ReserveAttempt) -> AttemptArtifactSnapshot:
        if command.sample_id != _SAMPLE_ID or command.attempt_id != _ATTEMPT_ID:
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "reserve")
        root = self._validate_attempt_root(command.artifact_root)
        self._mkdir_parents(root.parent)
        try:
            root.mkdir(mode=0o700, exist_ok=False)
        except FileExistsError:
            raise AttemptArtifactError(
                ArtifactErrorCode.ROOT_EXISTS, "reserve"
            ) from None
        except OSError:
            raise AttemptArtifactError(
                ArtifactErrorCode.ARTIFACT_IO_ERROR, "reserve"
            ) from None
        try:
            exports = root / "exports"
            exports.mkdir(mode=0o700, exist_ok=False)
            identity = {
                "record_type": _IDENTITY_RECORD_TYPE,
                "sample_id": command.sample_id,
                "attempt_id": command.attempt_id,
                "immutable": True,
            }
            _exclusive_write(root / "identity.json", identity)
            self._roots[command.attempt_id] = root
            return AttemptArtifactSnapshot(identity, None, "PENDING", root)
        except AttemptArtifactError:
            raise
        except OSError:
            raise AttemptArtifactError(
                ArtifactErrorCode.ARTIFACT_IO_ERROR, "reserve"
            ) from None

    def _record_run(self, command: RecordRun) -> None:
        if command.sample_id != _SAMPLE_ID or command.attempt_id != _ATTEMPT_ID:
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "record")
        root = self._roots.get(command.attempt_id)
        if root is None:
            root = self._find_root(command.attempt_id)
        if root is None:
            raise AttemptArtifactError(ArtifactErrorCode.ATTEMPT_NOT_FOUND, "record")
        identity = _safe_read_json(root / "identity.json")
        if (
            identity.get("sample_id") != command.sample_id
            or identity.get("attempt_id") != command.attempt_id
        ):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "record")
        run_path = root / "run.json"
        if run_path.exists() or _is_symlink(run_path):
            raise AttemptArtifactError(ArtifactErrorCode.RECORD_EXISTS, "record")
        _exclusive_write(run_path, command.to_mapping())

    def _capture_export(self, command: CaptureExport) -> AttemptArtifactSnapshot:
        self._validate_capture(command)
        root = self._roots.get(command.attempt_id)
        if root is None:
            root = self._find_root(command.attempt_id)
        if root is None:
            raise AttemptArtifactError(ArtifactErrorCode.ATTEMPT_NOT_FOUND, "capture")
        identity = _safe_read_json(root / "identity.json")
        if (
            identity.get("sample_id") != command.sample_id
            or identity.get("attempt_id") != command.attempt_id
        ):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "capture")
        run_path = root / "run.json"
        if not run_path.exists() or _is_symlink(run_path):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "capture")
        run = _safe_read_json(run_path)
        if not self._run_matches_capture(run, command):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "capture")
        self._ensure_not_terminal(root, "capture")

        self._load_exports(root, command.attempt_id)

        kind = command.brief_kind
        key = (command.attempt_id, kind)
        existing = self._exports.get(key)
        if existing is not None:
            if self._export_basis(existing) != self._export_basis(command.to_mapping()):
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "capture"
                )
            raise AttemptArtifactError(ArtifactErrorCode.RECORD_EXISTS, "capture")

        exports_dir = root / "exports"
        if _is_symlink(exports_dir) or not exports_dir.is_dir():
            raise AttemptArtifactError(ArtifactErrorCode.ROOT_NOT_ALLOWED, "capture")
        export_path = root / command.content_reference.value
        if export_path.exists() or _is_symlink(export_path):
            raise AttemptArtifactError(ArtifactErrorCode.RECORD_EXISTS, "capture")
        metadata_path = root / "exports" / _EXPORT_METADATA_FILE_NAMES[kind]
        if metadata_path.exists() or _is_symlink(metadata_path):
            raise AttemptArtifactError(ArtifactErrorCode.RECORD_EXISTS, "capture")
        _exclusive_write_bytes(export_path, command.content_bytes)
        projection = command.to_mapping()
        _exclusive_write(metadata_path, projection)
        self._exports[key] = projection
        exports = self._load_exports(root, command.attempt_id)
        return AttemptArtifactSnapshot(identity, run, "PENDING", root, exports)

    def _record_review(self, command: RecordReview) -> AttemptArtifactSnapshot:
        self._validate_review(command)
        root = self._roots.get(command.attempt_id)
        if root is None:
            root = self._find_root(command.attempt_id)
        if root is None:
            raise AttemptArtifactError(ArtifactErrorCode.ATTEMPT_NOT_FOUND, "review")
        self._ensure_not_terminal(root, "review")
        identity = _safe_read_json(root / "identity.json")
        if (
            identity.get("sample_id") != command.sample_id
            or identity.get("attempt_id") != command.attempt_id
        ):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "review")
        run_path = root / "run.json"
        if not run_path.exists() or _is_symlink(run_path):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "review")
        run = _safe_read_json(run_path)
        if not self._run_matches_review(run, command):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "review")

        exports = self._load_exports(root, command.attempt_id)
        selected_exports = self._review_export_selection(command, exports)
        self._validate_review_dimensions(command, selected_exports)
        reviewed_at = _timestamp(command.reviewed_at, "reviewed_at")
        if reviewed_at is None:
            raise AttemptArtifactError(ArtifactErrorCode.INVALID_COMMAND, "review")
        try:
            reviewed_moment = datetime.fromisoformat(
                reviewed_at[:-1] + "+00:00"
                if reviewed_at.endswith("Z")
                else reviewed_at
            )
            for export in selected_exports:
                exported_at = export.get("exported_at")
                if type(exported_at) is not str:
                    raise ValueError("export timestamp missing")
                exported_moment = datetime.fromisoformat(
                    exported_at[:-1] + "+00:00"
                    if exported_at.endswith("Z")
                    else exported_at
                )
                if reviewed_moment <= exported_moment:
                    raise AttemptArtifactError(
                        ArtifactErrorCode.IDENTITY_MISMATCH, "review"
                    )
        except AttemptArtifactError:
            raise
        except (TypeError, ValueError, OverflowError):
            raise AttemptArtifactError(
                ArtifactErrorCode.INVALID_COMMAND, "review"
            ) from None

        review_path = root / "review.json"
        if review_path.exists() or _is_symlink(review_path):
            raise AttemptArtifactError(ArtifactErrorCode.RECORD_EXISTS, "review")
        record = command.to_mapping()
        _exclusive_write(review_path, record)
        review_record = _safe_read_json(review_path)
        return AttemptArtifactSnapshot(
            identity,
            run,
            cast(str, record["overall"]),
            root,
            exports,
            review_record,
        )

    def _finalize_attempt(self, command: FinalizeAttempt) -> AttemptArtifactSnapshot:
        self._validate_finalize(command)
        root = self._roots.get(command.attempt_id)
        if root is None:
            root = self._find_root(command.attempt_id)
        if root is None:
            raise AttemptArtifactError(ArtifactErrorCode.ATTEMPT_NOT_FOUND, "finalize")
        identity = _safe_read_json(root / "identity.json")
        if (
            identity.get("sample_id") != command.sample_id
            or identity.get("attempt_id") != command.attempt_id
        ):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        run_path = root / "run.json"
        if not run_path.exists() or _is_symlink(run_path):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        run = _safe_read_json(run_path)
        if not self._run_matches_finalize(run, command):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")

        exports = self._load_exports(root, command.attempt_id)
        selected_exports = self._finalize_export_selection(
            command.selected_export_snapshot_ids, exports
        )
        review_path = root / "review.json"
        review_record: dict[str, object] | None = None
        review_state = "PENDING"
        if review_path.exists() or _is_symlink(review_path):
            if _is_symlink(review_path):
                raise AttemptArtifactError(
                    ArtifactErrorCode.ARTIFACT_CORRUPT, "finalize"
                )
            review_record = _safe_read_json(review_path)
            review_overall = review_record.get("overall")
            if review_overall not in _REVIEW_STATES:
                raise AttemptArtifactError(
                    ArtifactErrorCode.ARTIFACT_CORRUPT, "finalize"
                )
            review_state = cast(str, review_overall)
        self._validate_finalize_evidence(
            command,
            run,
            review_record,
            selected_exports,
            root,
        )
        outcome_path = root / "outcome.json"
        if outcome_path.exists() or _is_symlink(outcome_path):
            raise AttemptArtifactError(ArtifactErrorCode.RECORD_EXISTS, "finalize")
        record = command.to_mapping()
        _exclusive_write(outcome_path, record)
        outcome_record = _safe_read_json(outcome_path)
        outcome = cast(str, record["outcome"])
        return AttemptArtifactSnapshot(
            identity,
            run,
            review_state,
            root,
            exports,
            review_record,
            outcome,
            outcome_record,
        )

    @staticmethod
    def _ensure_not_terminal(root: Path, operation: str) -> None:
        outcome_path = root / "outcome.json"
        if outcome_path.exists() or _is_symlink(outcome_path):
            raise AttemptArtifactError(ArtifactErrorCode.RECORD_EXISTS, operation)

    @staticmethod
    def _validate_finalize(command: FinalizeAttempt) -> None:
        try:
            if command.sample_id != _SAMPLE_ID or command.attempt_id != _ATTEMPT_ID:
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                )
            _safe_id(command.sample_id, "sample_id")
            _safe_id(command.attempt_id, "attempt_id")
            if command.outcome is None:
                raise ValueError("outcome is required")
            disposition = _final_disposition(command.outcome)
            if command.task_id is None:
                if disposition == FinalDisposition.PASS:
                    raise AttemptArtifactError(
                        ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                    )
            else:
                _safe_id(command.task_id, "task_id")
                _nonnegative_int(command.task_revision, "task_revision")
            if command.result_id is None:
                if disposition == FinalDisposition.PASS:
                    raise AttemptArtifactError(
                        ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                    )
            else:
                _safe_id(command.result_id, "result_id")
                _nonnegative_int(command.result_revision, "result_revision")
            if command.reason_code is None:
                raise ValueError("reason_code is required")
            _safe_id(command.reason_code, "reason_code")
            if command.reason_code not in _FINAL_REASON_CODES:
                raise ValueError("reason_code is not fixed")
            if (
                disposition != FinalDisposition.PASS
                and (command.task_id is None or command.result_id is None)
                and command.reason_code != "execution_not_qualified"
            ):
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                )
            if disposition == FinalDisposition.PASS:
                if command.reason_code != "qualifying_approved_export":
                    raise ValueError("PASS reason_code is invalid")
            elif command.reason_code == "qualifying_approved_export":
                raise ValueError("non-PASS reason_code is invalid")
            if command.approved_review_id is not None:
                _safe_id(command.approved_review_id, "approved_review_id")
            if type(command.selected_export_snapshot_ids) is not tuple:
                raise TypeError("selected export ids must be an exact tuple")
            seen_export_ids: set[str] = set()
            for export_id in command.selected_export_snapshot_ids:
                safe_export_id = _safe_id(export_id, "selected_export_snapshot_id")
                if safe_export_id in seen_export_ids:
                    raise ValueError("selected export ids must be unique")
                seen_export_ids.add(safe_export_id)
            if type(command.automated_gates) is not FinalizationGates:
                raise TypeError("automated_gates must be typed")
            for gate_name in ("schema", "domain", "persistence", "export"):
                if type(getattr(command.automated_gates, gate_name)) is not bool:
                    raise TypeError("automated gates must be bool")
            if type(command.cost) is not FinalizationCost:
                raise TypeError("cost must be typed")
            if type(command.cost.actual_micro_usd) not in (int, UnknownValue):
                raise TypeError("actual_micro_usd must be observed or typed unknown")
            if type(command.cost.owner_cap_micro_usd) is not int:
                raise TypeError("owner_cap_micro_usd must be a known int")
            if (
                type(command.cost.actual_micro_usd) is int
                and command.cost.actual_micro_usd < 0
            ):
                raise ValueError("actual_micro_usd must not be negative")
            if (
                type(command.cost.owner_cap_micro_usd) is int
                and command.cost.owner_cap_micro_usd < 0
            ):
                raise ValueError("owner_cap_micro_usd must not be negative")
            _safe_id(command.cost.reservation_ref, "reservation_ref")
            if type(command.execution) is not FinalizationExecution:
                raise TypeError("execution must be typed")
            for field_name in (
                "call_count",
                "retry_count",
                "recovery_count",
                "replay_count",
                "fallback_count",
                "manual_intervention_count",
            ):
                _nonnegative_int(getattr(command.execution, field_name), field_name)
            if command.immutable is not True:
                raise ValueError("outcome must be immutable")
        except AttemptArtifactError:
            raise
        except (TypeError, ValueError):
            raise AttemptArtifactError(
                ArtifactErrorCode.INVALID_COMMAND, "finalize"
            ) from None

    @staticmethod
    def _run_matches_finalize(
        run: Mapping[str, object], command: FinalizeAttempt
    ) -> bool:
        if run.get("sample_id") != command.sample_id:
            return False
        if run.get("attempt_id") != command.attempt_id:
            return False
        return run.get("task") == {
            "task_id": command.task_id,
            "revision": command.task_revision,
        } and run.get("result") == {
            "result_id": command.result_id,
            "revision": command.result_revision,
        }

    @staticmethod
    def _finalize_export_selection(
        selected_ids: tuple[str, ...],
        exports: Mapping[str, Mapping[str, object]],
    ) -> tuple[Mapping[str, object], ...]:
        by_id: dict[str, Mapping[str, object]] = {}
        for projection in exports.values():
            export_id = projection.get("export_snapshot_id")
            if type(export_id) is str:
                by_id[export_id] = projection
        selected: list[Mapping[str, object]] = []
        for export_id in selected_ids:
            projection = by_id.get(export_id)
            if projection is None:
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                )
            selected.append(projection)
        return tuple(selected)

    @staticmethod
    def _validate_finalize_evidence(
        command: FinalizeAttempt,
        run: Mapping[str, object],
        review_record: Mapping[str, object] | None,
        selected_exports: tuple[Mapping[str, object], ...],
        root: Path,
    ) -> None:
        if command.outcome is None:
            raise AttemptArtifactError(ArtifactErrorCode.INVALID_COMMAND, "finalize")
        disposition = _final_disposition(command.outcome)
        gates = command.automated_gates
        cost = command.cost
        execution = command.execution
        if (
            type(gates) is not FinalizationGates
            or type(cost) is not FinalizationCost
            or type(execution) is not FinalizationExecution
        ):
            raise AttemptArtifactError(ArtifactErrorCode.INVALID_COMMAND, "finalize")
        if disposition != FinalDisposition.PASS:
            if (
                command.selected_export_snapshot_ids
                or command.approved_review_id is not None
            ):
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                )
            reason_code = command.reason_code
            if reason_code == "cost_cap_exceeded":
                if disposition != FinalDisposition.BLOCKED:
                    raise AttemptArtifactError(
                        ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                    )
            elif (
                reason_code
                in {
                    "review_rejected",
                    "automated_gate_failed",
                    "execution_not_qualified",
                    "missing_export",
                }
                and disposition != FinalDisposition.FAIL
            ):
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                )
            if reason_code == "review_rejected":
                reviewed_exports = (
                    None
                    if review_record is None
                    else review_record.get("captured_export_snapshot_ids")
                )
                if (
                    review_record is None
                    or review_record.get("overall") != "REJECTED"
                    or type(reviewed_exports) is not list
                    or not reviewed_exports
                ):
                    raise AttemptArtifactError(
                        ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                    )
            elif reason_code == "automated_gate_failed":
                run_gates = run.get("gates")
                if not isinstance(run_gates, Mapping):
                    raise AttemptArtifactError(
                        ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                    )
                run_gate_values = cast(Mapping[str, object], run_gates)
                if (
                    all((gates.schema, gates.domain, gates.persistence, gates.export))
                    or all(
                        run_gate_values.get(name) is True
                        for name in ("schema", "domain", "persistence", "export")
                    )
                    or any(
                        getattr(gates, name) is not run_gate_values.get(name)
                        for name in ("schema", "domain", "persistence", "export")
                    )
                ):
                    raise AttemptArtifactError(
                        ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                    )
            elif reason_code == "cost_cap_exceeded":
                pricing = run.get("pricing")
                run_cost = run.get("cost")
                run_pricing = None
                if isinstance(pricing, Mapping):
                    run_pricing = cast(Mapping[str, object], pricing).get("record_id")
                run_actual = (
                    None
                    if not isinstance(run_cost, Mapping)
                    else cast(Mapping[str, object], run_cost).get("actual_micro_usd")
                )
                if (
                    type(cost.actual_micro_usd) is not int
                    or type(cost.owner_cap_micro_usd) is not int
                    or cost.actual_micro_usd <= cost.owner_cap_micro_usd
                    or run_pricing != cost.reservation_ref
                    or run_actual != cost.actual_micro_usd
                ):
                    raise AttemptArtifactError(
                        ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                    )
            elif reason_code == "execution_not_qualified":
                run_call_count = run.get("call_count")
                run_calls = run.get("calls")
                run_not_qualified = (
                    type(run_call_count) is not int
                    or run_call_count != 5
                    or type(run_calls) not in (list, tuple)
                    or len(cast(list[object] | tuple[object, ...], run_calls)) != 5
                )
                command_qualified = (
                    execution.call_count == 5
                    and execution.retry_count == 0
                    and execution.recovery_count == 0
                    and execution.replay_count == 0
                    and execution.fallback_count == 0
                    and execution.manual_intervention_count == 0
                )
                if not run_not_qualified and command_qualified:
                    raise AttemptArtifactError(
                        ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                    )
            elif reason_code == "missing_export":
                run_gates = run.get("gates")
                if not isinstance(run_gates, Mapping):
                    raise AttemptArtifactError(
                        ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                    )
                run_gate_values = cast(Mapping[str, object], run_gates)
                if (
                    run_gate_values.get("export") is not False
                    or gates.export is not False
                    or any(
                        (root / "exports" / file_name).exists()
                        for file_name in _EXPORT_METADATA_FILE_NAMES.values()
                    )
                ):
                    raise AttemptArtifactError(
                        ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                    )
            return
        if not selected_exports or command.approved_review_id is None:
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        if review_record is None or review_record.get("overall") != "APPROVED":
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        if review_record.get("review_id") != command.approved_review_id:
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        reviewed_exports = review_record.get("captured_export_snapshot_ids")
        if type(reviewed_exports) is not list:
            raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "finalize")
        reviewed_export_values = cast(list[object], reviewed_exports)
        if any(type(export_id) is not str for export_id in reviewed_export_values):
            raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "finalize")
        reviewed_export_ids = tuple(
            cast(str, export_id) for export_id in reviewed_export_values
        )
        if set(reviewed_export_ids) != set(command.selected_export_snapshot_ids):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        if not all((gates.schema, gates.domain, gates.persistence, gates.export)):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        if (
            execution.call_count != 5
            or execution.retry_count != 0
            or execution.recovery_count != 0
            or execution.replay_count != 0
            or execution.fallback_count != 0
            or execution.manual_intervention_count != 0
        ):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        run_call_count = run.get("call_count")
        run_calls = run.get("calls")
        calls_are_sequence = type(run_calls) in (list, tuple)
        run_call_entries = (
            cast(list[object] | tuple[object, ...], run_calls)
            if calls_are_sequence
            else ()
        )
        if (
            type(run_call_count) is not int
            or run_call_count != 5
            or not calls_are_sequence
            or len(run_call_entries) != 5
        ):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        run_gates = run.get("gates")
        if not isinstance(run_gates, Mapping):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        run_gate_values = cast(Mapping[str, object], run_gates)
        # Run evidence is written before export capture, so the export gate
        # may remain false here; qualification is derived from immutable
        # captured sidecars selected above.
        for gate_name in ("schema", "domain", "persistence"):
            if run_gate_values.get(gate_name) is not True:
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                )
        pricing = run.get("pricing")
        run_cost = run.get("cost")
        if not isinstance(pricing, Mapping) or not isinstance(run_cost, Mapping):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        pricing_values = cast(Mapping[str, object], pricing)
        run_cost_values = cast(Mapping[str, object], run_cost)
        if pricing_values.get("record_id") != cost.reservation_ref:
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        if type(cost.actual_micro_usd) is int:
            actual_value: int | str = cost.actual_micro_usd
        elif isinstance(cost.actual_micro_usd, UnknownValue):
            actual_value = cost.actual_micro_usd.value
        else:
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        if run_cost_values.get("actual_micro_usd") != actual_value:
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        owner_cap = cost.owner_cap_micro_usd
        if type(owner_cap) is not int:
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        if type(cost.actual_micro_usd) is int and cost.actual_micro_usd > owner_cap:
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "finalize")
        for export in selected_exports:
            if export.get("immutable") is not True:
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                )
            reference = export.get("content_reference")
            if not isinstance(reference, Mapping):
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                )
            reference_values = cast(Mapping[str, object], reference)
            value = reference_values.get("value")
            if type(value) is not str:
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                )
            relative_value = value
            if Path(relative_value).is_absolute():
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                )
            export_path = root / relative_value
            if (
                not export_path.exists()
                or _is_symlink(export_path)
                or stat.S_IMODE(export_path.stat().st_mode) != stat.S_IRUSR
            ):
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "finalize"
                )

    @staticmethod
    def _export_basis(value: Mapping[str, object]) -> tuple[object, ...]:
        def canonical(item: object) -> object:
            if isinstance(item, Mapping):
                mapping = cast(Mapping[object, object], item)
                return tuple(
                    sorted(
                        (str(key), canonical(nested)) for key, nested in mapping.items()
                    )
                )
            if isinstance(item, (list, tuple)):
                sequence = cast(Sequence[object], item)
                return tuple(canonical(nested) for nested in sequence)
            return item

        return (
            canonical(value.get("sample_id")),
            canonical(value.get("attempt_id")),
            canonical(value.get("task")),
            canonical(value.get("result")),
            canonical(value.get("export_snapshot_id")),
            canonical(value.get("brief_kind")),
            canonical(value.get("brief_version")),
            canonical(value.get("upstream_versions")),
            canonical(value.get("exported_at")),
            canonical(value.get("file_name")),
            canonical(value.get("server_file_name")),
            canonical(value.get("template_version")),
            canonical(value.get("media_type")),
        )

    @staticmethod
    def _run_matches_capture(run: Mapping[str, object], command: CaptureExport) -> bool:
        if run.get("sample_id") != command.sample_id:
            return False
        if run.get("attempt_id") != command.attempt_id:
            return False
        task = run.get("task")
        result = run.get("result")
        return task == {
            "task_id": command.task_id,
            "revision": command.task_revision,
        } and result == {
            "result_id": command.result_id,
            "revision": command.result_revision,
        }

    @staticmethod
    def _validate_capture(command: CaptureExport) -> None:
        """Validate all capture fields before touching the destination file."""

        try:
            if command.sample_id != _SAMPLE_ID or command.attempt_id != _ATTEMPT_ID:
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "capture"
                )
            _safe_id(command.sample_id, "sample_id")
            _safe_id(command.attempt_id, "attempt_id")
            if command.task_id is None or command.result_id is None:
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "capture"
                )
            _safe_id(command.task_id, "task_id")
            _safe_id(command.result_id, "result_id")
            _nonnegative_int(command.task_revision, "task_revision")
            _nonnegative_int(command.result_revision, "result_revision")
            _safe_id(command.export_snapshot_id, "export_snapshot_id")
            if command.brief_kind not in _EXPORT_FILE_NAMES:
                raise ValueError("unsupported brief kind")
            if type(command.brief_version) is not ExportVersionReference:
                raise TypeError("brief_version must be an ExportVersionReference")
            _validate_version_reference(command.brief_version)
            if type(command.upstream_versions) is not tuple:
                raise TypeError("upstream_versions must be an exact tuple")
            for value in command.upstream_versions:
                if type(value) is not ExportVersionReference:
                    raise TypeError("upstream versions must be typed references")
                _validate_version_reference(value)
            if _timestamp(command.exported_at, "exported_at") is None:
                raise ValueError("exported_at must not be blank")
            expected_file_name = _EXPORT_FILE_NAMES[command.brief_kind]
            if command.file_name != expected_file_name:
                raise ValueError("file_name is not the fixed export name")
            _validate_server_file_name(command.server_file_name, command.brief_kind)
            if command.template_version != _EXPORT_TEMPLATE_VERSION:
                raise ValueError("template_version is unsupported")
            if command.media_type != _EXPORT_MEDIA_TYPE:
                raise ValueError("media_type is unsupported")
            if type(command.content_reference) is not ExportContentReference:
                raise TypeError("content_reference must be typed")
            expected_location = f"exports/{expected_file_name}"
            if (
                command.content_reference.kind != "local_relative"
                or command.content_reference.value != expected_location
                or Path(command.content_reference.value).is_absolute()
            ):
                raise ValueError("content_reference is not a fixed local-relative path")
            if command.capture_method != _EXPORT_CAPTURE_METHOD:
                raise ValueError("capture_method is unsupported")
            if command.record_type != _EXPORT_RECORD_TYPE:
                raise ValueError("record_type is unsupported")
            if command.immutable is not True:
                raise ValueError("capture must be immutable")
        except AttemptArtifactError:
            raise
        except (TypeError, ValueError):
            raise AttemptArtifactError(
                ArtifactErrorCode.INVALID_COMMAND, "capture"
            ) from None

        if type(command.content_bytes) is not bytes:
            raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "capture")
        if not command.content_bytes or command.content_bytes.startswith(
            b"\xef\xbb\xbf"
        ):
            raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "capture")
        if command.content_bytes.endswith(
            b"\n\n"
        ) or not command.content_bytes.endswith(b"\n"):
            raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "capture")
        try:
            command.content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise AttemptArtifactError(
                ArtifactErrorCode.ARTIFACT_CORRUPT, "capture"
            ) from None

    @staticmethod
    def _validate_review(command: RecordReview) -> None:
        try:
            if command.sample_id != _SAMPLE_ID or command.attempt_id != _ATTEMPT_ID:
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "review"
                )
            _safe_id(command.sample_id, "sample_id")
            _safe_id(command.attempt_id, "attempt_id")
            if command.task_id is None or command.result_id is None:
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "review"
                )
            _safe_id(command.task_id, "task_id")
            _safe_id(command.result_id, "result_id")
            _nonnegative_int(command.task_revision, "task_revision")
            _nonnegative_int(command.result_revision, "result_revision")
            _safe_id(command.review_id, "review_id")
            if type(command.captured_export_snapshot_ids) is not tuple:
                raise TypeError("captured export ids must be an exact tuple")
            seen_export_ids: set[str] = set()
            for export_id in command.captured_export_snapshot_ids:
                safe_export_id = _safe_id(export_id, "captured_export_snapshot_id")
                if safe_export_id in seen_export_ids:
                    raise ValueError("captured export ids must be unique")
                seen_export_ids.add(safe_export_id)
            _safe_id(command.reviewer_role, "reviewer_role")
            if command.reviewer_role not in _REVIEW_ROLES:
                raise ValueError("reviewer_role is not an approved role")
            if _timestamp(command.reviewed_at, "reviewed_at") is None:
                raise ValueError("reviewed_at must not be blank")
            if command.dimensions is None:
                raise ValueError("review dimensions are required")
            if command.overall is None or command.rationale is None:
                raise ValueError("review decision and rationale are required")
            if type(command.dimensions) is not tuple:
                raise TypeError("dimensions must be an exact tuple")
            if len(command.dimensions) != len(_REVIEW_DIMENSION_NAMES):
                raise ValueError("exactly seven review dimensions are required")
            names: list[str] = []
            for dimension in command.dimensions:
                if type(dimension) is not ReviewDimension:
                    raise TypeError("dimensions must be typed ReviewDimension values")
                if dimension.name not in _REVIEW_DIMENSION_NAMES:
                    raise ValueError("unknown review dimension")
                if dimension.name in names:
                    raise ValueError("review dimensions must be unique")
                if dimension.decision not in _REVIEW_DECISIONS:
                    raise ValueError("unknown review dimension decision")
                if type(dimension.critical) is not bool:
                    raise TypeError("dimension critical flag must be bool")
                names.append(dimension.name)
            if tuple(names) != _REVIEW_DIMENSION_NAMES:
                raise ValueError("review dimensions must use the fixed order")
            if command.overall not in _REVIEW_STATES:
                raise ValueError("unknown review state")
            expected_rationale = (
                "approved_all_applicable_critical_dimensions_pass"
                if command.overall == "APPROVED"
                else "rejected_critical_dimension_or_export"
            )
            if command.rationale != expected_rationale:
                raise ValueError("rationale does not match review state")
            if command.rationale not in _REVIEW_RATIONALES:
                raise ValueError("unknown rationale")
            if command.record_type != _REVIEW_RECORD_TYPE:
                raise ValueError("record_type is unsupported")
            if command.immutable is not True:
                raise ValueError("review must be immutable")
            PilotAttemptArtifacts._validate_review_texts(command.notes, "notes")
            PilotAttemptArtifacts._validate_review_texts(
                command.material_edits, "material_edits"
            )
        except AttemptArtifactError:
            raise
        except (TypeError, ValueError):
            raise AttemptArtifactError(
                ArtifactErrorCode.INVALID_COMMAND, "review"
            ) from None

    @staticmethod
    def _validate_review_texts(value: object, field_name: str) -> None:
        if type(value) is not tuple:
            raise TypeError(f"{field_name} must be an exact tuple")
        texts = cast(tuple[object, ...], value)
        if len(texts) > 8:
            raise ValueError(f"{field_name} has too many entries")
        for item in texts:
            if type(item) is not str:
                raise ValueError(f"{field_name} contains unsupported text")
            text = item
            if not text.strip() or len(text) > 240:
                raise ValueError(f"{field_name} contains unsupported text")
            lowered = text.casefold()
            if any(
                marker in lowered
                for marker in (
                    "password",
                    "credential",
                    "authorization",
                    "api_key",
                    "secret",
                    "cookie",
                    "traceback",
                    "prompt",
                )
            ) or any(character in text for character in "@/\\\r\n\x00"):
                raise ValueError(f"{field_name} contains prohibited content")

    @staticmethod
    def _run_matches_review(run: Mapping[str, object], command: RecordReview) -> bool:
        if run.get("sample_id") != command.sample_id:
            return False
        if run.get("attempt_id") != command.attempt_id:
            return False
        return run.get("task") == {
            "task_id": command.task_id,
            "revision": command.task_revision,
        } and run.get("result") == {
            "result_id": command.result_id,
            "revision": command.result_revision,
        }

    @staticmethod
    def _review_export_selection(
        command: RecordReview,
        exports: Mapping[str, Mapping[str, object]],
    ) -> tuple[Mapping[str, object], ...]:
        by_id: dict[str, Mapping[str, object]] = {}
        for projection in exports.values():
            export_id = projection.get("export_snapshot_id")
            if type(export_id) is str:
                by_id[export_id] = projection
        selected: list[Mapping[str, object]] = []
        for export_id in command.captured_export_snapshot_ids:
            projection = by_id.get(export_id)
            if projection is None:
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "review"
                )
            selected.append(projection)
        return tuple(selected)

    @staticmethod
    def _validate_review_dimensions(
        command: RecordReview, selected_exports: tuple[Mapping[str, object], ...]
    ) -> None:
        if command.dimensions is None:
            raise AttemptArtifactError(ArtifactErrorCode.INVALID_COMMAND, "review")
        dimensions = command.dimensions
        xiaohongshu_selected = any(
            export.get("brief_kind") == "xiaohongshu" for export in selected_exports
        )
        for dimension in dimensions:
            if dimension.name == "xiaohongshu_consistency":
                if xiaohongshu_selected:
                    if (
                        dimension.decision not in {"PASS", "FAIL"}
                        or not dimension.critical
                    ):
                        raise AttemptArtifactError(
                            ArtifactErrorCode.IDENTITY_MISMATCH, "review"
                        )
                elif dimension.decision != "NOT_APPLICABLE" or dimension.critical:
                    raise AttemptArtifactError(
                        ArtifactErrorCode.IDENTITY_MISMATCH, "review"
                    )
                continue
            if not dimension.critical or dimension.decision not in {"PASS", "FAIL"}:
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "review"
                )
        if not selected_exports:
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "review")
        if command.overall == "APPROVED":
            if any(
                dimension.critical and dimension.decision != "PASS"
                for dimension in dimensions
            ):
                raise AttemptArtifactError(
                    ArtifactErrorCode.IDENTITY_MISMATCH, "review"
                )
        elif not any(
            dimension.critical and dimension.decision == "FAIL"
            for dimension in dimensions
        ):
            raise AttemptArtifactError(ArtifactErrorCode.IDENTITY_MISMATCH, "review")

    def _validate_attempt_root(self, root: Path) -> Path:
        if not root.is_absolute():
            raise AttemptArtifactError(ArtifactErrorCode.INVALID_ROOT, "reserve")
        if any(part in {"", ".", ".."} for part in root.parts):
            raise AttemptArtifactError(ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve")
        if _is_symlink(root):
            raise AttemptArtifactError(ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve")
        lexical = Path(os.path.normpath(os.fspath(root)))
        try:
            relative = lexical.relative_to(self._approved_parent)
        except ValueError:
            raise AttemptArtifactError(
                ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve"
            ) from None
        if not relative.parts or any(
            part in {"", ".", ".."} for part in relative.parts
        ):
            raise AttemptArtifactError(ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve")
        if relative.parts != ("p2", _SAMPLE_ID, _ATTEMPT_ID):
            raise AttemptArtifactError(ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve")
        try:
            resolved = lexical.resolve(strict=False)
        except OSError:
            raise AttemptArtifactError(
                ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve"
            ) from None
        if resolved.is_relative_to(self._repository_root):
            raise AttemptArtifactError(ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve")
        if not resolved.is_relative_to(self._approved_parent):
            raise AttemptArtifactError(ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve")
        self._reject_symlink_components(lexical)
        if lexical.exists():
            raise AttemptArtifactError(ArtifactErrorCode.ROOT_EXISTS, "reserve")
        return lexical

    def _reject_symlink_components(self, path: Path) -> None:
        try:
            relative = path.relative_to(self._approved_parent)
        except ValueError:
            raise AttemptArtifactError(
                ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve"
            ) from None
        current = self._approved_parent
        for part in relative.parts:
            current /= part
            if _is_symlink(current):
                raise AttemptArtifactError(
                    ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve"
                )

    def _load_exports(
        self, root: Path, attempt_id: str
    ) -> dict[str, Mapping[str, object]]:
        """Load immutable export metadata so a fresh service can reconstruct it."""

        for key in tuple(self._exports):
            if key[0] == attempt_id:
                del self._exports[key]
        loaded: dict[str, Mapping[str, object]] = {}
        exports_dir = root / "exports"
        if _is_symlink(exports_dir) or not exports_dir.is_dir():
            raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
        for kind, file_name in _EXPORT_FILE_NAMES.items():
            metadata_path = exports_dir / _EXPORT_METADATA_FILE_NAMES[kind]
            content_path = exports_dir / file_name
            metadata_exists = metadata_path.exists() or _is_symlink(metadata_path)
            content_exists = content_path.exists() or _is_symlink(content_path)
            if not metadata_exists:
                if content_exists:
                    raise AttemptArtifactError(
                        ArtifactErrorCode.ARTIFACT_CORRUPT, "read"
                    )
                continue
            if _is_symlink(metadata_path) or _is_symlink(content_path):
                raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
            if (
                not metadata_path.is_file()
                or stat.S_IMODE(metadata_path.stat().st_mode) != stat.S_IRUSR
            ):
                raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
            projection = _safe_read_json(metadata_path)
            if (
                projection.get("record_type") != _EXPORT_RECORD_TYPE
                or projection.get("sample_id") != _SAMPLE_ID
                or projection.get("attempt_id") != attempt_id
                or projection.get("brief_kind") != kind
                or projection.get("immutable") is not True
            ):
                raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
            reference = projection.get("content_reference")
            if not isinstance(reference, Mapping):
                raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
            reference_values = cast(Mapping[str, object], reference)
            value = reference_values.get("value")
            if (
                type(value) is not str
                or Path(value).is_absolute()
                or value != f"exports/{file_name}"
            ):
                raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
            byte_count = projection.get("byte_count")
            if (
                type(byte_count) is not int
                or byte_count < 1
                or not content_path.is_file()
            ):
                raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
            try:
                content = content_path.read_bytes()
                content.decode("utf-8")
            except (OSError, UnicodeError):
                raise AttemptArtifactError(
                    ArtifactErrorCode.ARTIFACT_CORRUPT, "read"
                ) from None
            if (
                len(content) != byte_count
                or stat.S_IMODE(content_path.stat().st_mode) != stat.S_IRUSR
            ):
                raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "read")
            loaded[kind] = projection
            self._exports[(attempt_id, kind)] = projection
        return loaded

    def _mkdir_parents(self, path: Path) -> None:
        try:
            relative = path.relative_to(self._approved_parent)
        except ValueError:
            raise AttemptArtifactError(
                ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve"
            ) from None
        current = self._approved_parent
        for part in relative.parts:
            current /= part
            if _is_symlink(current):
                raise AttemptArtifactError(
                    ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve"
                )
            if current.exists():
                if not current.is_dir():
                    raise AttemptArtifactError(
                        ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve"
                    )
                continue
            try:
                current.mkdir(mode=0o700)
            except FileExistsError:
                if _is_symlink(current) or not current.is_dir():
                    raise AttemptArtifactError(
                        ArtifactErrorCode.ROOT_NOT_ALLOWED, "reserve"
                    ) from None
            except OSError:
                raise AttemptArtifactError(
                    ArtifactErrorCode.ARTIFACT_IO_ERROR, "reserve"
                ) from None

    def _find_root(self, attempt_id: str) -> Path | None:
        # Slice 3A uses a fixed P2/P01 layout.  No broad recursive scan is
        # needed, and rejecting symlinked components keeps the lookup safe.
        candidate = self._approved_parent / "p2" / _SAMPLE_ID / attempt_id
        if not candidate.exists() or _is_symlink(candidate):
            return None
        try:
            self._reject_symlink_components(candidate)
        except AttemptArtifactError:
            return None
        if not candidate.is_dir():
            return None
        self._roots[attempt_id] = candidate
        return candidate


def _exclusive_write(path: Path, value: Mapping[str, object]) -> None:
    _exclusive_write_bytes(path, _json_bytes(value))


def _exclusive_write_bytes(path: Path, payload: bytes) -> None:
    try:
        handle = path.open("xb")
    except FileExistsError:
        raise AttemptArtifactError(ArtifactErrorCode.RECORD_EXISTS, "write") from None
    except OSError:
        raise AttemptArtifactError(
            ArtifactErrorCode.ARTIFACT_IO_ERROR, "write"
        ) from None
    try:
        with handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(path, stat.S_IRUSR)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
        if path.read_bytes() != payload:
            raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "readback")
        if stat.S_IMODE(path.stat().st_mode) != stat.S_IRUSR:
            raise AttemptArtifactError(ArtifactErrorCode.ARTIFACT_CORRUPT, "readback")
    except AttemptArtifactError:
        raise
    except OSError:
        raise AttemptArtifactError(
            ArtifactErrorCode.ARTIFACT_IO_ERROR, "write"
        ) from None
