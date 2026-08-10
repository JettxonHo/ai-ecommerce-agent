"""Unit behavior tests for the deterministic scripted model runtime."""

from __future__ import annotations

from dataclasses import replace

import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelCallResult,
    ModelExecutionProfile,
    ModelOutputEnvelope,
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
    ModelRuntimeVersionTuple,
    ModelTokenUsage,
    ProviderAttemptId,
    ProviderCallMetadata,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform.model_runtime import (
    ScriptedModelRuntime,
    ScriptedModelScenario,
    ScriptedModelStep,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.unit


class _RequestSubclass(ModelCallRequest):
    pass


def _request(
    *,
    call_id: str = "call-1",
    profile_id: str = "profile-1",
    profile_version: str = "v1",
    schema_id: str = "schema-1",
    schema_version: str = "v1",
    context_marker: str = "context-marker",
) -> ModelCallRequest:
    return ModelCallRequest(
        ModelCallIdentity(ModelCallId(call_id)),
        "instruction-marker",
        StructuredContent.from_mapping({"safe": context_marker}),
        StructuredOutputSpec(
            schema_id,
            schema_version,
            StructuredContent.from_mapping({"schema": "schema-marker"}),
        ),
        ModelExecutionProfile(profile_id, profile_version),
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


def _metadata(
    request: ModelCallRequest, *, version_tuple: ModelRuntimeVersionTuple | None = None
) -> ProviderCallMetadata:
    return ProviderCallMetadata(
        request.identity.model_call_id,
        (ProviderAttemptId("attempt-1"),),
        version_tuple or _version_tuple(request),
        "response-marker",
        "request-marker",
        ModelTokenUsage(1, 2, 99),
        4,
    )


def _result(
    request: ModelCallRequest,
    *,
    payload: str = "payload-marker",
    metadata: ProviderCallMetadata | None = None,
) -> ModelCallResult:
    return ModelCallResult(ModelOutputEnvelope(payload), metadata or _metadata(request))


def _error(
    request: ModelCallRequest,
    *,
    metadata: ProviderCallMetadata | None = None,
    message: str = "error-message-marker",
) -> ModelRuntimeError:
    return ModelRuntimeError(
        ModelRuntimeErrorCategory.INVALID_CANDIDATE,
        message,
        False,
        request.identity.model_call_id,
        metadata if metadata is not None else _metadata(request),
    )


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


def _runtime(
    request: ModelCallRequest, outcome: ModelCallResult | ModelRuntimeError
) -> ScriptedModelRuntime:
    return ScriptedModelRuntime(
        scenario=ScriptedModelScenario("scenario-1", (_step(request, outcome),))
    )


def test_single_step_success_returns_exact_result_and_exhausts() -> None:
    request = _request()
    result = _result(request)
    runtime = _runtime(request, result)
    assert runtime.execute(request) is result
    assert runtime.assert_exhausted() is None


def test_execute_rejects_raw_and_subclass_requests() -> None:
    request = _request()
    runtime = _runtime(request, _result(request))
    with pytest.raises(TypeError):
        runtime.execute({"request": request})  # type: ignore[arg-type]
    subclass = _RequestSubclass(
        request.identity,
        request.instructions,
        request.context,
        request.structured_output,
        request.execution_profile,
        request.contract_versions,
    )
    with pytest.raises(TypeError):
        runtime.execute(subclass)
    with pytest.raises(AssertionError, match="not_exhausted"):
        runtime.assert_exhausted()


def test_declared_error_consumes_step_and_raises_exact_error() -> None:
    request = _request()
    error = _error(request)
    runtime = _runtime(request, error)
    with pytest.raises(ModelRuntimeError) as caught:
        runtime.execute(request)
    assert caught.value is error
    assert runtime.assert_exhausted() is None


def test_two_step_success_and_error_follow_tuple_order() -> None:
    first_request = _request(call_id="first")
    second_request = _request(call_id="second")
    first_result = _result(first_request, payload="first-payload")
    second_error = _error(second_request)
    runtime = ScriptedModelRuntime(
        scenario=ScriptedModelScenario(
            "ordered",
            (_step(first_request, first_result), _step(second_request, second_error)),
        )
    )
    assert runtime.execute(first_request) is first_result
    with pytest.raises(ModelRuntimeError) as caught:
        runtime.execute(second_request)
    assert caught.value is second_error
    assert runtime.assert_exhausted() is None


@pytest.mark.parametrize(
    "candidate",
    [
        _request(call_id="wrong"),
        _request(profile_id="wrong"),
        _request(profile_version="wrong"),
        _request(schema_id="wrong"),
        _request(schema_version="wrong"),
    ],
)
def test_request_identity_profile_and_schema_mismatches_do_not_consume(
    candidate: ModelCallRequest,
) -> None:
    expected_request = _request()
    result = _result(expected_request)
    runtime = _runtime(expected_request, result)
    with pytest.raises(AssertionError) as caught:
        runtime.execute(candidate)
    assert "scenario-1" in str(caught.value)
    assert "ordinal 1" in str(caught.value)
    assert "instruction-marker" not in str(caught.value)
    assert runtime.execute(expected_request) is result


def test_result_and_error_call_identity_mismatches_do_not_consume() -> None:
    request = _request()
    wrong_result_request = _request(call_id="wrong-result")
    wrong_result = _result(wrong_result_request)
    runtime = _runtime(request, wrong_result)
    with pytest.raises(AssertionError, match="outcome.model_call_id"):
        runtime.execute(request)
    with pytest.raises(AssertionError, match="not_exhausted"):
        runtime.assert_exhausted()

    wrong_error_request = _request(call_id="wrong-error")
    wrong_error = _error(wrong_error_request)
    runtime = _runtime(request, wrong_error)
    with pytest.raises(AssertionError, match="outcome.model_call_id"):
        runtime.execute(request)
    with pytest.raises(AssertionError, match="not_exhausted"):
        runtime.assert_exhausted()


@pytest.mark.parametrize(
    "field",
    [
        "prompt_template_id",
        "prompt_template_version",
        "output_schema_id",
        "output_schema_version",
        "skill_contract_version",
        "domain_validator_version",
        "execution_profile_id",
        "execution_profile_version",
        "context_assembly_version",
    ],
)
def test_version_tuple_reference_mismatch_does_not_consume(field: str) -> None:
    request = _request()
    bad_version = replace(_version_tuple(request), **{field: "mismatch"})
    result = _result(request, metadata=_metadata(request, version_tuple=bad_version))
    runtime = _runtime(request, result)
    with pytest.raises(AssertionError, match=f"version_tuple.{field}"):
        runtime.execute(request)
    with pytest.raises(AssertionError, match=f"version_tuple.{field}"):
        runtime.execute(request)
    with pytest.raises(AssertionError, match="not_exhausted"):
        runtime.assert_exhausted()


def test_error_version_tuple_mismatch_does_not_consume() -> None:
    request = _request()
    bad_version = replace(_version_tuple(request), context_assembly_version="mismatch")
    error = _error(request, metadata=_metadata(request, version_tuple=bad_version))
    runtime = _runtime(request, error)
    with pytest.raises(AssertionError, match="version_tuple.context_assembly_version"):
        runtime.execute(request)
    with pytest.raises(AssertionError, match="version_tuple.context_assembly_version"):
        runtime.execute(request)


def test_exhaustion_and_empty_scenario_fail_without_ordinal_change() -> None:
    request = _request()
    runtime = _runtime(request, _result(request))
    assert runtime.execute(request)
    with pytest.raises(AssertionError, match="script_exhausted"):
        runtime.execute(request)
    with pytest.raises(AssertionError, match="script_exhausted"):
        runtime.execute(request)
    empty = ScriptedModelRuntime(scenario=ScriptedModelScenario("empty", ()))
    with pytest.raises(AssertionError, match="script_exhausted"):
        empty.execute(request)
    assert empty.assert_exhausted() is None


def test_premature_assert_exhausted_does_not_change_ordinal() -> None:
    request = _request()
    result = _result(request)
    runtime = _runtime(request, result)
    with pytest.raises(AssertionError, match="not_exhausted"):
        runtime.assert_exhausted()
    assert runtime.execute(request) is result


def test_diagnostics_exclude_unsafe_request_and_outcome_content() -> None:
    request = _request(context_marker="context-secret")
    bad_request = _request(call_id="wrong")
    result = _result(request, payload="payload-secret")
    runtime = _runtime(request, result)
    with pytest.raises(AssertionError) as caught:
        runtime.execute(bad_request)
    message = str(caught.value)
    for unsafe in (
        "instruction-marker",
        "context-secret",
        "schema-marker",
        "payload-secret",
        "error-message-marker",
    ):
        assert unsafe not in message


def test_request_scenario_step_and_outcome_remain_unmodified() -> None:
    request = _request()
    result = _result(request)
    step = _step(request, result)
    scenario = ScriptedModelScenario("immutable", (step,))
    runtime = ScriptedModelRuntime(scenario=scenario)
    assert runtime.execute(request) is result
    assert scenario.steps == (step,)
    assert step.outcome is result
    assert result.output_envelope.payload_text == "payload-marker"
