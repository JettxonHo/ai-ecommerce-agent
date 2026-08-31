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
        "git_commit": runner.P2_GIT_COMMIT,
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
        "artifact_root": approved_artifact_root
        / runner.P2_SAMPLE_ID
        / runner.P2_ATTEMPT_ID,
        "approved_artifact_root": approved_artifact_root,
        "repository_root": repository_root,
    }


def _controls(tmp_path: Path, repository_root: Path) -> Any:
    return runner.P2LiveControlConfig(**_valid_controls(tmp_path, repository_root))


def test_future_grant_absence_rejects_before_binder(
    tmp_path: Path,
) -> None:
    """The default path is fail-closed before constructing the binder."""

    repository_root = Path(__file__).resolve().parents[3]
    controls = _controls(tmp_path, repository_root)

    with pytest.raises(runner.P2LiveControlError) as error:
        runner.run_p2_operator(controls)
    assert error.value.code == "future_owner_grant_required"


def test_live_controls_are_immutable_metadata_only(tmp_path: Path) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    config = _controls(tmp_path, repository_root)

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


def test_future_grant_delegates_to_production_binder_without_secret(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A synthetic future Grant calls the production binder seam only."""

    repository_root = Path(__file__).resolve().parents[3]
    controls = _controls(tmp_path, repository_root)
    captured: list[Any] = []

    class _FakeProductionOperator:
        def __init__(self, **kwargs: object) -> None:
            captured.append(("init", kwargs))

        def apply(self, command: Any) -> str:
            captured.append(("apply", command))
            return "provider-free-synthetic"

    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv(
        "MVP0_TASK_HTTP_DATABASE_URL", "postgresql+psycopg://test:test@127.0.0.1/p2"
    )
    from ai_ecommerce_agent.bootstrap import pilot_p2_operator

    monkeypatch.setattr(pilot_p2_operator, "PilotP2Operator", _FakeProductionOperator)

    result = runner.run_p2_operator(controls)
    assert result == "provider-free-synthetic"
    assert [event for event, _value in captured] == ["init", "apply"]
    command = captured[1][1]
    assert command.input_path == controls.input_path
    assert command.authorized_commit == controls.git_commit
    assert command.owner_cap_micro_usd == controls.owner_cap_micro_usd


def test_future_grant_requires_database_config_before_binder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.delenv("MVP0_TASK_HTTP_DATABASE_URL", raising=False)

    with pytest.raises(runner.P2LiveControlError) as error:
        runner.run_p2_operator(_controls(tmp_path, repository_root))
    assert error.value.code == "live_environment_incomplete"
