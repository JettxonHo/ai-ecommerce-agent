"""Provider-free tests for the opt-in P2 live runner controls and seam."""

from __future__ import annotations

import importlib.util
import subprocess
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


def _repository_head(repository_root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repository_root), "rev-parse", "HEAD"], text=True
    ).strip()


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
    monkeypatch.setenv("GIT_COMMIT", _repository_head(repository_root))
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
    assert command.authorized_commit == _repository_head(repository_root)
    assert command.git_commit == _repository_head(repository_root)
    assert command.git_head == _repository_head(repository_root)
    assert command.owner_cap_micro_usd == controls.owner_cap_micro_usd


def test_future_grant_requires_database_config_before_binder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", _repository_head(repository_root))
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

    with pytest.raises(runner.P2LiveControlError) as error:
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
    monkeypatch.setenv("GIT_COMMIT", _repository_head(repository_root))
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


def test_alternate_canonical_shaped_parent_rejects_before_binder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    controls = _controls(tmp_path, repository_root)
    alternate_parent = tmp_path / "not-the-approved-ai-ecommerce-pilot-parent"
    alternate_parent.mkdir()
    alternate_shape = replace(
        controls,
        approved_artifact_parent=alternate_parent,
        artifact_root=alternate_parent
        / "p2"
        / runner.P2_SAMPLE_ID
        / runner.P2_ATTEMPT_ID,
    )
    monkeypatch.setattr(runner, "P2_PRIVATE_INPUTS_ROOT", controls.input_path.parent)
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", _repository_head(repository_root))
    monkeypatch.setenv(
        "MVP0_TASK_HTTP_DATABASE_URL", "postgresql+psycopg://test:test@127.0.0.1/p2"
    )
    captured: list[object] = []

    class _UnexpectedBinder:
        def __init__(self, **_kwargs: object) -> None:
            captured.append("constructed")

        def apply(self, _command: object) -> str:
            return "unexpected-binder-call"

    from ai_ecommerce_agent.bootstrap import pilot_p2_operator

    monkeypatch.setattr(pilot_p2_operator, "PilotP2Operator", _UnexpectedBinder)
    with pytest.raises(runner.P2LiveControlError) as error:
        runner.run_p2_operator(alternate_shape)
    assert error.value.code == "artifact_root_invalid"
    assert captured == []
    assert not alternate_shape.artifact_root.exists()


def test_missing_exact_input_handoff_rejects_before_binder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    controls = _controls(tmp_path, repository_root)
    controls.input_path.unlink()
    monkeypatch.setattr(runner, "P2_PRIVATE_INPUTS_ROOT", controls.input_path.parent)
    monkeypatch.setattr(
        runner, "P2_PRIVATE_ARTIFACT_PARENT", controls.approved_artifact_parent
    )
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", _repository_head(repository_root))
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
    monkeypatch.setattr(
        runner, "P2_PRIVATE_ARTIFACT_PARENT", controls.approved_artifact_parent
    )
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", _repository_head(repository_root))
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


def test_start_attempt_identity_has_no_silent_p01_defaults() -> None:
    """A missing caller identity must not be silently replaced with P01/A1."""

    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import StartAttempt

    command = StartAttempt()
    assert command.sample_id is None
    assert command.attempt_id is None


def test_runner_rejects_mismatched_identity_before_database_lookup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Caller identity is checked before reading the database configuration."""

    repository_root = Path(__file__).resolve().parents[3]
    controls = replace(_controls(tmp_path, repository_root), sample_id="P02")
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", _repository_head(repository_root))
    monkeypatch.delenv("MVP0_TASK_HTTP_DATABASE_URL", raising=False)
    monkeypatch.setattr(runner, "P2_PRIVATE_INPUTS_ROOT", controls.input_path.parent)
    monkeypatch.setattr(
        runner, "P2_PRIVATE_ARTIFACT_PARENT", controls.approved_artifact_parent
    )
    seen: list[str] = []
    original = runner._required_environment_value

    def record(name: str, *, error_code: str = "live_environment_incomplete") -> str:
        seen.append(name)
        return original(name, error_code=error_code)

    monkeypatch.setattr(runner, "_required_environment_value", record)
    with pytest.raises(runner.P2LiveControlError) as error:
        runner.run_p2_operator(controls)
    assert error.value.code == "identity_mismatch"
    assert "MVP0_TASK_HTTP_DATABASE_URL" not in seen


def test_runner_rejects_stale_head_before_database_lookup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A stale owner HEAD handoff fails before database configuration access."""

    repository_root = Path(__file__).resolve().parents[3]
    controls = _controls(tmp_path, repository_root)
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", "0" * 40)
    monkeypatch.delenv("MVP0_TASK_HTTP_DATABASE_URL", raising=False)
    monkeypatch.setattr(runner, "P2_PRIVATE_INPUTS_ROOT", controls.input_path.parent)
    monkeypatch.setattr(
        runner, "P2_PRIVATE_ARTIFACT_PARENT", controls.approved_artifact_parent
    )
    seen: list[str] = []
    original = runner._required_environment_value

    def record(name: str, *, error_code: str = "live_environment_incomplete") -> str:
        seen.append(name)
        return original(name, error_code=error_code)

    monkeypatch.setattr(runner, "_required_environment_value", record)
    with pytest.raises(runner.P2LiveControlError) as error:
        runner.run_p2_operator(controls)
    assert error.value.code == "git_head_mismatch"
    assert "MVP0_TASK_HTTP_DATABASE_URL" not in seen
    assert not controls.artifact_root.exists()


def test_runner_precommits_and_forwards_complete_idempotency_bundle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    controls = _controls(tmp_path, repository_root)
    monkeypatch.setattr(runner, "P2_PRIVATE_INPUTS_ROOT", controls.input_path.parent)
    monkeypatch.setattr(
        runner, "P2_PRIVATE_ARTIFACT_PARENT", controls.approved_artifact_parent
    )
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", _repository_head(repository_root))
    monkeypatch.setenv(
        "MVP0_TASK_HTTP_DATABASE_URL", "postgresql+psycopg://test:test@127.0.0.1/p2"
    )
    captured: list[Any] = []

    class _FakeProductionOperator:
        def __init__(self, **_kwargs: object) -> None:
            return None

        def apply(self, command: Any) -> str:
            captured.append(command)
            return "provider-free-synthetic"

    from ai_ecommerce_agent.bootstrap import pilot_p2_operator

    monkeypatch.setattr(pilot_p2_operator, "PilotP2Operator", _FakeProductionOperator)
    result = runner.run_p2_operator(controls)

    assert result == "provider-free-synthetic"
    assert len(captured) == 1
    bundle = captured[0].idempotency_bundle
    assert bundle.to_mapping() == {
        "sample_id": "P01",
        "attempt_id": "P2-P01-A1",
        "task_create": "operator-P2-P01-A1-task",
        "generate": "operator-P2-P01-A1-generate",
        "confirm": "operator-P2-P01-A1-confirm",
        "marketing_export": "operator-P2-P01-A1-export-marketing",
        "xiaohongshu_export": "operator-P2-P01-A1-export-xiaohongshu",
    }


def test_runner_rejects_invalid_static_controls_before_database_lookup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    controls = replace(_controls(tmp_path, repository_root), owner_cap_micro_usd=None)
    monkeypatch.setattr(runner, "P2_PRIVATE_INPUTS_ROOT", controls.input_path.parent)
    monkeypatch.setattr(
        runner, "P2_PRIVATE_ARTIFACT_PARENT", controls.approved_artifact_parent
    )
    monkeypatch.setenv(runner.P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv("GIT_COMMIT", _repository_head(repository_root))
    monkeypatch.delenv("MVP0_TASK_HTTP_DATABASE_URL", raising=False)
    seen: list[str] = []
    original = runner._required_environment_value

    def record(name: str, *, error_code: str = "live_environment_incomplete") -> str:
        seen.append(name)
        return original(name, error_code=error_code)

    monkeypatch.setattr(runner, "_required_environment_value", record)
    with pytest.raises(runner.P2LiveControlError) as error:
        runner.run_p2_operator(controls)
    assert error.value.code == "owner_cap_invalid"
    assert "MVP0_TASK_HTTP_DATABASE_URL" not in seen


def test_current_truth_surfaces_reconcile_post_correction_state() -> None:
    repository_root = Path(__file__).resolve().parents[4]
    relative_paths = (
        Path("AGENTS.md"),
        Path("README.md"),
        Path("apps/web/README.md"),
        Path("docs/goals/real-product-to-brief-pilot-goal.md"),
        Path("docs/handoffs/implementation-readiness.md"),
        Path("docs/handoffs/real-product-to-brief-pilot-p2-real-p01-precall.md"),
    )
    required_markers = (
        "REAL_P01_INPUT_FILE_READY = YES",
        "REAL_P01_PRE_CALL = BLOCKED_BY_EXECUTION_CONTROL_CORRECTION",
        "REAL_P01_GRANT = NOT_ISSUED",
        "Blocker 3 = UNKNOWN_NOT_INSPECTED",
    )
    stale_markers = (
        "WAIT_FOR_REAL_P01_INPUT_HANDOFF_AND_NEW_EXACT_MAIN_OWNER_GRANT",
        "NOT_CONSUMED_BUT_STALE_FOR_NEW_MAIN",
        "REAL_P01_INPUT_FILE_READY=NO",
    )
    for relative_path in relative_paths:
        content = (repository_root / relative_path).read_text(encoding="utf-8")
        for marker in required_markers:
            assert marker in content, f"{relative_path} missing {marker}"
        for marker in stale_markers:
            assert marker not in content, f"{relative_path} retains {marker}"
