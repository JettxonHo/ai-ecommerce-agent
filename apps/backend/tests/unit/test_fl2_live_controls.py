"""Tests for explicit FL-2 live gating and sanitized evidence serialization."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_ecommerce_agent.platform.model_runtime.openai_responses._live_evidence import (
    serialize_live_smoke_evidence,
    write_live_smoke_evidence,
)

pytestmark = pytest.mark.unit


def test_live_evidence_has_only_the_operator_allowlist() -> None:
    evidence = serialize_live_smoke_evidence(
        commit="fa02d1f4e8172948ad1a909ac4ebf7fb9bdfb5a5",
        started_at_utc="2026-08-13T00:00:00Z",
        duration_ms=123,
        disposition="FAIL",
        reason="operator placeholder",
        calls=(),
        retry_count=0,
        recovery_count=0,
        behavior_gates={
            "validated_candidates": False,
            "confirmed_result": False,
            "marketing_export_immutable": False,
            "xiaohongshu_export_immutable": False,
            "downloads_utf8_no_bom_one_final_lf": False,
        },
    )
    decoded = json.loads(evidence)
    assert set(decoded) == {
        "commit",
        "started_at_utc",
        "duration_ms",
        "disposition",
        "reason",
        "calls",
        "retry_count",
        "recovery_count",
        "behavior_gates",
    }
    assert "OPENAI_API_KEY" not in evidence
    assert "payload" not in evidence
    assert "prompt" not in evidence
    assert "context" not in evidence


def test_live_evidence_file_is_append_only(tmp_path: Path) -> None:
    path = tmp_path / "fl2.json"
    write_live_smoke_evidence(path, "{}\n")
    with pytest.raises(FileExistsError):
        write_live_smoke_evidence(path, "{}\n")
