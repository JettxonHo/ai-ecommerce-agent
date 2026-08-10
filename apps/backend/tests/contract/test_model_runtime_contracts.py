"""Contract tests for the provider-neutral synchronous model runtime port."""

from __future__ import annotations

from dataclasses import fields, is_dataclass, replace
from inspect import iscoroutinefunction, signature
from typing import get_type_hints

import pytest

from ai_ecommerce_agent import application as application_package
from ai_ecommerce_agent.application import model_runtime
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelCallResult,
    ModelExecutionProfile,
    ModelOutputEnvelope,
    ModelRecoveryKind,
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
    ModelRuntimePort,
    ModelRuntimeVersionTuple,
    ModelTokenUsage,
    ProviderAttemptId,
    ProviderCallMetadata,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.contract


_EXPECTED_PUBLIC = [
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


class _IntSubclass(int):
    pass


def _content() -> StructuredContent:
    return StructuredContent.from_mapping({"sku": "anchor"})


def _profile() -> ModelExecutionProfile:
    return ModelExecutionProfile("profile", "v1")


def _schema() -> StructuredOutputSpec:
    return StructuredOutputSpec("schema", "v1", _content())


def _versions() -> ModelCallContractVersions:
    return ModelCallContractVersions("prompt", "v1", "skill", "domain", "ctx")


def _identity() -> ModelCallIdentity:
    return ModelCallIdentity(ModelCallId("call-1"))


def _runtime_version() -> ModelRuntimeVersionTuple:
    return ModelRuntimeVersionTuple(
        "provider",
        "api",
        "sdk",
        "configured",
        None,
        "prompt",
        "v1",
        "schema",
        "v1",
        "skill",
        "domain",
        "profile",
        "v1",
        "ctx",
    )


def _metadata(
    *, provider_attempt_ids: tuple[ProviderAttemptId, ...] | None = None
) -> ProviderCallMetadata:
    attempts = provider_attempt_ids or (ProviderAttemptId("attempt-1"),)
    return ProviderCallMetadata(
        ModelCallId("call-1"),
        attempts,
        _runtime_version(),
        "response",
        None,
        ModelTokenUsage(2, 3, 99),
        12,
    )


def _request() -> ModelCallRequest:
    return ModelCallRequest(
        _identity(), "instructions", _content(), _schema(), _profile(), _versions()
    )


def test_facade_has_exact_ordered_symbols_and_no_alias() -> None:
    assert model_runtime.__all__ == _EXPECTED_PUBLIC
    assert [getattr(model_runtime, name) for name in _EXPECTED_PUBLIC] == [
        ModelCallContractVersions,
        ModelCallId,
        ModelCallIdentity,
        ModelCallRequest,
        ModelCallResult,
        ModelExecutionProfile,
        ModelOutputEnvelope,
        ModelRecoveryKind,
        ModelRuntimeError,
        ModelRuntimeErrorCategory,
        ModelRuntimePort,
        ModelRuntimeVersionTuple,
        ModelTokenUsage,
        ProviderAttemptId,
        ProviderCallMetadata,
        StructuredOutputSpec,
    ]
    assert not hasattr(model_runtime, "ModelRuntime")
    public_names = {
        name
        for name in model_runtime.__dict__
        if not name.startswith("_") and name != "annotations"
    }
    assert public_names == set(_EXPECTED_PUBLIC)


def test_model_runtime_symbols_are_not_reexported_by_application_package() -> None:
    assert all(not hasattr(application_package, name) for name in _EXPECTED_PUBLIC)


@pytest.mark.parametrize(
    "cls, names",
    [
        (ModelCallId, ["value"]),
        (ProviderAttemptId, ["value"]),
        (ModelCallIdentity, ["model_call_id", "recovers_call_id", "recovery_kind"]),
        (ModelExecutionProfile, ["execution_profile_id", "execution_profile_version"]),
        (StructuredOutputSpec, ["output_schema_id", "output_schema_version", "schema"]),
        (
            ModelCallContractVersions,
            [
                "prompt_template_id",
                "prompt_template_version",
                "skill_contract_version",
                "domain_validator_version",
                "context_assembly_version",
            ],
        ),
        (
            ModelCallRequest,
            [
                "identity",
                "instructions",
                "context",
                "structured_output",
                "execution_profile",
                "contract_versions",
            ],
        ),
        (
            ModelRuntimeVersionTuple,
            [
                "provider_id",
                "api_family",
                "sdk_version",
                "configured_model_id",
                "resolved_model_id",
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
        ),
        (ModelTokenUsage, ["input_tokens", "output_tokens", "total_tokens"]),
        (
            ProviderCallMetadata,
            [
                "model_call_id",
                "provider_attempt_ids",
                "version_tuple",
                "provider_response_id",
                "provider_request_id",
                "usage",
                "latency_ms",
            ],
        ),
        (ModelOutputEnvelope, ["payload_text"]),
        (ModelCallResult, ["output_envelope", "provider_metadata"]),
        (
            ModelRuntimeError,
            [
                "category",
                "message",
                "retryability",
                "model_call_id",
                "provider_metadata",
            ],
        ),
    ],
)
def test_dataclass_fields_are_exact_and_slotted(
    cls: type[object], names: list[str]
) -> None:
    assert is_dataclass(cls)
    assert [field.name for field in fields(cls)] == names
    assert hasattr(cls, "__slots__")
    assert "__dict__" not in cls.__slots__  # type: ignore[attr-defined]


def test_ordinary_dtos_are_frozen_and_identity_ordered() -> None:
    ordinary = (
        ModelCallId("a"),
        ProviderAttemptId("a"),
        _identity(),
        _profile(),
        _schema(),
        _versions(),
        _request(),
        _runtime_version(),
        ModelTokenUsage(1, 2, 3),
        _metadata(),
        ModelOutputEnvelope("payload"),
        ModelCallResult(ModelOutputEnvelope("payload"), _metadata()),
    )
    for value in ordinary:
        with pytest.raises((AttributeError, TypeError)):
            value.__dict__ = {}  # type: ignore[attr-defined]
        field_name = fields(value)[0].name
        with pytest.raises((AttributeError, TypeError)):
            setattr(value, field_name, None)
        with pytest.raises((AttributeError, TypeError)):
            delattr(value, field_name)
    assert ModelCallId("a") < ModelCallId("b")
    assert ProviderAttemptId("a") < ProviderAttemptId("b")
    assert ModelCallIdentity(ModelCallId("a")) < ModelCallIdentity(ModelCallId("b"))


def test_exact_annotations_for_identity_request_result_and_error() -> None:
    assert get_type_hints(ModelCallId) == {"value": str}
    assert get_type_hints(ProviderAttemptId) == {"value": str}
    assert get_type_hints(ModelCallIdentity) == {
        "model_call_id": ModelCallId,
        "recovers_call_id": ModelCallId | None,
        "recovery_kind": ModelRecoveryKind | None,
    }
    assert get_type_hints(ModelCallRequest) == {
        "identity": ModelCallIdentity,
        "instructions": str,
        "context": StructuredContent,
        "structured_output": StructuredOutputSpec,
        "execution_profile": ModelExecutionProfile,
        "contract_versions": ModelCallContractVersions,
    }
    assert get_type_hints(ModelCallResult) == {
        "output_envelope": ModelOutputEnvelope,
        "provider_metadata": ProviderCallMetadata,
    }
    assert get_type_hints(ModelRuntimeError) == {
        "category": ModelRuntimeErrorCategory,
        "message": str,
        "retryability": bool,
        "model_call_id": ModelCallId,
        "provider_metadata": ProviderCallMetadata | None,
    }


def test_nested_values_are_supplied_identity_and_order_preserving() -> None:
    identity = _identity()
    context = _content()
    schema = _schema()
    profile = _profile()
    versions = _versions()
    request = ModelCallRequest(
        identity, "instructions", context, schema, profile, versions
    )
    assert request.identity is identity
    assert request.context is context
    assert request.structured_output is schema
    assert request.execution_profile is profile
    assert request.contract_versions is versions

    attempts = (ProviderAttemptId("first"), ProviderAttemptId("second"))
    metadata = _metadata(provider_attempt_ids=attempts)
    assert metadata.provider_attempt_ids is attempts
    assert metadata.provider_attempt_ids == attempts


def test_nested_fields_reject_raw_values_and_preserve_exact_instances() -> None:
    recovered_identity = ModelCallIdentity(
        ModelCallId("call"), ModelCallId("previous"), ModelRecoveryKind.REPAIR
    )
    for field_name, raw_value in (
        ("model_call_id", {"raw": "id"}),
        ("recovery_kind", "repair"),
    ):
        with pytest.raises(TypeError):
            replace(recovered_identity, **{field_name: raw_value})

    with pytest.raises(TypeError):
        replace(_schema(), schema={"raw": "schema"})
    request = _request()
    for field_name, raw_value in (
        ("identity", {"raw": "identity"}),
        ("context", {"raw": "context"}),
        ("structured_output", {"raw": "schema"}),
        ("execution_profile", {"raw": "profile"}),
        ("contract_versions", {"raw": "versions"}),
    ):
        with pytest.raises(TypeError):
            replace(request, **{field_name: raw_value})

    metadata = _metadata()
    for field_name, raw_value in (
        ("provider_attempt_ids", [ProviderAttemptId("raw")]),
        ("provider_attempt_ids", ("raw",)),
        ("version_tuple", {"raw": "version"}),
        ("usage", {"raw": "usage"}),
    ):
        with pytest.raises(TypeError):
            replace(metadata, **{field_name: raw_value})
    with pytest.raises(TypeError):
        replace(metadata, latency_ms=True)
    with pytest.raises(ValueError):
        replace(metadata, latency_ms=-1)

    result = ModelCallResult(ModelOutputEnvelope("payload"), metadata)
    with pytest.raises(TypeError):
        replace(result, output_envelope="raw")
    with pytest.raises(TypeError):
        replace(result, provider_metadata={"raw": "metadata"})

    error = ModelRuntimeError(
        ModelRuntimeErrorCategory.INVALID_REQUEST,
        "message",
        True,
        ModelCallId("call-1"),
    )
    with pytest.raises(TypeError):
        replace(error, category="invalid_request")
    with pytest.raises(TypeError):
        replace(error, model_call_id="call-1")
    usage = ModelTokenUsage(1, 2, 99)
    assert usage.total_tokens == 99


def test_error_is_non_frozen_and_accepts_both_supplied_retryability_values() -> None:
    for retryability in (False, True):
        error = ModelRuntimeError(
            ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            "message",
            retryability,
            ModelCallId("call"),
        )
        assert error.retryability is retryability
        error.message = "updated"
        assert error.message == "updated"
        del error.provider_metadata
        assert not hasattr(error, "provider_metadata")


def test_recovery_pair_and_self_recovery_invariants() -> None:
    call = ModelCallId("call")
    recovered = ModelCallId("recovered")
    assert ModelCallIdentity(call, recovered, ModelRecoveryKind.REPAIR)
    with pytest.raises(ValueError):
        ModelCallIdentity(call, recovered)
    with pytest.raises(ValueError):
        ModelCallIdentity(call, None, ModelRecoveryKind.REPAIR)
    with pytest.raises(ValueError):
        ModelCallIdentity(call, ModelCallId("call"), ModelRecoveryKind.INCOMPLETE)


def test_catalogs_have_exact_order_and_values() -> None:
    assert list(ModelRecoveryKind) == [
        ModelRecoveryKind.INCOMPLETE,
        ModelRecoveryKind.REPAIR,
        ModelRecoveryKind.REGENERATION,
    ]
    assert [kind.value for kind in ModelRecoveryKind] == [
        "incomplete",
        "repair",
        "regeneration",
    ]
    assert [category.value for category in ModelRuntimeErrorCategory] == [
        "configuration_or_access",
        "invalid_request",
        "transient_provider_failure",
        "refusal",
        "incomplete_output",
        "invalid_candidate",
        "cancelled_or_superseded",
    ]


def test_strict_primitive_validation_rejects_null_raw_and_subclasses() -> None:
    with pytest.raises(TypeError):
        ModelCallId(_TextSubclass("call"))
    with pytest.raises((TypeError, ValueError)):
        ModelCallId("")
    with pytest.raises((TypeError, ValueError)):
        ModelOutputEnvelope({"raw": "payload"})  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ModelTokenUsage(_IntSubclass(1), 2, 3)
    with pytest.raises(TypeError):
        ModelTokenUsage(True, 2, 3)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ModelTokenUsage(1, 2, None)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        ModelTokenUsage(1, 2, -1)
    with pytest.raises(TypeError):
        ModelRuntimeError(
            ModelRuntimeErrorCategory.INVALID_REQUEST,
            "message",
            1,  # type: ignore[arg-type]
            ModelCallId("call"),
        )
    with pytest.raises(TypeError):
        ModelCallRequest(
            _identity(),
            "instructions",
            {"raw": "context"},  # type: ignore[arg-type]
            _schema(),
            _profile(),
            _versions(),
        )


def test_every_text_field_rejects_subclasses_and_nulls() -> None:
    cases = (
        (ModelCallId("call"), "value"),
        (ProviderAttemptId("attempt"), "value"),
        (ModelExecutionProfile("profile", "v1"), "execution_profile_id"),
        (ModelExecutionProfile("profile", "v1"), "execution_profile_version"),
        (StructuredOutputSpec("schema", "v1", _content()), "output_schema_id"),
        (
            StructuredOutputSpec("schema", "v1", _content()),
            "output_schema_version",
        ),
        (ModelCallContractVersions("a", "b", "c", "d", "e"), "prompt_template_id"),
        (
            ModelCallContractVersions("a", "b", "c", "d", "e"),
            "prompt_template_version",
        ),
        (ModelCallContractVersions("a", "b", "c", "d", "e"), "skill_contract_version"),
        (
            ModelCallContractVersions("a", "b", "c", "d", "e"),
            "domain_validator_version",
        ),
        (
            ModelCallContractVersions("a", "b", "c", "d", "e"),
            "context_assembly_version",
        ),
        (_request(), "instructions"),
        (_runtime_version(), "provider_id"),
        (_runtime_version(), "api_family"),
        (_runtime_version(), "sdk_version"),
        (_runtime_version(), "configured_model_id"),
        (_runtime_version(), "prompt_template_id"),
        (_runtime_version(), "prompt_template_version"),
        (_runtime_version(), "output_schema_id"),
        (_runtime_version(), "output_schema_version"),
        (_runtime_version(), "skill_contract_version"),
        (_runtime_version(), "domain_validator_version"),
        (_runtime_version(), "execution_profile_id"),
        (_runtime_version(), "execution_profile_version"),
        (_runtime_version(), "context_assembly_version"),
        (_metadata(), "provider_response_id"),
        (_metadata(), "provider_request_id"),
        (ModelOutputEnvelope("payload"), "payload_text"),
    )
    optional_fields = {"provider_response_id", "provider_request_id"}
    for instance, field_name in cases:
        with pytest.raises(TypeError):
            replace(instance, **{field_name: _TextSubclass("poison")})
        if field_name in optional_fields:
            assert getattr(replace(instance, **{field_name: None}), field_name) is None
        else:
            with pytest.raises((TypeError, ValueError)):
                replace(instance, **{field_name: None})

    with pytest.raises(ValueError):
        replace(_runtime_version(), resolved_model_id=" ")
    with pytest.raises(TypeError):
        replace(_runtime_version(), resolved_model_id=_TextSubclass("poison"))


def test_output_and_metadata_validation_preserves_supplied_values() -> None:
    usage = ModelTokenUsage(1, 2, 99)
    attempts = (ProviderAttemptId("a"),)
    metadata = ProviderCallMetadata(
        ModelCallId("call"), attempts, _runtime_version(), None, None, usage, 0
    )
    assert metadata.usage is usage
    assert metadata.provider_attempt_ids is attempts
    envelope = ModelOutputEnvelope("payload")
    result = ModelCallResult(envelope, metadata)
    assert result.output_envelope is envelope
    assert result.provider_metadata is metadata
    with pytest.raises(ValueError):
        ModelRuntimeVersionTuple(
            "provider",
            "api",
            "sdk",
            "configured",
            "",
            "prompt",
            "v1",
            "schema",
            "v1",
            "skill",
            "domain",
            "profile",
            "v1",
            "ctx",
        )


def test_error_is_catchable_slotted_and_metadata_identity_checked() -> None:
    metadata = _metadata()
    error = ModelRuntimeError(
        ModelRuntimeErrorCategory.INVALID_CANDIDATE,
        "invalid candidate",
        False,
        ModelCallId("call-1"),
        metadata,
    )
    with pytest.raises(ModelRuntimeError) as caught:
        raise error
    assert caught.value is error
    assert str(error) == "invalid candidate"
    assert error.args == ("invalid candidate",)
    assert "__dict__" not in ModelRuntimeError.__slots__
    with pytest.raises(ValueError):
        ModelRuntimeError(
            ModelRuntimeErrorCategory.INVALID_CANDIDATE,
            "invalid candidate",
            False,
            ModelCallId("other"),
            metadata,
        )


def test_runtime_port_is_synchronous_and_structurally_checkable() -> None:
    request = _request()
    result = ModelCallResult(ModelOutputEnvelope("payload"), _metadata())

    class _RuntimeDouble:
        def execute(self, request: ModelCallRequest) -> ModelCallResult:
            assert request is not None
            return result

    method = ModelRuntimePort.execute
    assert list(signature(method).parameters) == ["self", "request"]
    assert get_type_hints(method) == {
        "request": ModelCallRequest,
        "return": ModelCallResult,
    }
    assert not iscoroutinefunction(method)
    assert not iscoroutinefunction(_RuntimeDouble.execute)
    assert isinstance(_RuntimeDouble(), ModelRuntimePort)
    assert _RuntimeDouble().execute(request) is result
