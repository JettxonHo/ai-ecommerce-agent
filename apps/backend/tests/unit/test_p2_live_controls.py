"""Provider-free tests for the opt-in P2 live runner controls and seam."""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import FrozenInstanceError, replace
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
    input_path = inputs_root / "p01-public.txt"
    input_path.write_text(
        "synthetic permitted input; content is never read", encoding="utf-8"
    )
    approved_artifact_parent = tmp_path / "approved-artifact-parent"
    approved_artifact_parent.mkdir()
    return {
        "git_commit": "control-field-is-not-the-owner-handoff",
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
        "artifact_root": approved_artifact_parent
        / "p2"
        / runner.P2_SAMPLE_ID
        / runner.P2_ATTEMPT_ID,
        "approved_artifact_parent": approved_artifact_parent,
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
    monkeypatch.setattr(runner, "P2_PRIVATE_INPUTS_ROOT", controls.input_path.parent)
    monkeypatch.setattr(
        runner, "P2_PRIVATE_ARTIFACT_PARENT", controls.approved_artifact_parent
    )
    captured: list[Any] = []

    class _FakeProductionOperator:
        def __init__(self, **kwargs: object) -> None:
            captured.append(("init", kwargs))

        def apply(self, command: Any) -> str:
            captured.append(("apply", command))
            return "provider-free-synthetic"

    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", "owner-selected-commit")
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
    assert command.authorized_commit == "owner-selected-commit"
    assert command.git_commit == "owner-selected-commit"
    assert command.git_head == "owner-selected-commit"
    assert command.owner_cap_micro_usd == controls.owner_cap_micro_usd


def test_future_grant_requires_database_config_before_binder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", "owner-selected-commit")
    monkeypatch.delenv("MVP0_TASK_HTTP_DATABASE_URL", raising=False)
    controls = _controls(tmp_path, repository_root)
    monkeypatch.setattr(runner, "P2_PRIVATE_INPUTS_ROOT", controls.input_path.parent)
    monkeypatch.setattr(
        runner, "P2_PRIVATE_ARTIFACT_PARENT", controls.approved_artifact_parent
    )

    with pytest.raises(runner.P2LiveControlError) as error:
        runner.run_p2_operator(controls)
    assert error.value.code == "live_environment_incomplete"


@pytest.mark.parametrize("handoff", [None, "", "   "])
def test_git_commit_handoff_is_required_before_binder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    handoff: str | None,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv(
        "MVP0_TASK_HTTP_DATABASE_URL", "postgresql+psycopg://test:test@127.0.0.1/p2"
    )
    if handoff is None:
        monkeypatch.delenv("GIT_COMMIT", raising=False)
    else:
        monkeypatch.setenv("GIT_COMMIT", handoff)
    captured: list[object] = []

    class _BinderMustNotBeConstructed:
        def __init__(self, **_kwargs: object) -> None:
            captured.append("constructed")

    from ai_ecommerce_agent.bootstrap import pilot_p2_operator

    monkeypatch.setattr(
        pilot_p2_operator, "PilotP2Operator", _BinderMustNotBeConstructed
    )
    with pytest.raises(runner.P2LiveControlError) as error:
        runner.run_p2_operator(_controls(tmp_path, repository_root))
    assert error.value.code == "git_commit_required"
    assert captured == []


def test_stale_git_commit_rejected_by_core_before_artifact_side_effect(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    controls = _controls(tmp_path, repository_root)
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv(
        "MVP0_TASK_HTTP_DATABASE_URL", "postgresql+psycopg://test:test@127.0.0.1/p2"
    )
    monkeypatch.setenv("GIT_COMMIT", "0" * 40)
    monkeypatch.setattr(runner, "P2_PRIVATE_INPUTS_ROOT", controls.input_path.parent)
    monkeypatch.setattr(
        runner, "P2_PRIVATE_ARTIFACT_PARENT", controls.approved_artifact_parent
    )

    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import PilotP2OperatorError

    with pytest.raises(PilotP2OperatorError) as error:
        runner.run_p2_operator(controls)
    assert error.value.code == "git_head_mismatch"
    assert not controls.artifact_root.exists()


def test_old_double_p2_artifact_geometry_rejects_before_binder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    controls = _controls(tmp_path, repository_root)
    old_parent = tmp_path / "p2"
    old_parent.mkdir()
    old_shape = replace(
        controls,
        approved_artifact_parent=old_parent,
        artifact_root=old_parent / runner.P2_SAMPLE_ID / runner.P2_ATTEMPT_ID,
    )
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", "owner-selected-commit")
    monkeypatch.setenv(
        "MVP0_TASK_HTTP_DATABASE_URL", "postgresql+psycopg://test:test@127.0.0.1/p2"
    )
    captured: list[object] = []

    class _BinderMustNotBeConstructed:
        def __init__(self, **_kwargs: object) -> None:
            captured.append("constructed")

    from ai_ecommerce_agent.bootstrap import pilot_p2_operator

    monkeypatch.setattr(
        pilot_p2_operator, "PilotP2Operator", _BinderMustNotBeConstructed
    )
    with pytest.raises(runner.P2LiveControlError) as error:
        runner.run_p2_operator(old_shape)
    assert error.value.code == "artifact_root_invalid"
    assert captured == []
    assert not old_shape.artifact_root.exists()


def test_missing_exact_input_handoff_rejects_before_binder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    controls = _controls(tmp_path, repository_root)
    controls.input_path.unlink()
    monkeypatch.setattr(runner, "P2_PRIVATE_INPUTS_ROOT", controls.input_path.parent)
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", "owner-selected-commit")
    monkeypatch.setenv(
        "MVP0_TASK_HTTP_DATABASE_URL", "postgresql+psycopg://test:test@127.0.0.1/p2"
    )
    captured: list[object] = []

    class _BinderMustNotBeConstructed:
        def __init__(self, **_kwargs: object) -> None:
            captured.append("constructed")

    from ai_ecommerce_agent.bootstrap import pilot_p2_operator

    monkeypatch.setattr(
        pilot_p2_operator, "PilotP2Operator", _BinderMustNotBeConstructed
    )
    with pytest.raises(runner.P2LiveControlError) as error:
        runner.run_p2_operator(controls)
    assert error.value.code == "input_handoff_required"
    assert captured == []
    assert not controls.artifact_root.exists()


def test_noncanonical_input_handoff_rejects_without_search_or_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    controls = _controls(tmp_path, repository_root)
    alternate = controls.input_path.parent / "P01-product.md"
    alternate.write_text("synthetic alternate fixture", encoding="utf-8")
    noncanonical = replace(controls, input_path=alternate)
    monkeypatch.setattr(runner, "P2_PRIVATE_INPUTS_ROOT", controls.input_path.parent)
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", "owner-selected-commit")
    monkeypatch.setenv(
        "MVP0_TASK_HTTP_DATABASE_URL", "postgresql+psycopg://test:test@127.0.0.1/p2"
    )
    captured: list[object] = []

    class _BinderMustNotBeConstructed:
        def __init__(self, **_kwargs: object) -> None:
            captured.append("constructed")

    from ai_ecommerce_agent.bootstrap import pilot_p2_operator

    monkeypatch.setattr(
        pilot_p2_operator, "PilotP2Operator", _BinderMustNotBeConstructed
    )
    with pytest.raises(runner.P2LiveControlError) as error:
        runner.run_p2_operator(noncanonical)
    assert error.value.code == "input_handoff_required"
    assert captured == []
    assert not noncanonical.artifact_root.exists()
