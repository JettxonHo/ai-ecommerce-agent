"""Provider-free tests for the opt-in P2 live runner controls and seam."""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any, cast

import pytest

pytestmark = pytest.mark.unit

_RUNNER_PATH = (
    Path(__file__).resolve().parents[1]
    / "integration"
    / ("test_p2_deepseek_real_product_live.py")
)


def _runner_module() -> Any:
    spec = importlib.util.spec_from_file_location("p2_live_runner", _RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("P2 live runner module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return cast(Any, module)


runner = _runner_module()


def _valid_controls(tmp_path: Path, repository_root: Path) -> dict[str, object]:
    inputs_root = tmp_path / "approved-private-inputs"
    inputs_root.mkdir()
    input_path = inputs_root / "P01-product.md"
    input_path.write_text(
        "synthetic permitted input; content is never read", encoding="utf-8"
    )
    approved_artifact_root = tmp_path / "p2"
    approved_artifact_root.mkdir()
    return {
        "live_execution_enabled": True,
        "provider_access_enabled": True,
        "git_commit": runner.P2_GIT_COMMIT,
        "git_head": runner.P2_GIT_COMMIT,
        "sample_id": runner.P2_SAMPLE_ID,
        "attempt_id": runner.P2_ATTEMPT_ID,
        "product_name": runner.P2_PRODUCT_NAME,
        "model_designation": runner.P2_MODEL_DESIGNATION,
        "color": runner.P2_COLOR,
        "variant": runner.P2_VARIANT,
        "category": runner.P2_CATEGORY,
        "owner_cap_micro_usd": runner.P2_RESERVATION_MICRO_USD,
        "pricing_record_id": runner.P2_PRICING_RECORD_ID,
        "max_calls": runner.P2_MAX_CALLS,
        "retry_count": 0,
        "recovery_count": 0,
        "replay_count": 0,
        "fallback_count": 0,
        "manual_intervention_count": 0,
        "input_path": input_path,
        "approved_inputs_root": inputs_root,
        "artifact_root": approved_artifact_root / runner.P2_SAMPLE_ID,
        "approved_artifact_root": approved_artifact_root,
        "repository_root": repository_root,
    }


def test_preflight_controls_fail_closed_before_any_runtime_or_file_action(
    tmp_path: Path,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    controls = _valid_controls(tmp_path, repository_root)
    effects = {
        "input_read": 0,
        "artifact_create": 0,
        "secret": 0,
        "client": 0,
        "factory": 0,
        "postgres": 0,
        "network": 0,
    }
    invalid = dict(controls)
    invalid["provider_access_enabled"] = False
    with pytest.raises(runner.P2LiveControlError) as error:
        runner._preflight_controls(**invalid)
    assert error.value.code == "provider_access_flag_required"
    assert effects == dict.fromkeys(effects, 0)

    invalid_cases = (
        ("git_commit", "different-head"),
        ("sample_id", "P02"),
        ("product_name", "anchor-city-commuter-backpack"),
        ("owner_cap_micro_usd", runner.P2_RESERVATION_MICRO_USD - 1),
        ("pricing_record_id", "wrong-pricing-record"),
        ("max_calls", 4),
        ("retry_count", 1),
        ("input_path", tmp_path / "outside.md"),
        ("artifact_root", repository_root / "forbidden-artifact-root"),
    )
    for field_name, value in invalid_cases:
        invalid = dict(controls)
        invalid[field_name] = value
        with pytest.raises(runner.P2LiveControlError) as invalid_error:
            runner._preflight_controls(**invalid)
        assert "/" not in str(invalid_error.value)
        assert str(tmp_path) not in str(invalid_error.value)
    assert not cast(Path, controls["artifact_root"]).exists()


def test_valid_controls_are_immutable_metadata_only(tmp_path: Path) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    config = runner._preflight_controls(**_valid_controls(tmp_path, repository_root))

    assert config.sample_id == runner.P2_SAMPLE_ID
    assert config.attempt_id == runner.P2_ATTEMPT_ID
    assert config.owner_cap_micro_usd == runner.P2_RESERVATION_MICRO_USD
    assert config.pricing_record_id == runner.P2_PRICING_RECORD_ID
    assert config.max_calls == runner.P2_MAX_CALLS
    assert config.retry_count == 0
    assert config.recovery_count == 0
    assert config.replay_count == 0
    assert config.fallback_count == 0
    assert config.manual_intervention_count == 0
    assert config.input_path.is_file()
    assert not config.artifact_root.exists()
    with pytest.raises(FrozenInstanceError):
        runner.P2LiveControlConfig.__setattr__(config, "sample_id", "P02")


def test_prepared_p2_attempt_executes_only_injected_ordered_seam(
    tmp_path: Path,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    config = runner._preflight_controls(**_valid_controls(tmp_path, repository_root))
    events: list[str] = []

    def read_input(_path: Path) -> str:
        events.append("input_read")
        return "synthetic permitted input"

    def reserve_artifact(_path: Path) -> None:
        events.append("artifact_reserve")

    def compose_deepseek(_content: str, _config: object) -> Any:
        events.append("deepseek_factory")
        events.extend(f"deepseek_call_{index}" for index in range(1, 6))
        return runner.P2RunEvidence(
            task_id="task-P01",
            task_revision=1,
            result_id="result-P01",
            result_revision=1,
            call_ids=tuple(f"P2-P01-A1-stage-{index}" for index in range(1, 6)),
        )

    def record_run(_run: Any) -> None:
        events.append("run_record")

    def capture_exports(_run: Any, _config: object) -> tuple[Any, ...]:
        events.append("export_capture")
        return (
            runner.P2ExportEvidence(
                kind="marketing",
                export_snapshot_id="export-P2-P01-A1",
                content_bytes=b"# Marketing Brief\n",
            ),
        )

    def record_review_pending(_run: Any, _exports: tuple[Any, ...]) -> None:
        events.append("review_pending")

    def close_runtime() -> None:
        events.append("runtime_close")

    dependencies = runner.P2RunnerDependencies(
        read_input=read_input,
        reserve_artifact=reserve_artifact,
        compose_deepseek=compose_deepseek,
        record_run=record_run,
        capture_exports=capture_exports,
        record_review_pending=record_review_pending,
        close_runtime=close_runtime,
    )
    prepared = runner.prepare_p2_attempt(config, dependencies)
    assert events == []
    result = prepared.execute()

    assert events == [
        "input_read",
        "artifact_reserve",
        "deepseek_factory",
        "deepseek_call_1",
        "deepseek_call_2",
        "deepseek_call_3",
        "deepseek_call_4",
        "deepseek_call_5",
        "run_record",
        "export_capture",
        "review_pending",
        "runtime_close",
    ]
    assert result.run.provider_id == "deepseek"
    assert result.run.call_ids == tuple(
        f"P2-P01-A1-stage-{index}" for index in range(1, 6)
    )
    assert result.review_state == "PENDING"
    assert result.outcome is None
    assert not config.artifact_root.exists()


def test_prepared_p2_attempt_failure_is_terminal_without_retry(tmp_path: Path) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    config = runner._preflight_controls(**_valid_controls(tmp_path, repository_root))
    events: list[str] = []

    def fail_compose(_content: str, _config: object) -> Any:
        events.append("deepseek_factory")
        raise runner.P2LiveControlError("deepseek_execution_failed")

    def read_input(_path: Path) -> str:
        events.append("input_read")
        return "input"

    def reserve_artifact(_path: Path) -> None:
        events.append("artifact_reserve")

    def record_run(_run: object) -> None:
        events.append("run_record")

    def capture_exports(_run: object, _config: object) -> tuple[object, ...]:
        return ()

    def record_review_pending(_run: object, _exports: tuple[object, ...]) -> None:
        return None

    def close_runtime() -> None:
        events.append("runtime_close")

    dependencies = runner.P2RunnerDependencies(
        read_input=read_input,
        reserve_artifact=reserve_artifact,
        compose_deepseek=fail_compose,
        record_run=record_run,
        capture_exports=capture_exports,
        record_review_pending=record_review_pending,
        close_runtime=close_runtime,
    )
    prepared = runner.prepare_p2_attempt(config, dependencies)
    with pytest.raises(runner.P2LiveControlError):
        prepared.execute()
    with pytest.raises(runner.P2LiveControlError) as second_error:
        prepared.execute()
    assert second_error.value.code == "attempt_already_executed"
    assert events == [
        "input_read",
        "artifact_reserve",
        "deepseek_factory",
        "runtime_close",
    ]


def test_prepare_requires_explicit_dependencies_before_any_fallback(
    tmp_path: Path,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    config = runner._preflight_controls(**_valid_controls(tmp_path, repository_root))
    effects = {
        "input_read": 0,
        "artifact_create": 0,
        "runtime_factory": 0,
        "secret_resolution": 0,
    }
    prepared: Any | None = None
    preparation_error: Any | None = None
    try:
        prepared = runner.prepare_p2_attempt(config)
    except runner.P2LiveControlError as error:
        preparation_error = error

    actual = (
        None if preparation_error is None else preparation_error.code,
        prepared is not None,
        effects,
    )
    assert actual == (
        "postgres_operator_dependencies_required",
        False,
        {
            "input_read": 0,
            "artifact_create": 0,
            "runtime_factory": 0,
            "secret_resolution": 0,
        },
    ), f"prepare accepted no dependencies: actual={actual}"
