"""Allowlisted, provider-neutral evidence for the one FL-2 live smoke."""

from __future__ import annotations

import json as _json
from collections.abc import Mapping, Sequence
from pathlib import Path

from ai_ecommerce_agent.application.model_runtime import (
    ProviderCallMetadata as _ProviderCallMetadata,
)

_DISPOSITIONS = frozenset({"PASS", "FAIL"})
_BEHAVIOR_GATES = frozenset(
    {
        "validated_candidates",
        "confirmed_result",
        "marketing_export_immutable",
        "xiaohongshu_export_immutable",
        "downloads_utf8_no_bom_one_final_lf",
    }
)
_VERSION_FIELDS = (
    "provider_id",
    "api_family",
    "sdk_version",
    "configured_model_id",
    "resolved_model_id",
    "prompt_template_id",
    "prompt_template_version",
    "output_schema_id",
    "output_schema_version",
    "skill_contract_version",
    "domain_validator_version",
    "execution_profile_id",
    "execution_profile_version",
    "context_assembly_version",
)


def _nonempty_text(value: object, name: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _metadata(value: _ProviderCallMetadata) -> dict[str, object]:
    version = value.version_tuple
    usage = value.usage
    return {
        "model_call_id": value.model_call_id.value,
        "provider_attempt_ids": [item.value for item in value.provider_attempt_ids],
        "provider_response_id": value.provider_response_id,
        "provider_request_id": value.provider_request_id,
        "version_tuple": {field: getattr(version, field) for field in _VERSION_FIELDS},
        "usage": (
            None
            if usage is None
            else {
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "total_tokens": usage.total_tokens,
            }
        ),
        "latency_ms": value.latency_ms,
    }


def serialize_live_smoke_evidence(
    *,
    commit: str,
    started_at_utc: str,
    duration_ms: int,
    disposition: str,
    reason: str,
    calls: Sequence[_ProviderCallMetadata],
    retry_count: int,
    recovery_count: int,
    behavior_gates: Mapping[str, bool],
) -> str:
    """Serialize only the fixed FL-2 operator evidence allowlist.

    The function accepts already provider-neutral metadata and has no input
    for prompts, context, source text, candidate payloads or SDK responses.
    """

    commit = _nonempty_text(commit, "commit")
    started_at_utc = _nonempty_text(started_at_utc, "started_at_utc")
    reason = _nonempty_text(reason, "reason")
    if type(duration_ms) is not int or duration_ms < 0:
        raise ValueError("duration_ms must be a non-negative int")
    if disposition not in _DISPOSITIONS:
        raise ValueError("disposition must be PASS or FAIL")
    if type(retry_count) is not int or retry_count < 0:
        raise ValueError("retry_count must be a non-negative int")
    if type(recovery_count) is not int or recovery_count < 0:
        raise ValueError("recovery_count must be a non-negative int")
    if type(calls) not in (tuple, list):
        raise TypeError("calls must be a sequence")
    call_records: list[dict[str, object]] = []
    for call in calls:
        if type(call) is not _ProviderCallMetadata:
            raise TypeError("calls must contain ProviderCallMetadata")
        call_records.append(_metadata(call))
    gates = dict(behavior_gates)
    if frozenset(gates) != _BEHAVIOR_GATES:
        raise ValueError("behavior_gates must match the fixed FL-2 gate set")
    if any(type(value) is not bool for value in gates.values()):
        raise TypeError("behavior_gates values must be bool")
    evidence = {
        "commit": commit,
        "started_at_utc": started_at_utc,
        "duration_ms": duration_ms,
        "disposition": disposition,
        "reason": reason,
        "calls": call_records,
        "retry_count": retry_count,
        "recovery_count": recovery_count,
        "behavior_gates": {key: gates[key] for key in sorted(gates)},
    }
    return _json.dumps(evidence, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def write_live_smoke_evidence(path: Path, serialized: str) -> None:
    """Create one new evidence file and refuse to overwrite an earlier run."""

    if type(serialized) is not str or not serialized:
        raise ValueError("serialized evidence must be non-empty text")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(serialized)


__all__ = ["serialize_live_smoke_evidence", "write_live_smoke_evidence"]
