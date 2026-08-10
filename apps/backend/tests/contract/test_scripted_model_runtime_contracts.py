"""Contract tests for the deterministic scripted model runtime."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from inspect import Parameter, signature
from typing import get_type_hints

import pytest

from ai_ecommerce_agent import application as application_package
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelCallResult,
    ModelExecutionProfile,
    ModelOutputEnvelope,
    ModelRuntimeError,
    ModelRuntimePort,
    ModelRuntimeVersionTuple,
    ModelTokenUsage,
    ProviderAttemptId,
    ProviderCallMetadata,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform import model_runtime as scripted_public
from ai_ecommerce_agent.platform.model_runtime import (
    ScriptedModelRuntime,
    ScriptedModelScenario,
    ScriptedModelStep,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.contract

_EXPECTED_PUBLIC = [
    "ScriptedModelRuntime",
    "ScriptedModelScenario",
    "ScriptedModelStep",
]
_APPLICATION_PUBLIC = [
    "ModelCallContractVersions",
    "ModelCallId",
    "ModelCallIdentity",
    "ModelCallRequest",
    "ModelCallResult",
    "ModelExecutionProfile",
    "ModelOutputEnvelope",
    "ModelRecoveryKind",
    "ModelRuntimeError",
    "ModelRuntimeErrorCategory",
    "ModelRuntimePort",
    "ModelRuntimeVersionTuple",
    "ModelTokenUsage",
    "ProviderAttemptId",
    "ProviderCallMetadata",
    "StructuredOutputSpec",
]


class _TextSubclass(str):
    pass


class _IdentitySubclass(ModelCallIdentity):
    pass


class _ProfileSubclass(ModelExecutionProfile):
    pass


class _ResultSubclass(ModelCallResult):
    pass


class _StepSubclass(ScriptedModelStep):
    pass


class _TupleSubclass(tuple[ScriptedModelStep, ...]):
    pass


def _content() -> StructuredContent:
    return StructuredContent.from_mapping({"safe": "context-marker"})


def _request(
    *, call_id: str = "call-1", schema_id: str = "schema-1", schema_version: str = "v1"
) -> ModelCallRequest:
    return ModelCallRequest(
        ModelCallIdentity(ModelCallId(call_id)),
        "instruction-marker",
        _content(),
        StructuredOutputSpec(schema_id, schema_version, _content()),
        ModelExecutionProfile("profile-1", "v1"),
        ModelCallContractVersions("prompt-1", "v1", "skill-1", "domain-1", "ctx-1"),
    )


def _version_tuple(request: ModelCallRequest) -> ModelRuntimeVersionTuple:
    return ModelRuntimeVersionTuple(
        "provider-fixed",
        "api-fixed",
        "sdk-fixed",
        "model-fixed",
        "model-resolved",
        request.contract_versions.prompt_template_id,
        request.contract_versions.prompt_template_version,
        request.structured_output.output_schema_id,
        request.structured_output.output_schema_version,
        request.contract_versions.skill_contract_version,
        request.contract_versions.domain_validator_version,
        request.execution_profile.execution_profile_id,
        request.execution_profile.execution_profile_version,
        request.contract_versions.context_assembly_version,
    )


def _metadata(request: ModelCallRequest) -> ProviderCallMetadata:
    return ProviderCallMetadata(
        request.identity.model_call_id,
        (ProviderAttemptId("attempt-1"),),
        _version_tuple(request),
        "provider-response",
        "provider-request",
        ModelTokenUsage(1, 2, 99),
        4,
    )


def _result(
    request: ModelCallRequest, *, payload: str = "payload-marker"
) -> ModelCallResult:
    return ModelCallResult(ModelOutputEnvelope(payload), _metadata(request))


def _step(
    request: ModelCallRequest, outcome: ModelCallResult | ModelRuntimeError
) -> ScriptedModelStep:
    return ScriptedModelStep(
        request.identity,
        request.execution_profile,
        request.structured_output.output_schema_id,
        request.structured_output.output_schema_version,
        outcome,
    )


def test_scripted_facade_has_exact_order_and_identity() -> None:
    assert scripted_public.__all__ == _EXPECTED_PUBLIC
    assert [getattr(scripted_public, name) for name in _EXPECTED_PUBLIC] == [
        ScriptedModelRuntime,
        ScriptedModelScenario,
        ScriptedModelStep,
    ]
    public_names = {
        name
        for name in scripted_public.__dict__
        if not name.startswith("_") and name != "annotations"
    }
    assert public_names == set(_EXPECTED_PUBLIC)


def test_application_model_runtime_contract_and_facade_remain_unchanged() -> None:
    from ai_ecommerce_agent.application import model_runtime

    assert model_runtime.__all__ == _APPLICATION_PUBLIC
    assert all(not hasattr(application_package, name) for name in _APPLICATION_PUBLIC)


@pytest.mark.parametrize(
    "cls, names",
    [
        (
            ScriptedModelStep,
            [
                "expected_identity",
                "expected_execution_profile",
                "expected_output_schema_id",
                "expected_output_schema_version",
                "outcome",
            ],
        ),
        (ScriptedModelScenario, ["scenario_id", "steps"]),
    ],
)
def test_scripted_dtos_have_exact_frozen_slotted_fields(
    cls: type[object], names: list[str]
) -> None:
    assert is_dataclass(cls)
    assert [field.name for field in fields(cls)] == names
    assert "__dict__" not in cls.__slots__  # type: ignore[attr-defined]


def test_scripted_dto_annotations_are_exact() -> None:
    assert get_type_hints(ScriptedModelStep) == {
        "expected_identity": ModelCallIdentity,
        "expected_execution_profile": ModelExecutionProfile,
        "expected_output_schema_id": str,
        "expected_output_schema_version": str,
        "outcome": ModelCallResult | ModelRuntimeError,
    }
    assert get_type_hints(ScriptedModelScenario) == {
        "scenario_id": str,
        "steps": tuple[ScriptedModelStep, ...],
    }


def test_nested_identity_and_tuple_order_are_preserved() -> None:
    request = _request()
    outcome = _result(request)
    step = _step(request, outcome)
    steps = (step,)
    scenario = ScriptedModelScenario("scenario-1", steps)
    assert scenario.steps is steps
    assert scenario.steps[0] is step
    assert step.expected_identity is request.identity
    assert step.expected_execution_profile is request.execution_profile
    assert step.outcome is outcome


def test_scripted_dtos_reject_mutation_and_deletion() -> None:
    request = _request()
    step = _step(request, _result(request))
    scenario = ScriptedModelScenario("scenario-1", (step,))
    with pytest.raises(FrozenInstanceError):
        step.expected_identity = request.identity  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del step.outcome  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        scenario.steps = ()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del scenario.scenario_id  # type: ignore[misc]


def test_scenario_empty_tuple_is_valid_and_exact_tuple_boundaries_are_strict() -> None:
    assert ScriptedModelScenario("empty", ()).steps == ()
    request = _request()
    outcome = _result(request)
    step = _step(request, outcome)
    with pytest.raises(TypeError):
        ScriptedModelScenario("raw", [step])  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ScriptedModelScenario("subclass", _TupleSubclass((step,)))
    with pytest.raises(TypeError):
        ScriptedModelScenario("raw-item", (object(),))  # type: ignore[arg-type]
    subclass = _StepSubclass(
        step.expected_identity,
        step.expected_execution_profile,
        step.expected_output_schema_id,
        step.expected_output_schema_version,
        step.outcome,
    )
    with pytest.raises(TypeError):
        ScriptedModelScenario("subclass-item", (subclass,))


def test_strict_text_nested_and_outcome_boundaries_reject_raw_null_subclasses() -> None:
    request = _request()
    outcome = _result(request)
    with pytest.raises(TypeError):
        ScriptedModelStep(
            {"raw": "identity"},  # type: ignore[arg-type]
            request.execution_profile,
            "schema",
            "v1",
            outcome,
        )
    with pytest.raises(TypeError):
        ScriptedModelStep(
            _IdentitySubclass(ModelCallId("identity-subclass")),
            request.execution_profile,
            "schema",
            "v1",
            outcome,
        )
    with pytest.raises(TypeError):
        ScriptedModelStep(
            None,  # type: ignore[arg-type]
            request.execution_profile,
            "schema",
            "v1",
            outcome,
        )
    with pytest.raises(TypeError):
        ScriptedModelStep(
            request.identity,
            {"raw": "profile"},  # type: ignore[arg-type]
            "schema",
            "v1",
            outcome,
        )
    with pytest.raises(TypeError):
        ScriptedModelStep(
            request.identity,
            _ProfileSubclass("profile-subclass", "v1"),
            "schema",
            "v1",
            outcome,
        )
    with pytest.raises(TypeError):
        ScriptedModelStep(
            request.identity,
            None,  # type: ignore[arg-type]
            "schema",
            "v1",
            outcome,
        )
    with pytest.raises(TypeError):
        ScriptedModelStep(
            request.identity,
            request.execution_profile,
            _TextSubclass("schema"),
            "v1",
            outcome,
        )
    with pytest.raises(TypeError):
        ScriptedModelStep(
            request.identity,
            request.execution_profile,
            "schema",
            _TextSubclass("v1"),
            outcome,
        )
    with pytest.raises((TypeError, ValueError)):
        ScriptedModelStep(
            request.identity,
            request.execution_profile,
            "schema",
            None,  # type: ignore[arg-type]
            outcome,
        )
    with pytest.raises(TypeError):
        ScriptedModelScenario(_TextSubclass("scenario"), ())
    with pytest.raises((TypeError, ValueError)):
        ScriptedModelScenario("", ())
    with pytest.raises(TypeError):
        ScriptedModelStep(
            request.identity,
            request.execution_profile,
            "schema",
            "v1",
            {"raw": "outcome"},  # type: ignore[arg-type]
        )
    with pytest.raises(TypeError):
        ScriptedModelStep(
            request.identity,
            request.execution_profile,
            "schema",
            "v1",
            _ResultSubclass(ModelOutputEnvelope("payload"), _metadata(request)),
        )


def test_runtime_is_synchronous_port_conformant_and_signature_exact() -> None:
    runtime = ScriptedModelRuntime(scenario=ScriptedModelScenario("scenario", ()))
    method = ScriptedModelRuntime.execute
    assert list(signature(method).parameters) == ["self", "request"]
    assert get_type_hints(method) == {
        "request": ModelCallRequest,
        "return": ModelCallResult,
    }
    init_params = signature(ScriptedModelRuntime.__init__).parameters
    assert list(init_params) == ["self", "scenario"]
    assert init_params["scenario"].kind is Parameter.KEYWORD_ONLY
    assert get_type_hints(ScriptedModelRuntime.__init__) == {
        "scenario": ScriptedModelScenario,
        "return": type(None),
    }
    assert list(signature(ScriptedModelRuntime.assert_exhausted).parameters) == ["self"]
    assert isinstance(runtime, ModelRuntimePort)
