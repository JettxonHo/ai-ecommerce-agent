"""Provider-free cost admission and bounded request guard for P2."""

from __future__ import annotations

import json as _json
from collections.abc import Callable
from dataclasses import dataclass as _dataclass
from typing import Final

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest as _ModelCallRequest,
)
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallResult as _ModelCallResult,
)
from ai_ecommerce_agent.application.model_runtime import (
    ModelExecutionProfile as _ModelExecutionProfile,
)
from ai_ecommerce_agent.application.model_runtime import (
    ModelRuntimePort as _ModelRuntimePort,
)
from ai_ecommerce_agent.application.model_runtime import (
    StructuredOutputSpec as _StructuredOutputSpec,
)

from ._request_preparation import (
    DeepSeekCallParameters as _DeepSeekCallParameters,
)
from ._request_preparation import (
    DeepSeekReasoningEffort as _DeepSeekReasoningEffort,
)
from ._request_preparation import (
    PreparedDeepSeekCall as _PreparedDeepSeekCall,
)
from ._request_preparation import (
    prepare_deepseek_call as _prepare_deepseek_call,
)

_MICRO_USD_PER_MILLION: Final[int] = 1_000_000
_MODEL_ID: Final[str] = "deepseek-v4-pro"
_CONTEXT_WINDOW_TOKENS: Final[int] = 1_000_000
_INPUT_CACHE_MISS_MICRO_USD_PER_MILLION: Final[int] = 1_320_000
_INPUT_CACHE_HIT_MICRO_USD_PER_MILLION: Final[int] = 44_000
_OUTPUT_MICRO_USD_PER_MILLION: Final[int] = 3_960_000
_PRICING_SOURCE_URL: Final[str] = "https://api-docs.deepseek.com/quick_start/pricing/"
_PRICING_RECORD_ID: Final[str] = "deepseek-v4-pro-2026-08-30-peak-v1"

_P2_CALL_IDS: Final[tuple[str, ...]] = tuple(
    f"P2-P01-A1-stage-{index}" for index in range(1, 6)
)
_P2_PROFILE_IDS: Final[tuple[str, ...]] = (
    "product_intake_v1",
    "customer_insight_v1",
    "product_positioning_v1",
    "marketing_brief_v1",
    "xiaohongshu_mapping_v1",
)
_P2_PROFILE_VERSIONS: Final[tuple[str, ...]] = ("v1", "v1", "v1", "v1", "v2")
_P2_OUTPUT_SCHEMA_IDS: Final[tuple[str, ...]] = (
    "product_intake_fact_candidate",
    "customer_insight_candidate",
    "product_positioning_candidate",
    "marketing_brief_candidate",
    "xiaohongshu_brief_candidate",
)
_P2_OUTPUT_SCHEMA_VERSIONS: Final[tuple[str, ...]] = ("v1", "v1", "v1", "v1", "v1")
_P2_OUTPUT_CEILINGS: Final[tuple[int, ...]] = (
    8_192,
    12_288,
    16_384,
    16_384,
    16_384,
)
_P2_TIMEOUTS: Final[tuple[int, ...]] = (120, 180, 240, 180, 240)

REQUEST_FRAMING_VERSION: Final[str] = "utf8-json-framing-v1"
REQUEST_FRAMING_RESERVE_BYTES: Final[int] = 256
TOKEN_PROXY_BYTES_PER_TOKEN: Final[int] = 1
MAX_P2_CALLS: Final[int] = 5


@_dataclass(frozen=True, slots=True)
class DeepSeekPricingRecord:
    """Versioned official pricing used for an authorization reservation."""

    record_id: str
    source_url: str
    model_id: str
    context_window_tokens: int
    input_cache_miss_micro_usd_per_million: int
    output_micro_usd_per_million: int
    input_cache_hit_micro_usd_per_million: int

    def __post_init__(self) -> None:
        for name in ("record_id", "source_url", "model_id"):
            value = getattr(self, name)
            if type(value) is not str:
                raise TypeError(f"{name} must be a string")
            if not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in (
            "context_window_tokens",
            "input_cache_miss_micro_usd_per_million",
            "output_micro_usd_per_million",
            "input_cache_hit_micro_usd_per_million",
        ):
            value = getattr(self, name)
            if type(value) is not int:
                raise TypeError(f"{name} must be an int")
            if value <= 0:
                raise ValueError(f"{name} must be positive")


DEEPSEEK_PRICING_RECORD: Final[DeepSeekPricingRecord] = DeepSeekPricingRecord(
    record_id=_PRICING_RECORD_ID,
    source_url=_PRICING_SOURCE_URL,
    model_id=_MODEL_ID,
    context_window_tokens=_CONTEXT_WINDOW_TOKENS,
    input_cache_miss_micro_usd_per_million=_INPUT_CACHE_MISS_MICRO_USD_PER_MILLION,
    output_micro_usd_per_million=_OUTPUT_MICRO_USD_PER_MILLION,
    input_cache_hit_micro_usd_per_million=_INPUT_CACHE_HIT_MICRO_USD_PER_MILLION,
)


@_dataclass(frozen=True, slots=True)
class DeepSeekStageBudget:
    """One ordered P2 call's fixed profile and context-derived ceilings."""

    model_call_id: str
    execution_profile: _ModelExecutionProfile
    output_schema_id: str
    output_schema_version: str
    output_token_ceiling: int
    input_token_ceiling: int
    parameters: _DeepSeekCallParameters


@_dataclass(frozen=True, slots=True)
class DeepSeekCostReservation:
    """Conservative peak/cache-miss reservation in integer micro-USD."""

    pricing_record_id: str
    input_token_ceilings: tuple[int, ...]
    output_token_ceilings: tuple[int, ...]
    per_stage_micro_usd: tuple[int, ...]
    reserved_micro_usd: int

    @property
    def required_micro_usd(self) -> int:
        return self.reserved_micro_usd


def _validate_pricing_record(record: DeepSeekPricingRecord) -> None:
    if type(record) is not DeepSeekPricingRecord:
        raise TypeError("pricing_record must be a DeepSeekPricingRecord")
    if record != DEEPSEEK_PRICING_RECORD:
        raise ValueError("pricing record is not the official DeepSeek record")


def _ceil_micro_usd(token_ceiling: int, rate: int) -> int:
    return (token_ceiling * rate + _MICRO_USD_PER_MILLION - 1) // (
        _MICRO_USD_PER_MILLION
    )


def _stage_budgets(record: DeepSeekPricingRecord) -> tuple[DeepSeekStageBudget, ...]:
    _validate_pricing_record(record)
    budgets: list[DeepSeekStageBudget] = []
    for index, (
        call_id,
        profile_id,
        profile_version,
        schema_id,
        schema_version,
        output_ceiling,
        timeout,
    ) in enumerate(
        zip(
            _P2_CALL_IDS,
            _P2_PROFILE_IDS,
            _P2_PROFILE_VERSIONS,
            _P2_OUTPUT_SCHEMA_IDS,
            _P2_OUTPUT_SCHEMA_VERSIONS,
            _P2_OUTPUT_CEILINGS,
            _P2_TIMEOUTS,
            strict=True,
        ),
        start=1,
    ):
        profile = _ModelExecutionProfile(profile_id, profile_version)
        parameters = _DeepSeekCallParameters(
            execution_profile=profile,
            reasoning_effort=_DeepSeekReasoningEffort.HIGH,
            max_output_tokens=output_ceiling,
            timeout_seconds=timeout,
        )
        budgets.append(
            DeepSeekStageBudget(
                model_call_id=call_id,
                execution_profile=profile,
                output_schema_id=schema_id,
                output_schema_version=schema_version,
                output_token_ceiling=output_ceiling,
                input_token_ceiling=record.context_window_tokens - output_ceiling,
                parameters=parameters,
            )
        )
        del index
    return tuple(budgets)


DEEPSEEK_P2_STAGE_BUDGETS: Final[tuple[DeepSeekStageBudget, ...]] = _stage_budgets(
    DEEPSEEK_PRICING_RECORD
)


def calculate_peak_cache_miss_reservation(
    pricing_record: DeepSeekPricingRecord = DEEPSEEK_PRICING_RECORD,
) -> DeepSeekCostReservation:
    """Calculate a full per-stage context/output reservation."""

    budgets = _stage_budgets(pricing_record)
    per_stage = tuple(
        _ceil_micro_usd(
            budget.input_token_ceiling,
            pricing_record.input_cache_miss_micro_usd_per_million,
        )
        + _ceil_micro_usd(
            budget.output_token_ceiling,
            pricing_record.output_micro_usd_per_million,
        )
        for budget in budgets
    )
    return DeepSeekCostReservation(
        pricing_record_id=pricing_record.record_id,
        input_token_ceilings=tuple(budget.input_token_ceiling for budget in budgets),
        output_token_ceilings=tuple(budget.output_token_ceiling for budget in budgets),
        per_stage_micro_usd=per_stage,
        reserved_micro_usd=sum(per_stage),
    )


DEEPSEEK_P2_COST_RESERVATION: Final[DeepSeekCostReservation] = (
    calculate_peak_cache_miss_reservation()
)
DEEPSEEK_P2_RESERVATION_MICRO_USD: Final[int] = (
    DEEPSEEK_P2_COST_RESERVATION.reserved_micro_usd
)


def _canonical_request_body(prepared: _PreparedDeepSeekCall) -> bytes:
    body = _json.dumps(
        prepared.request_body.to_mapping(),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return body.encode("utf-8")


def canonical_request_body_utf8_bytes(
    request: _ModelCallRequest,
    parameters: _DeepSeekCallParameters,
) -> bytes:
    """Prepare one request and return its deterministic UTF-8 body bytes."""

    return _canonical_request_body(
        _prepare_deepseek_call(request=request, parameters=parameters)
    )


def conservative_request_input_tokens(
    request: _ModelCallRequest,
    parameters: _DeepSeekCallParameters,
) -> int:
    """Return a versioned byte/framing token proxy, not exact tokenization."""

    body_bytes = canonical_request_body_utf8_bytes(request, parameters)
    framed_bytes = len(body_bytes) + REQUEST_FRAMING_RESERVE_BYTES
    return (framed_bytes + TOKEN_PROXY_BYTES_PER_TOKEN - 1) // (
        TOKEN_PROXY_BYTES_PER_TOKEN
    )


class DeepSeekCostGateError(ValueError):
    """Safe fixed error for cost admission or bounded runtime violations."""


RuntimeFactory = Callable[
    [tuple[_ModelCallRequest, ...], tuple[str, ...]], _ModelRuntimePort
]


def _validate_planned_requests(
    requests: tuple[_ModelCallRequest, ...],
) -> tuple[DeepSeekStageBudget, ...]:
    if type(requests) is not tuple:
        raise TypeError("planned requests must be a tuple")
    if len(requests) != MAX_P2_CALLS:
        raise DeepSeekCostGateError("exactly five P2 requests are required")
    budgets = DEEPSEEK_P2_STAGE_BUDGETS
    for request, budget in zip(requests, budgets, strict=True):
        if type(request) is not _ModelCallRequest:
            raise TypeError("planned requests must contain ModelCallRequest")
        if request.identity.model_call_id.value != budget.model_call_id:
            raise DeepSeekCostGateError("P2 model call order is invalid")
        if request.identity.recovers_call_id is not None:
            raise DeepSeekCostGateError("P2 recovery calls are not permitted")
        if request.execution_profile != budget.execution_profile:
            raise DeepSeekCostGateError("P2 execution profile is invalid")
        output: _StructuredOutputSpec = request.structured_output
        if (
            output.output_schema_id != budget.output_schema_id
            or output.output_schema_version != budget.output_schema_version
        ):
            raise DeepSeekCostGateError("P2 output schema is invalid")
    return budgets


class _GuardedDeepSeekRuntime:
    """Enforce one ordered, bounded P2 attempt around a runtime adapter."""

    def __init__(
        self,
        delegate: _ModelRuntimePort,
        requests: tuple[_ModelCallRequest, ...],
        budgets: tuple[DeepSeekStageBudget, ...],
    ) -> None:
        self._delegate = delegate
        self._requests = requests
        self._budgets = budgets
        self._call_count = 0
        self._terminal = False

    @property
    def call_count(self) -> int:
        return self._call_count

    def execute(self, request: _ModelCallRequest) -> _ModelCallResult:
        if self._terminal:
            raise DeepSeekCostGateError("P2 runtime attempt is terminal")
        if self._call_count >= MAX_P2_CALLS:
            self._terminal = True
            raise DeepSeekCostGateError("P2 maximum call count exceeded")
        if type(request) is not _ModelCallRequest:
            self._terminal = True
            raise TypeError("request must be a ModelCallRequest")
        expected = self._requests[self._call_count]
        budget = self._budgets[self._call_count]
        if (
            request.identity != expected.identity
            or request.execution_profile != expected.execution_profile
            or request.structured_output.output_schema_id
            != expected.structured_output.output_schema_id
            or request.structured_output.output_schema_version
            != expected.structured_output.output_schema_version
        ):
            self._terminal = True
            raise DeepSeekCostGateError("P2 model call order is invalid")
        try:
            estimated_input_tokens = conservative_request_input_tokens(
                request, budget.parameters
            )
        except Exception:
            self._terminal = True
            raise DeepSeekCostGateError(
                "P2 request budget could not be established"
            ) from None
        if estimated_input_tokens > budget.input_token_ceiling:
            self._terminal = True
            raise DeepSeekCostGateError("P2 request exceeds input ceiling")

        self._call_count += 1
        try:
            return self._delegate.execute(request)
        except Exception:
            self._terminal = True
            raise


class DeepSeekRuntimeAdmissionGate:
    """Authorize one P2 reservation, then expose one guarded runtime factory."""

    def __init__(
        self,
        *,
        runtime_factory: RuntimeFactory,
        owner_cap_micro_usd: int | None,
        pricing_record_id: str | None,
        pricing_record: DeepSeekPricingRecord = DEEPSEEK_PRICING_RECORD,
    ) -> None:
        if not callable(runtime_factory):
            raise TypeError("runtime_factory must be callable")
        _validate_pricing_record(pricing_record)
        self._runtime_factory = runtime_factory
        self._owner_cap_micro_usd = owner_cap_micro_usd
        self._pricing_record_id = pricing_record_id
        self._pricing_record = pricing_record
        self._reservation = calculate_peak_cache_miss_reservation(pricing_record)
        self._authorized_requests: tuple[_ModelCallRequest, ...] | None = None
        self._authorization_attempted = False
        self._runtime_factory_used = False

    @property
    def reservation(self) -> DeepSeekCostReservation:
        return self._reservation

    @property
    def authorized(self) -> bool:
        return self._authorized_requests is not None

    def authorize(self, requests: tuple[_ModelCallRequest, ...]) -> None:
        """Validate owner cap and planned calls exactly once, without I/O."""

        if self._authorization_attempted:
            raise DeepSeekCostGateError("P2 runtime admission is single-use")
        self._authorization_attempted = True
        budgets = _validate_planned_requests(requests)
        del budgets
        if self._owner_cap_micro_usd is None:
            raise DeepSeekCostGateError("owner cost authorization is required")
        if type(self._owner_cap_micro_usd) is not int:
            raise DeepSeekCostGateError("owner cost authorization is invalid")
        if self._owner_cap_micro_usd <= 0:
            raise DeepSeekCostGateError("owner cost authorization is invalid")
        if self._pricing_record_id is None:
            raise DeepSeekCostGateError("pricing record reference is required")
        if self._pricing_record_id != self._pricing_record.record_id:
            raise DeepSeekCostGateError("pricing record reference is mismatched")
        if self._owner_cap_micro_usd < self._reservation.reserved_micro_usd:
            raise DeepSeekCostGateError("owner cost authorization is underfunded")
        self._authorized_requests = requests

    def runtime_factory(
        self,
        requests: tuple[_ModelCallRequest, ...],
        payloads: tuple[str, ...],
    ) -> _ModelRuntimePort:
        """Return one guarded adapter only after successful authorization."""

        if self._authorized_requests is None:
            raise DeepSeekCostGateError("P2 runtime admission is not authorized")
        if self._runtime_factory_used:
            raise DeepSeekCostGateError("P2 runtime factory is single-use")
        if requests != self._authorized_requests:
            raise DeepSeekCostGateError("P2 runtime requests do not match admission")
        self._runtime_factory_used = True
        delegate = self._runtime_factory(requests, payloads)
        budgets = _validate_planned_requests(requests)
        return _GuardedDeepSeekRuntime(delegate, requests, budgets)


__all__ = [
    "DEEPSEEK_P2_COST_RESERVATION",
    "DEEPSEEK_P2_RESERVATION_MICRO_USD",
    "DEEPSEEK_P2_STAGE_BUDGETS",
    "DEEPSEEK_PRICING_RECORD",
    "MAX_P2_CALLS",
    "REQUEST_FRAMING_RESERVE_BYTES",
    "REQUEST_FRAMING_VERSION",
    "TOKEN_PROXY_BYTES_PER_TOKEN",
    "DeepSeekCostGateError",
    "DeepSeekCostReservation",
    "DeepSeekPricingRecord",
    "DeepSeekRuntimeAdmissionGate",
    "DeepSeekStageBudget",
    "RuntimeFactory",
    "calculate_peak_cache_miss_reservation",
    "canonical_request_body_utf8_bytes",
    "conservative_request_input_tokens",
]
