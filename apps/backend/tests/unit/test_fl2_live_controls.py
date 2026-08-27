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
    assert "FL2_DEEPSEEK_LIVE_EXPORT_DIR" in source


def _smoke_module_path(repository_root: Path) -> Path:
    return (
        repository_root
        / "apps/backend/tests/integration/test_fl2_deepseek_live_smoke.py"
    )


def _run_smoke_module(
    repository_root: Path,
    *,
    evidence_path: Path,
    export_dir: Path,
    script: str,
) -> subprocess.CompletedProcess[str]:
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
                    str(repository_root / "apps/backend/src"),
                    os.environ.get("PYTHONPATH", ""),
                ),
            )
        ),
        "RUN_DEEPSEEK_LIVE_SMOKE": "1",
        "MVP0_RUN_TASK_HTTP_POSTGRES": "1",
        "GIT_COMMIT": commit,
        "FL2_DEEPSEEK_LIVE_EVIDENCE_PATH": str(evidence_path),
        "FL2_DEEPSEEK_LIVE_EXPORT_DIR": str(export_dir),
    }
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=repository_root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_successful_smoke_preserves_exact_user_downloads(tmp_path: Path) -> None:
    repository_root = Path(__file__).resolve().parents[4]
    evidence_path = tmp_path / "evidence.json"
    export_dir = tmp_path / "exports"
    script = f"""
import runpy

module = runpy.run_path(
    {str(_smoke_module_path(repository_root))!r},
    run_name="deepseek_smoke_exports",
)
module["_preserve_downloads"]({{
    "marketing": b"# Marketing Brief\\n",
    "xiaohongshu": b"# Xiaohongshu Brief\\n",
}})
"""
    result = _run_smoke_module(
        repository_root,
        evidence_path=evidence_path,
        export_dir=export_dir,
        script=script,
    )
    assert result.returncode == 0, result.stderr
    assert sorted(path.name for path in export_dir.iterdir()) == [
        "marketing-brief.md",
        "xiaohongshu-brief.md",
    ]
    assert (export_dir / "marketing-brief.md").read_bytes() == (b"# Marketing Brief\n")
    assert (export_dir / "xiaohongshu-brief.md").read_bytes() == (
        b"# Xiaohongshu Brief\n"
    )


def test_existing_export_target_fails_before_private_runtime_or_resource_seams(
    tmp_path: Path,
) -> None:
    repository_root = Path(__file__).resolve().parents[4]
    evidence_path = tmp_path / "evidence.json"
    export_dir = tmp_path / "existing-exports"
    export_dir.mkdir()
    (export_dir / "sentinel.txt").write_text("preserved\n", encoding="utf-8")
    script = f"""
import runpy

calls = []
import ai_ecommerce_agent.platform.model_runtime.deepseek._runtime as runtime_module
import ai_ecommerce_agent.platform.postgres as postgres_module

runtime_module.create_deepseek_runtime = (
    lambda *args, **kwargs: calls.append("runtime")
)
postgres_module.create_postgres_engine = (
    lambda *args, **kwargs: calls.append("postgres")
)

try:
    runpy.run_path(
        {str(_smoke_module_path(repository_root))!r},
        run_name="deepseek_smoke_existing_export",
    )
except BaseException as exc:
    if type(exc).__name__ == "Failed" and str(exc) == (
        "the live export directory must not already exist"
    ):
        print(f"seams={{calls!r}}")
        raise SystemExit(0)
    raise
raise SystemExit(1)
"""
    result = _run_smoke_module(
        repository_root,
        evidence_path=evidence_path,
        export_dir=export_dir,
        script=script,
    )
    assert result.returncode == 0, result.stderr
    assert "seams=[]" in result.stdout
    assert str(export_dir) not in result.stdout
    assert str(export_dir) not in result.stderr
    assert (export_dir / "sentinel.txt").read_text(encoding="utf-8") == ("preserved\n")


def test_export_preservation_has_only_two_user_facing_files(tmp_path: Path) -> None:
    repository_root = Path(__file__).resolve().parents[4]
    evidence_path = tmp_path / "evidence.json"
    export_dir = tmp_path / "exports"
    script = f"""
import runpy

module = runpy.run_path(
    {str(_smoke_module_path(repository_root))!r},
    run_name="deepseek_smoke_file_allowlist",
)
module["_preserve_downloads"]({{
    "marketing": b"# Marketing Brief\\n",
    "xiaohongshu": b"# Xiaohongshu Brief\\n",
}})
assert sorted(path.name for path in module["_EXPORT_DIR"].iterdir()) == [
    "marketing-brief.md",
    "xiaohongshu-brief.md",
]
"""
    result = _run_smoke_module(
        repository_root,
        evidence_path=evidence_path,
        export_dir=export_dir,
        script=script,
    )
    assert result.returncode == 0, result.stderr
    assert not any(
        path.name
        in {
            "provider-response.json",
            "reasoning.txt",
            "prompt.txt",
            "context.json",
            "candidate.json",
            "traceback.txt",
            "account.json",
            "database-row.json",
        }
        for path in export_dir.iterdir()
    )


def test_later_smoke_failure_removes_preserved_exports(tmp_path: Path) -> None:
    repository_root = Path(__file__).resolve().parents[4]
    evidence_path = tmp_path / "evidence.json"
    export_dir = tmp_path / "exports"
    script = f"""
import runpy
from types import SimpleNamespace

module = runpy.run_path(
    {str(_smoke_module_path(repository_root))!r},
    run_name="deepseek_smoke_late_failure",
)
smoke = module["test_one_deepseek_task_to_export_smoke"]
globals = smoke.__globals__

class Response:
    def __init__(self, status_code, payload=None, content=b""):
        self.status_code = status_code
        self._payload = payload
        self.content = content
        self.text = ""

    def json(self):
        return self._payload

class Client:
    def __init__(self):
        self.snapshot_count = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def post(self, path, **kwargs):
        if path == "/api/v1/tasks":
            return Response(201, {{"taskId": "task-1"}})
        if path.endswith("/commands/generate-result"):
            return Response(201, {{"status": "awaiting_review"}})
        if path.endswith("/commands/confirm-current-result"):
            return Response(201, {{"status": "confirmed"}})
        if path.endswith("/export-previews"):
            return Response(200, {{"basis": kwargs["json"]}})
        if path == "/api/v1/export-snapshots":
            self.snapshot_count += 1
            return Response(
                201,
                {{
                    "snapshotId": f"snapshot-{{self.snapshot_count}}",
                    "contentLocation": f"/download-{{self.snapshot_count}}",
                }},
            )
        raise AssertionError(path)

    def put(self, path, **kwargs):
        return Response(200, {{}})

    def get(self, path, **kwargs):
        if path.endswith("/current-result"):
            return Response(
                200,
                {{
                    "status": "awaiting_review",
                    "productIntake": {{}},
                    "customerInsight": {{}},
                    "productPositioning": {{}},
                    "marketingBrief": {{}},
                    "xiaohongshuBrief": {{}},
                }},
            )
        return Response(200, content=b"# Export\\n")

profiles = (
    "product_intake_v1",
    "customer_insight_v1",
    "product_positioning_v1",
    "marketing_brief_v1",
    "xiaohongshu_mapping_v1",
)
metadata = tuple(
    SimpleNamespace(
        version_tuple=SimpleNamespace(
            provider_id="deepseek",
            execution_profile_id=profile,
            execution_profile_version=(
                "v2" if profile.endswith("mapping_v1") else "v1"
            ),
        )
    )
    for profile in profiles
)

def result_client(_engine, runtimes):
    runtimes.append(
        SimpleNamespace(metadata_records=metadata, retry_count=0, close=lambda: None)
    )
    return Client(), SimpleNamespace(close=lambda: None)

globals["_result_client"] = result_client
evidence_writes = []

def write_evidence(**kwargs):
    evidence_writes.append(kwargs["disposition"])
    if kwargs["disposition"] == "PASS":
        raise FileExistsError("evidence race")

globals["_write_evidence"] = write_evidence
try:
    smoke(None)
except FileExistsError as error:
    if str(error) != "evidence race":
        raise
else:
    raise AssertionError("late evidence failure must fail the smoke")
assert evidence_writes == ["PASS", "FAIL"]
assert not module["_EXPORT_DIR"].exists()
"""
    result = _run_smoke_module(
        repository_root,
        evidence_path=evidence_path,
        export_dir=export_dir,
        script=script,
    )
    assert result.returncode == 0, result.stderr


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
    export_dir = tmp_path / "unused-exports"
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
        "FL2_DEEPSEEK_LIVE_EXPORT_DIR": str(export_dir),
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
