"""Deterministic, in-memory implementation of the Model Runtime port."""

from __future__ import annotations

from dataclasses import dataclass as _dataclass

import ai_ecommerce_agent.application.model_runtime as _contracts


def _text(value: object, name: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _exact(value: object, expected: type[object], name: str) -> None:
    if type(value) is not expected:
        raise TypeError(f"{name} must be a {expected.__name__}")


def _safe_failure(scenario_id: str, ordinal: int, field: str) -> AssertionError:
    return AssertionError(
        f"scripted scenario {scenario_id!r} ordinal {ordinal} mismatch {field}"
    )


@_dataclass(frozen=True, slots=True)
class ScriptedModelStep:
    expected_identity: _contracts.ModelCallIdentity
    expected_execution_profile: _contracts.ModelExecutionProfile
    expected_output_schema_id: str
    expected_output_schema_version: str
    outcome: _contracts.ModelCallResult | _contracts.ModelRuntimeError

    def __post_init__(self) -> None:
        _exact(
            self.expected_identity, _contracts.ModelCallIdentity, "expected_identity"
        )
        _exact(
            self.expected_execution_profile,
            _contracts.ModelExecutionProfile,
            "expected_execution_profile",
        )
        _text(self.expected_output_schema_id, "expected_output_schema_id")
        _text(self.expected_output_schema_version, "expected_output_schema_version")
        if type(self.outcome) not in (
            _contracts.ModelCallResult,
            _contracts.ModelRuntimeError,
        ):
            raise TypeError("outcome must be a ModelCallResult or ModelRuntimeError")


@_dataclass(frozen=True, slots=True)
class ScriptedModelScenario:
    scenario_id: str
    steps: tuple[ScriptedModelStep, ...]

    def __post_init__(self) -> None:
        _text(self.scenario_id, "scenario_id")
        _exact(self.steps, tuple, "steps")
        for step in self.steps:
            _exact(step, ScriptedModelStep, "steps item")


class ScriptedModelRuntime:
    def __init__(self, *, scenario: ScriptedModelScenario) -> None:
        _exact(scenario, ScriptedModelScenario, "scenario")
        self._scenario = scenario
        self._ordinal = 1

    def _fail(self, field: str) -> AssertionError:
        return _safe_failure(self._scenario.scenario_id, self._ordinal, field)

    def _current_step(self) -> ScriptedModelStep:
        index = self._ordinal - 1
        if index >= len(self._scenario.steps):
            raise self._fail("script_exhausted")
        return self._scenario.steps[index]

    def _assert_request_matches(
        self, request: _contracts.ModelCallRequest, step: ScriptedModelStep
    ) -> None:
        if request.identity != step.expected_identity:
            raise self._fail("identity")
        if request.execution_profile != step.expected_execution_profile:
            raise self._fail("execution_profile")
        if request.structured_output.output_schema_id != step.expected_output_schema_id:
            raise self._fail("output_schema_id")
        if (
            request.structured_output.output_schema_version
            != step.expected_output_schema_version
        ):
            raise self._fail("output_schema_version")

    def _assert_version_parity(
        self,
        request: _contracts.ModelCallRequest,
        version_tuple: _contracts.ModelRuntimeVersionTuple,
    ) -> None:
        expected = (
            ("prompt_template_id", request.contract_versions.prompt_template_id),
            (
                "prompt_template_version",
                request.contract_versions.prompt_template_version,
            ),
            ("output_schema_id", request.structured_output.output_schema_id),
            (
                "output_schema_version",
                request.structured_output.output_schema_version,
            ),
            (
                "skill_contract_version",
                request.contract_versions.skill_contract_version,
            ),
            (
                "domain_validator_version",
                request.contract_versions.domain_validator_version,
            ),
            ("execution_profile_id", request.execution_profile.execution_profile_id),
            (
                "execution_profile_version",
                request.execution_profile.execution_profile_version,
            ),
            (
                "context_assembly_version",
                request.contract_versions.context_assembly_version,
            ),
        )
        for field, expected_value in expected:
            if getattr(version_tuple, field) != expected_value:
                raise self._fail(f"version_tuple.{field}")

    def _assert_outcome_matches(
        self,
        request: _contracts.ModelCallRequest,
        outcome: _contracts.ModelCallResult | _contracts.ModelRuntimeError,
    ) -> None:
        if isinstance(outcome, _contracts.ModelCallResult):
            model_call_id = outcome.provider_metadata.model_call_id
            metadata = outcome.provider_metadata
        else:
            model_call_id = outcome.model_call_id
            metadata = outcome.provider_metadata
        if model_call_id != request.identity.model_call_id:
            raise self._fail("outcome.model_call_id")
        if metadata is not None:
            self._assert_version_parity(request, metadata.version_tuple)

    def execute(
        self, request: _contracts.ModelCallRequest
    ) -> _contracts.ModelCallResult:
        _exact(request, _contracts.ModelCallRequest, "request")
        step = self._current_step()
        self._assert_request_matches(request, step)
        self._assert_outcome_matches(request, step.outcome)
        self._ordinal += 1
        if isinstance(step.outcome, _contracts.ModelRuntimeError):
            raise step.outcome
        return step.outcome

    def assert_exhausted(self) -> None:
        if self._ordinal <= len(self._scenario.steps):
            raise self._fail("not_exhausted")


__all__ = ["ScriptedModelRuntime", "ScriptedModelScenario", "ScriptedModelStep"]
