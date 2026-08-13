"""Tests for explicit FL-2 live gating and sanitized evidence serialization."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import ai_ecommerce_agent.platform.model_runtime as _runtime_package

_runtime_package.__dict__.pop("openai_responses", None)

pytestmark = pytest.mark.unit


def test_deepseek_smoke_never_reads_provider_secret_directly() -> None:
    source = (
        Path(__file__).parents[1] / "integration" / "test_fl2_deepseek_live_smoke.py"
    ).read_text(encoding="utf-8")
    assert "DEEPSEEK_API_KEY" not in source
    assert "RUN_DEEPSEEK_LIVE_SMOKE" in source
    assert "FL2_DEEPSEEK_LIVE_EVIDENCE_PATH" in source


def test_deepseek_existing_evidence_path_fails_during_collection_preflight(
    tmp_path: Path,
) -> None:
    repository_root = Path(__file__).resolve().parents[4]
    smoke_module = (
        Path(__file__).resolve().parents[1]
        / "integration"
        / "test_fl2_deepseek_live_smoke.py"
    )
    evidence_path = tmp_path / "already-created.json"
    evidence_path.write_text("existing\n", encoding="utf-8")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": os.pathsep.join(
            filter(
                None,
                (
                    str(repository_root / "apps/backend/tests"),
                    os.environ.get("PYTHONPATH", ""),
                ),
            )
        ),
        "RUN_DEEPSEEK_LIVE_SMOKE": "1",
        "MVP0_RUN_TASK_HTTP_POSTGRES": "1",
        "GIT_COMMIT": commit,
        "FL2_DEEPSEEK_LIVE_EVIDENCE_PATH": str(evidence_path),
    }
    script = f"""
import runpy

try:
    runpy.run_path({str(smoke_module)!r}, run_name="deepseek_smoke_preflight")
except BaseException as exc:
    if type(exc).__name__ == "Failed" and str(exc) == (
        "the live evidence path must not already exist"
    ):
        raise SystemExit(0)
    raise
raise SystemExit(1)
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=repository_root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert str(evidence_path) not in result.stdout
    assert str(evidence_path) not in result.stderr


def test_live_evidence_has_only_the_operator_allowlist() -> None:
    from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
        _live_evidence as evidence_module,
    )

    evidence = evidence_module.serialize_live_smoke_evidence(
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
    from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
        _live_evidence as evidence_module,
    )

    path = tmp_path / "fl2.json"
    evidence_module.write_live_smoke_evidence(path, "{}\n")
    with pytest.raises(FileExistsError):
        evidence_module.write_live_smoke_evidence(path, "{}\n")
