"""Provider-neutral synchronous model runtime contracts."""

from __future__ import annotations

from dataclasses import dataclass as _dataclass
from enum import StrEnum as _StrEnum
from typing import Protocol as _Protocol
from typing import runtime_checkable as _runtime_checkable

from ai_ecommerce_agent.shared_kernel.structured_content import (
    StructuredContent as _StructuredContent,
)


def _text(value: object, name: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _optional_text(value: object, name: str) -> None:
    if value is not None:
        _text(value, name)


def _exact(value: object, expected: type[object], name: str) -> None:
    if type(value) is not expected:
        raise TypeError(f"{name} must be a {expected.__name__}")


def _optional_exact(value: object, expected: type[object], name: str) -> None:
    if value is not None:
        _exact(value, expected, name)


def _integer(value: object, name: str) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an int")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")


@_dataclass(frozen=True, slots=True, order=True)
class ModelCallId:
    value: str

    def __post_init__(self) -> None:
        _text(self.value, "value")


@_dataclass(frozen=True, slots=True, order=True)
class ProviderAttemptId:
    value: str

    def __post_init__(self) -> None:
        _text(self.value, "value")


class ModelRecoveryKind(_StrEnum):
    INCOMPLETE = "incomplete"
    REPAIR = "repair"
    REGENERATION = "regeneration"


@_dataclass(frozen=True, slots=True, order=True)
class ModelCallIdentity:
    model_call_id: ModelCallId
    recovers_call_id: ModelCallId | None = None
    recovery_kind: ModelRecoveryKind | None = None

    def __post_init__(self) -> None:
        _exact(self.model_call_id, ModelCallId, "model_call_id")
        has_recovered = self.recovers_call_id is not None
        has_kind = self.recovery_kind is not None
        if has_recovered != has_kind:
            raise ValueError("recovery identity fields must be both present or null")
        if has_recovered:
            recovers_call_id = self.recovers_call_id
            if recovers_call_id is None:
                raise ValueError(
                    "recovery identity fields must be both present or null"
                )
            _exact(recovers_call_id, ModelCallId, "recovers_call_id")
            _exact(self.recovery_kind, ModelRecoveryKind, "recovery_kind")
            if recovers_call_id.value == self.model_call_id.value:
                raise ValueError("a model call cannot recover itself")


@_dataclass(frozen=True, slots=True)
class ModelExecutionProfile:
    execution_profile_id: str
    execution_profile_version: str

    def __post_init__(self) -> None:
        _text(self.execution_profile_id, "execution_profile_id")
        _text(self.execution_profile_version, "execution_profile_version")


@_dataclass(frozen=True, slots=True)
class StructuredOutputSpec:
    output_schema_id: str
    output_schema_version: str
    schema: _StructuredContent

    def __post_init__(self) -> None:
        _text(self.output_schema_id, "output_schema_id")
        _text(self.output_schema_version, "output_schema_version")
        _exact(self.schema, _StructuredContent, "schema")


@_dataclass(frozen=True, slots=True)
class ModelCallContractVersions:
    prompt_template_id: str
    prompt_template_version: str
    skill_contract_version: str
    domain_validator_version: str
    context_assembly_version: str

    def __post_init__(self) -> None:
        for name in (
            "prompt_template_id",
            "prompt_template_version",
            "skill_contract_version",
            "domain_validator_version",
            "context_assembly_version",
        ):
            _text(getattr(self, name), name)


@_dataclass(frozen=True, slots=True)
class ModelCallRequest:
    identity: ModelCallIdentity
    instructions: str
    context: _StructuredContent
    structured_output: StructuredOutputSpec
    execution_profile: ModelExecutionProfile
    contract_versions: ModelCallContractVersions

    def __post_init__(self) -> None:
        _exact(self.identity, ModelCallIdentity, "identity")
        _text(self.instructions, "instructions")
        _exact(self.context, _StructuredContent, "context")
        _exact(self.structured_output, StructuredOutputSpec, "structured_output")
        _exact(self.execution_profile, ModelExecutionProfile, "execution_profile")
        _exact(self.contract_versions, ModelCallContractVersions, "contract_versions")


@_dataclass(frozen=True, slots=True)
class ModelRuntimeVersionTuple:
    provider_id: str
    api_family: str
    sdk_version: str
    configured_model_id: str
    resolved_model_id: str | None
    prompt_template_id: str
    prompt_template_version: str
    output_schema_id: str
    output_schema_version: str
    skill_contract_version: str
    domain_validator_version: str
    execution_profile_id: str
    execution_profile_version: str
    context_assembly_version: str

    def __post_init__(self) -> None:
        for name in (
            "provider_id",
            "api_family",
            "sdk_version",
            "configured_model_id",
            "prompt_template_id",
            "prompt_template_version",
            "output_schema_id",
            "output_schema_version",
            "skill_contract_version",
            "domain_validator_version",
            "execution_profile_id",
            "execution_profile_version",
            "context_assembly_version",
        ):
            _text(getattr(self, name), name)
        _optional_text(self.resolved_model_id, "resolved_model_id")


@_dataclass(frozen=True, slots=True)
class ModelTokenUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int

    def __post_init__(self) -> None:
        _integer(self.input_tokens, "input_tokens")
        _integer(self.output_tokens, "output_tokens")
        _integer(self.total_tokens, "total_tokens")


@_dataclass(frozen=True, slots=True)
class ProviderCallMetadata:
    model_call_id: ModelCallId
    provider_attempt_ids: tuple[ProviderAttemptId, ...]
    version_tuple: ModelRuntimeVersionTuple
    provider_response_id: str | None
    provider_request_id: str | None
    usage: ModelTokenUsage | None
    latency_ms: int

    def __post_init__(self) -> None:
        _exact(self.model_call_id, ModelCallId, "model_call_id")
        _exact(self.provider_attempt_ids, tuple, "provider_attempt_ids")
        for attempt_id in self.provider_attempt_ids:
            _exact(attempt_id, ProviderAttemptId, "provider_attempt_ids item")
        _exact(self.version_tuple, ModelRuntimeVersionTuple, "version_tuple")
        _optional_text(self.provider_response_id, "provider_response_id")
        _optional_text(self.provider_request_id, "provider_request_id")
        _optional_exact(self.usage, ModelTokenUsage, "usage")
        _integer(self.latency_ms, "latency_ms")


@_dataclass(frozen=True, slots=True)
class ModelOutputEnvelope:
    payload_text: str

    def __post_init__(self) -> None:
        _text(self.payload_text, "payload_text")


@_dataclass(frozen=True, slots=True)
class ModelCallResult:
    output_envelope: ModelOutputEnvelope
    provider_metadata: ProviderCallMetadata

    def __post_init__(self) -> None:
        _exact(self.output_envelope, ModelOutputEnvelope, "output_envelope")
        _exact(self.provider_metadata, ProviderCallMetadata, "provider_metadata")


class ModelRuntimeErrorCategory(_StrEnum):
    CONFIGURATION_OR_ACCESS = "configuration_or_access"
    INVALID_REQUEST = "invalid_request"
    TRANSIENT_PROVIDER_FAILURE = "transient_provider_failure"
    REFUSAL = "refusal"
    INCOMPLETE_OUTPUT = "incomplete_output"
    INVALID_CANDIDATE = "invalid_candidate"
    CANCELLED_OR_SUPERSEDED = "cancelled_or_superseded"


@_dataclass(slots=True)
class ModelRuntimeError(Exception):
    category: ModelRuntimeErrorCategory
    message: str
    retryability: bool
    model_call_id: ModelCallId
    provider_metadata: ProviderCallMetadata | None = None

    def __post_init__(self) -> None:
        _exact(self.category, ModelRuntimeErrorCategory, "category")
        _text(self.message, "message")
        if type(self.retryability) is not bool:
            raise TypeError("retryability must be a bool")
        _exact(self.model_call_id, ModelCallId, "model_call_id")
        _optional_exact(
            self.provider_metadata, ProviderCallMetadata, "provider_metadata"
        )
        if (
            self.provider_metadata is not None
            and self.provider_metadata.model_call_id.value != self.model_call_id.value
        ):
            raise ValueError("provider metadata must belong to the model call")
        Exception.__init__(self, self.message)


@_runtime_checkable
class ModelRuntimePort(_Protocol):
    def execute(self, request: ModelCallRequest) -> ModelCallResult: ...


__all__ = [
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
