"""Opt-in P2 runner seam; real Provider execution remains gated and skipped."""

from __future__ import annotations

import os
from dataclasses import dataclass
from inspect import signature
from pathlib import Path
from typing import Any, Final, NoReturn

import pytest

pytestmark = pytest.mark.live

P2_SAMPLE_ID: Final[str] = "P01"
P2_ATTEMPT_ID: Final[str] = "P2-P01-A1"
P2_PRODUCT_NAME: Final[str] = "Anker Nano Power Bank"
P2_MODEL_DESIGNATION: Final[str] = "A1259"
P2_COLOR: Final[str] = "Black Stone"
P2_VARIANT: Final[str] = "42733233766550"
P2_CATEGORY: Final[str] = "A"
P2_MAX_CALLS: Final[int] = 5
P2_GIT_COMMIT: Final[str] = "cb77de2f96954a2d63ef00eead2f93bea1197649"
P2_PRICING_RECORD_ID: Final[str] = "deepseek-v4-pro-2026-08-30-peak-v1"
P2_RESERVATION_MICRO_USD: Final[int] = 6_783_834
P2_PRIVATE_INPUTS_ROOT: Final[Path] = Path(
    "/Users/ketchup/Private/ai-ecommerce-pilot/inputs"
)
P2_PRIVATE_ARTIFACT_PARENT: Final[Path] = Path(
    "/Users/ketchup/Private/ai-ecommerce-pilot/p2"
)
P2_PRIVATE_ARTIFACT_ROOT: Final[Path] = (
    P2_PRIVATE_ARTIFACT_PARENT / P2_SAMPLE_ID / P2_ATTEMPT_ID
)
P2_FUTURE_GRANT_ENVIRONMENT: Final[str] = "AI_ECOMMERCE_P2_REAL_GRANT"
_DATABASE_URL_ENV: Final[str] = "MVP0_TASK_HTTP_DATABASE_URL"


class P2LiveControlError(ValueError):
    """Fixed safe preflight/runner error with no path or secret leakage."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"{code}:preflight")


@dataclass(frozen=True, slots=True)
class P2LiveControlConfig:
    """Sanitized immutable controls; input content is intentionally absent."""

    sample_id: str
    attempt_id: str
    git_commit: str
    product_name: str
    model_designation: str
    color: str
    variant: str
    category: str
    owner_cap_micro_usd: int
    pricing_record_id: str
    max_calls: int
    retry_count: int
    recovery_count: int
    replay_count: int
    fallback_count: int
    manual_intervention_count: int
    input_path: Path
    artifact_root: Path
    approved_artifact_root: Path
    repository_root: Path


def _fail(code: str) -> NoReturn:
    raise P2LiveControlError(code)


def _required_environment_value(name: str) -> str:
    value = os.environ.get(name, "")
    if not value.strip():
        _fail("live_environment_incomplete")
    return value


def test_thin_live_entrypoint_requires_a_future_grant_before_binder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The opt-in entrypoint cannot invoke the production binder by default."""

    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import PilotP2OperatorError

    del PilotP2OperatorError
    monkeypatch.delenv("AI_ECOMMERCE_P2_REAL_GRANT", raising=False)
    controls = P2LiveControlConfig(
        sample_id=P2_SAMPLE_ID,
        attempt_id=P2_ATTEMPT_ID,
        git_commit=P2_GIT_COMMIT,
        product_name=P2_PRODUCT_NAME,
        model_designation=P2_MODEL_DESIGNATION,
        color=P2_COLOR,
        variant=P2_VARIANT,
        category=P2_CATEGORY,
        owner_cap_micro_usd=P2_RESERVATION_MICRO_USD,
        pricing_record_id=P2_PRICING_RECORD_ID,
        max_calls=P2_MAX_CALLS,
        retry_count=0,
        recovery_count=0,
        replay_count=0,
        fallback_count=0,
        manual_intervention_count=0,
        input_path=P2_PRIVATE_INPUTS_ROOT / "p01-public.txt",
        artifact_root=P2_PRIVATE_ARTIFACT_ROOT,
        approved_artifact_root=P2_PRIVATE_ARTIFACT_PARENT,
        repository_root=Path(__file__).resolve().parents[3],
    )

    with pytest.raises(P2LiveControlError) as error:
        run_p2_operator(controls)
    assert error.value.code == "future_owner_grant_required"


def test_legacy_injected_runner_is_retired() -> None:
    """The live entrypoint has one production binder path, not a test runner."""

    assert "prepare_p2_attempt" not in globals()
    assert "operator_factory" not in signature(run_p2_operator).parameters


def test_future_grant_entrypoint_delegates_to_production_binder_without_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A synthetic future Grant reaches only the production operator seam."""

    from ai_ecommerce_agent.bootstrap import pilot_p2_operator
    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import StartAttempt

    monkeypatch.setenv(P2_FUTURE_GRANT_ENVIRONMENT, "1")
    monkeypatch.setenv(_DATABASE_URL_ENV, "postgresql+psycopg://test:test@127.0.0.1/p2")
    controls = P2LiveControlConfig(
        sample_id=P2_SAMPLE_ID,
        attempt_id=P2_ATTEMPT_ID,
        git_commit=P2_GIT_COMMIT,
        product_name=P2_PRODUCT_NAME,
        model_designation=P2_MODEL_DESIGNATION,
        color=P2_COLOR,
        variant=P2_VARIANT,
        category=P2_CATEGORY,
        owner_cap_micro_usd=P2_RESERVATION_MICRO_USD,
        pricing_record_id=P2_PRICING_RECORD_ID,
        max_calls=P2_MAX_CALLS,
        retry_count=0,
        recovery_count=0,
        replay_count=0,
        fallback_count=0,
        manual_intervention_count=0,
        input_path=P2_PRIVATE_INPUTS_ROOT / "p01-public.txt",
        artifact_root=P2_PRIVATE_ARTIFACT_ROOT,
        approved_artifact_root=P2_PRIVATE_ARTIFACT_PARENT,
        repository_root=Path(__file__).resolve().parents[3],
    )
    captured: list[StartAttempt] = []

    class _FakeProductionOperator:
        def __init__(self, **_kwargs: object) -> None:
            return None

        def apply(self, command: StartAttempt) -> str:
            captured.append(command)
            return "provider-free-synthetic"

    monkeypatch.setattr(pilot_p2_operator, "PilotP2Operator", _FakeProductionOperator)
    result = run_p2_operator(controls)

    assert result == "provider-free-synthetic"
    assert len(captured) == 1
    assert captured[0].input_path == controls.input_path
    assert captured[0].owner_cap_micro_usd == controls.owner_cap_micro_usd


def run_p2_operator(
    controls: P2LiveControlConfig,
) -> Any:
    """Invoke the production binder only after a future explicit Grant."""

    if os.environ.get(P2_FUTURE_GRANT_ENVIRONMENT) != "1":
        _fail("future_owner_grant_required")
    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import (
        PilotP2Operator,
    )
    from ai_ecommerce_agent.bootstrap.pilot_p2_operator import (
        StartAttempt as _OperatorStartAttempt,
    )
    from ai_ecommerce_agent.entrypoints.http import FixedWorkspaceHttpConfig
    from ai_ecommerce_agent.platform.postgres import PostgresEngineConfig

    database_url = _required_environment_value(_DATABASE_URL_ENV)
    operator = PilotP2Operator(
        repository_root=controls.repository_root,
        approved_inputs_root=P2_PRIVATE_INPUTS_ROOT,
        approved_artifact_parent=controls.approved_artifact_root,
        postgres_config=PostgresEngineConfig(database_url),
        http_config=FixedWorkspaceHttpConfig("p2", "http://127.0.0.1:4174"),
    )
    return operator.apply(
        _OperatorStartAttempt(
            input_path=controls.input_path,
            artifact_root=controls.artifact_root,
            authorized_commit=controls.git_commit,
            git_commit=controls.git_commit,
            git_head=controls.git_commit,
            owner_cap_micro_usd=controls.owner_cap_micro_usd,
            pricing_record_id=controls.pricing_record_id,
            max_calls=controls.max_calls,
            retry_count=controls.retry_count,
            recovery_count=controls.recovery_count,
            replay_count=controls.replay_count,
            fallback_count=controls.fallback_count,
            manual_intervention_count=controls.manual_intervention_count,
        )
    )
