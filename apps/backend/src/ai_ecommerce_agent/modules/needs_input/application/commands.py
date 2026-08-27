"""Typed, bounded Needs Input resolution command."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from ai_ecommerce_agent.shared_kernel import Revision

_RESOLUTION_TYPES = frozenset(
    {
        "provide_source_reference",
        "choose_existing_value",
        "submit_correction",
        "confirm_known_limitation",
        "cancel_path",
    }
)


def _canonical_payload(payload: Mapping[str, object]) -> Mapping[str, object]:
    try:
        serialized = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise ValueError("resolution payload must be canonical JSON") from error
    if len(serialized.encode("utf-8")) > 32768:
        raise OverflowError("resolution payload is too large")
    decoded = json.loads(serialized)
    if not isinstance(decoded, dict):
        raise ValueError("resolution payload must be a JSON object")
    return cast(dict[str, object], decoded)


@dataclass(frozen=True, slots=True)
class ResolveNeedsInput:
    """Resolve one current request with a server-validated typed payload."""

    action_request_id: str
    expected_revision: Revision
    idempotency_key: str
    resolution_type: str
    resolution_payload: Mapping[str, object]

    def __post_init__(self) -> None:
        if not self.action_request_id.strip():
            raise ValueError("action_request_id must be non-empty")
        if type(self.expected_revision) is not Revision:
            raise TypeError("expected_revision must be a Revision")
        if not self.idempotency_key.strip():
            raise ValueError("idempotency_key must be non-empty")
        if len(self.idempotency_key.encode("utf-8")) > 200:
            raise OverflowError("idempotency_key is too large")
        if self.resolution_type not in _RESOLUTION_TYPES:
            raise ValueError("resolution_type is unsupported")
        object.__setattr__(
            self, "resolution_payload", _canonical_payload(self.resolution_payload)
        )


__all__ = ["ResolveNeedsInput"]
