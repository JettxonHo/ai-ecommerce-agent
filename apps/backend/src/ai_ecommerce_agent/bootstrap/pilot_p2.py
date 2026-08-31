"""Lazy, P01-only P2 composition bound to the DeepSeek runtime."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Final

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest,
    ModelCallResult,
    ModelRuntimeError,
    ModelRuntimePort,
)
from ai_ecommerce_agent.bootstrap.deterministic_result_postgres import (
    DeterministicResultPostgresComposition,
    compose_deterministic_result_postgres,
    default_spec_factories,
)
from ai_ecommerce_agent.bootstrap.primary_input_postgres import (
    PrimaryInputPostgresComposition,
    compose_primary_input_postgres,
)
from ai_ecommerce_agent.bootstrap.task_management_postgres import (
    TaskManagementPostgresComposition,
    compose_task_management_postgres,
)
from ai_ecommerce_agent.entrypoints.http import (
    FixedWorkspaceHttpConfig,
    create_task_http_application,
)
from ai_ecommerce_agent.orchestration.deterministic_pipeline import (
    DeterministicPipelineCoordinator,
    PipelineInvocation,
    PipelineResult,
    SpecFactory,
)
from ai_ecommerce_agent.platform.model_runtime.deepseek._cost_gate import (
    DEEPSEEK_P2_RESERVATION_MICRO_USD,
    DEEPSEEK_PRICING_RECORD,
    DeepSeekCostGateError,
    DeepSeekRuntimeAdmissionGate,
)
from ai_ecommerce_agent.platform.model_runtime.deepseek._runtime import (
    create_deepseek_runtime as _real_create_deepseek_runtime,
)
from ai_ecommerce_agent.platform.postgres import PostgresEngineConfig

__all__ = [
    "P2CallObservation",
    "P2RuntimeObserver",
    "PilotP2Composition",
    "PilotP2PostgresComposition",
    "PilotP2Coordinator",
    "compose_pilot_p2_pipeline",
    "compose_pilot_p2_postgres",
    "validate_p2_input",
]


@dataclass(frozen=True, slots=True)
class P2CallObservation:
    """Sanitized metadata for one observed P2 runtime call."""

    model_call_id: str
    status: str
    provider_id: str | None = None
    api_family: str | None = None
    configured_model_id: str | None = None
    resolved_model_id: str | None = None
    sdk_version: str | None = None
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    error_category: str | None = None

    def to_mapping(self) -> dict[str, object]:
        return {
            "model_call_id": self.model_call_id,
            "status": self.status,
            "provider_id": self.provider_id,
            "api_family": self.api_family,
            "configured_model_id": self.configured_model_id,
            "resolved_model_id": self.resolved_model_id,
            "sdk_version": self.sdk_version,
            "latency_ms": self.latency_ms,
            "usage": {
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "total_tokens": self.total_tokens,
            },
            "error_category": self.error_category,
        }


class P2RuntimeObserver:
    """Minimal internal observer for ordered, sanitized P2 call telemetry."""

    def __init__(self) -> None:
        self._calls: list[P2CallObservation] = []
        self._attempted_count = 0

    @property
    def attempted_count(self) -> int:
        return self._attempted_count

    @property
    def completed_count(self) -> int:
        return sum(call.status == "COMPLETED" for call in self._calls)

    @property
    def calls(self) -> tuple[P2CallObservation, ...]:
        return tuple(self._calls)

    def record_attempt(self, request: ModelCallRequest) -> None:
        self._attempted_count += 1
        self._calls.append(
            P2CallObservation(
                model_call_id=request.identity.model_call_id.value,
                status="ATTEMPTED",
            )
        )

    def record_completed(self, result: ModelCallResult) -> None:
        metadata = result.provider_metadata
        usage = metadata.usage
        observation = P2CallObservation(
            model_call_id=metadata.model_call_id.value,
            status="COMPLETED",
            provider_id=metadata.version_tuple.provider_id,
            api_family=metadata.version_tuple.api_family,
            configured_model_id=metadata.version_tuple.configured_model_id,
            resolved_model_id=metadata.version_tuple.resolved_model_id,
            sdk_version=metadata.version_tuple.sdk_version,
            latency_ms=metadata.latency_ms,
            input_tokens=None if usage is None else usage.input_tokens,
            output_tokens=None if usage is None else usage.output_tokens,
            total_tokens=None if usage is None else usage.total_tokens,
        )
        self._replace_last(observation)

    def record_failed(
        self,
        request: ModelCallRequest,
        error: ModelRuntimeError | None,
    ) -> None:
        category = None if error is None else error.category.value
        metadata = None if error is None else error.provider_metadata
        usage = None if metadata is None else metadata.usage
        observation = P2CallObservation(
            model_call_id=request.identity.model_call_id.value,
            status="FAILED",
            provider_id=(
                None if metadata is None else metadata.version_tuple.provider_id
            ),
            api_family=None if metadata is None else metadata.version_tuple.api_family,
            configured_model_id=(
                None if metadata is None else metadata.version_tuple.configured_model_id
            ),
            resolved_model_id=(
                None if metadata is None else metadata.version_tuple.resolved_model_id
            ),
            sdk_version=(
                None if metadata is None else metadata.version_tuple.sdk_version
            ),
            latency_ms=None if metadata is None else metadata.latency_ms,
            input_tokens=None if usage is None else usage.input_tokens,
            output_tokens=None if usage is None else usage.output_tokens,
            total_tokens=None if usage is None else usage.total_tokens,
            error_category=category or "unknown_runtime_failure",
        )
        self._replace_last(observation)

    def snapshot(self) -> Mapping[str, object]:
        calls = tuple(call.to_mapping() for call in self._calls)
        first = self._calls[0] if self._calls else None
        return {
            "attempted_count": self.attempted_count,
            "completed_count": self.completed_count,
            "calls": calls,
            "provider_id": None if first is None else first.provider_id,
            "api_family": None if first is None else first.api_family,
            "configured_model_id": (
                None if first is None else first.configured_model_id
            ),
            "resolved_model_id": None if first is None else first.resolved_model_id,
        }

    def _replace_last(self, observation: P2CallObservation) -> None:
        if self._calls:
            self._calls[-1] = observation
        else:
            self._calls.append(observation)


class _ObservedRuntime:
    def __init__(self, delegate: ModelRuntimePort, observer: P2RuntimeObserver):
        self._delegate = delegate
        self._observer = observer

    def execute(self, request: ModelCallRequest) -> ModelCallResult:
        self._observer.record_attempt(request)
        try:
            result = self._delegate.execute(request)
        except ModelRuntimeError as error:
            self._observer.record_failed(request, error)
            raise
        except Exception:
            self._observer.record_failed(request, None)
            raise
        self._observer.record_completed(result)
        return result

    def close(self) -> None:
        close = getattr(self._delegate, "close", None)
        if callable(close):
            close()


RuntimeBuilder = Callable[
    [tuple[ModelCallRequest, ...], tuple[str, ...]], ModelRuntimePort
]

_P2_SAMPLE_ID: Final[str] = "P01"
_P2_ATTEMPT_ID: Final[str] = "P2-P01-A1"
_P2_CONTEXT_ASSEMBLY_VERSION: Final[str] = "pilot-p2-v1"
_P2_INPUT_FIELDS: Final[tuple[tuple[str, str], ...]] = (
    ("sample_id", _P2_SAMPLE_ID),
    ("attempt_id", _P2_ATTEMPT_ID),
    ("product", "Anker Nano Power Bank"),
    ("model/designation", "A1259"),
    ("color", "Black Stone"),
    ("variant", "42733233766550"),
    ("category", "A"),
)

_SPEC_FACTORIES: Final[tuple[SpecFactory, ...]] = default_spec_factories()


def _create_deepseek_runtime(
    requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
) -> ModelRuntimePort:
    """Private factory seam; tests may replace this symbol with a fake."""

    del requests, payloads
    return _real_create_deepseek_runtime()


def _validate_p2_input(*, sample_id: str, attempt_id: str, input_text: str) -> None:
    if type(sample_id) is not str or sample_id != _P2_SAMPLE_ID:
        raise ValueError("P2 composition requires sample P01")
    if type(attempt_id) is not str or attempt_id != _P2_ATTEMPT_ID:
        raise ValueError("P2 composition requires attempt P2-P01-A1")
    if type(input_text) is not str or not input_text.strip():
        raise ValueError("P2 input must be non-empty text")
    expected_fields = dict(_P2_INPUT_FIELDS)
    observed: dict[str, str] = {}
    for raw_line in input_text.splitlines():
        line = raw_line.strip()
        key, separator, value = line.partition(":")
        if not separator or key not in expected_fields:
            continue
        if key in observed or value.strip() != expected_fields[key]:
            raise ValueError("P2 input identity markers are invalid")
        observed[key] = value.strip()
    if observed != expected_fields:
        raise ValueError("P2 input identity markers are invalid")


def validate_p2_input(*, sample_id: str, attempt_id: str, input_text: str) -> None:
    """Validate the fixed P01/P2 identity without constructing a runtime."""

    _validate_p2_input(
        sample_id=sample_id,
        attempt_id=attempt_id,
        input_text=input_text,
    )


def _p2_input_preflight(
    *, sample_id: str, attempt_id: str, input_text: str
) -> tuple[str, ...]:
    _validate_p2_input(
        sample_id=sample_id,
        attempt_id=attempt_id,
        input_text=input_text,
    )
    return ()


def _validate_authorization(
    *, owner_cap_micro_usd: int | None, pricing_record_id: str | None
) -> tuple[int, str]:
    if type(owner_cap_micro_usd) is not int or owner_cap_micro_usd <= 0:
        raise DeepSeekCostGateError("owner cost authorization is invalid")
    if owner_cap_micro_usd < DEEPSEEK_P2_RESERVATION_MICRO_USD:
        raise DeepSeekCostGateError("owner cost authorization is underfunded")
    if (
        type(pricing_record_id) is not str
        or pricing_record_id != DEEPSEEK_PRICING_RECORD.record_id
    ):
        raise DeepSeekCostGateError("pricing record reference is mismatched")
    return owner_cap_micro_usd, pricing_record_id


def _empty_runtime_holder() -> list[ModelRuntimePort]:
    return []


def _empty_close_state() -> list[bool]:
    return [False]


def _build_p2_coordinator(
    *,
    sample_id: str,
    attempt_id: str,
    owner_cap_micro_usd: int,
    pricing_record_id: str,
    runtime_builder: RuntimeBuilder | None = None,
    runtime_observer: P2RuntimeObserver | None = None,
) -> tuple[DeterministicPipelineCoordinator, list[ModelRuntimePort], list[bool]]:
    runtime_holder: list[ModelRuntimePort] = []
    close_state = _empty_close_state()

    def runtime_factory(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> ModelRuntimePort:
        builder = (
            _create_deepseek_runtime if runtime_builder is None else runtime_builder
        )
        runtime = builder(requests, payloads)
        observed = (
            runtime
            if runtime_observer is None
            else _ObservedRuntime(runtime, runtime_observer)
        )
        runtime_holder.append(observed)
        return observed

    admission = DeepSeekRuntimeAdmissionGate(
        runtime_factory=runtime_factory,
        owner_cap_micro_usd=owner_cap_micro_usd,
        pricing_record_id=pricing_record_id,
    )
    coordinator = DeterministicPipelineCoordinator(
        _SPEC_FACTORIES,
        runtime_factory=admission.runtime_factory,
        input_preflight=lambda input_text: _p2_input_preflight(
            sample_id=sample_id,
            attempt_id=attempt_id,
            input_text=input_text,
        ),
        pipeline_invocation=PipelineInvocation(
            sample_id=sample_id,
            attempt_id=attempt_id,
            context_assembly_version=_P2_CONTEXT_ASSEMBLY_VERSION,
        ),
        runtime_admission_gate=admission.authorize,
    )
    return coordinator, runtime_holder, close_state


def _close_all(*closables: object | None) -> None:
    first_error: BaseException | None = None
    for closable in closables:
        if closable is None:
            continue
        close = getattr(closable, "close", None)
        if not callable(close):
            continue
        try:
            close()
        except BaseException as error:
            if first_error is None:
                first_error = error
    if first_error is not None:
        raise first_error


def _close_runtime_once(
    runtime_holder: list[ModelRuntimePort], close_state: list[bool]
) -> None:
    if close_state[0]:
        return
    _close_all(*runtime_holder)
    close_state[0] = True


@dataclass(frozen=True, slots=True)
class PilotP2Composition:
    """Immutable lazy composition for exactly one P01/P2 attempt."""

    sample_id: str
    attempt_id: str
    input_text: str
    _coordinator: DeterministicPipelineCoordinator = field(repr=False, compare=False)
    _runtime_holder: list[ModelRuntimePort] = field(
        default_factory=_empty_runtime_holder, repr=False, compare=False
    )
    _closed: list[bool] = field(
        default_factory=_empty_close_state, repr=False, compare=False
    )
    observer: P2RuntimeObserver = field(
        default_factory=P2RuntimeObserver, repr=False, compare=False
    )

    def generate(self) -> PipelineResult:
        """Execute the one authorized P2 composition and close its runtime."""

        try:
            result = self._coordinator.generate(input_text=self.input_text)
        except BaseException:
            try:
                self._close_runtime_once()
            except BaseException:
                pass
            raise
        self._close_runtime_once()
        return result

    def _close_runtime_once(self) -> None:
        if self._closed[0]:
            return
        _close_runtime_once(self._runtime_holder, self._closed)


class PilotP2Coordinator(DeterministicPipelineCoordinator):
    """P2 coordinator adapter that owns and closes its lazy runtime."""

    def __init__(
        self,
        delegate: DeterministicPipelineCoordinator,
        runtime_holder: list[ModelRuntimePort],
        close_state: list[bool],
        observer: P2RuntimeObserver | None = None,
    ) -> None:
        self._delegate = delegate
        self._runtime_holder = runtime_holder
        self._close_state = close_state
        self.observer = observer if observer is not None else P2RuntimeObserver()

    def generate(self, *, input_text: str) -> PipelineResult:
        try:
            result = self._delegate.generate(input_text=input_text)
        except BaseException:
            try:
                _close_runtime_once(self._runtime_holder, self._close_state)
            except BaseException:
                pass
            raise
        _close_runtime_once(self._runtime_holder, self._close_state)
        return result

    def close(self) -> None:
        _close_runtime_once(self._runtime_holder, self._close_state)


@dataclass(frozen=True, slots=True)
class PilotP2PostgresComposition:
    """No-migration P2 composition over existing PostgreSQL/FastAPI seams."""

    application: Any
    task: TaskManagementPostgresComposition
    primary_input: PrimaryInputPostgresComposition
    result: DeterministicResultPostgresComposition
    coordinator: PilotP2Coordinator
    observer: P2RuntimeObserver = field(
        default_factory=P2RuntimeObserver, repr=False, compare=False
    )
    _closed: bool = field(default=False, init=False, repr=False, compare=False)

    def close(self) -> None:
        if self._closed:
            return
        object.__setattr__(self, "_closed", True)
        _close_all(self.coordinator, self.result, self.primary_input, self.task)


def compose_pilot_p2_pipeline(
    *,
    sample_id: str,
    attempt_id: str,
    input_text: str,
    owner_cap_micro_usd: int | None,
    pricing_record_id: str | None,
    runtime_builder: RuntimeBuilder | None = None,
    runtime_observer: P2RuntimeObserver | None = None,
) -> PilotP2Composition:
    """Construct one lazy P01/P2 DeepSeek composition without runtime I/O."""

    _validate_p2_input(
        sample_id=sample_id,
        attempt_id=attempt_id,
        input_text=input_text,
    )
    validated_owner_cap, validated_pricing_record = _validate_authorization(
        owner_cap_micro_usd=owner_cap_micro_usd,
        pricing_record_id=pricing_record_id,
    )
    observer = runtime_observer if runtime_observer is not None else P2RuntimeObserver()
    coordinator, runtime_holder, close_state = _build_p2_coordinator(
        sample_id=sample_id,
        attempt_id=attempt_id,
        owner_cap_micro_usd=validated_owner_cap,
        pricing_record_id=validated_pricing_record,
        runtime_builder=runtime_builder,
        runtime_observer=observer,
    )
    return PilotP2Composition(
        sample_id=sample_id,
        attempt_id=attempt_id,
        input_text=input_text,
        _coordinator=coordinator,
        _runtime_holder=runtime_holder,
        _closed=close_state,
        observer=observer,
    )


def compose_pilot_p2_postgres(
    postgres_config: PostgresEngineConfig,
    http_config: FixedWorkspaceHttpConfig,
    *,
    schema: str = "public",
    sample_id: str = _P2_SAMPLE_ID,
    attempt_id: str = _P2_ATTEMPT_ID,
    owner_cap_micro_usd: int | None = None,
    pricing_record_id: str | None = None,
    runtime_builder: RuntimeBuilder | None = None,
    runtime_observer: P2RuntimeObserver | None = None,
) -> PilotP2PostgresComposition:
    """Compose P2 Task/Input/Result/Export behind the existing HTTP app."""

    if type(postgres_config) is not PostgresEngineConfig:
        raise TypeError("postgres_config must be PostgresEngineConfig")
    if type(http_config) is not FixedWorkspaceHttpConfig:
        raise TypeError("http_config must be FixedWorkspaceHttpConfig")
    if sample_id != _P2_SAMPLE_ID or attempt_id != _P2_ATTEMPT_ID:
        raise ValueError("P2 composition requires the fixed P01 attempt identity")
    validated_owner_cap, validated_pricing_record = _validate_authorization(
        owner_cap_micro_usd=owner_cap_micro_usd,
        pricing_record_id=pricing_record_id,
    )
    observer = runtime_observer if runtime_observer is not None else P2RuntimeObserver()
    delegate, runtime_holder, close_state = _build_p2_coordinator(
        sample_id=sample_id,
        attempt_id=attempt_id,
        owner_cap_micro_usd=validated_owner_cap,
        pricing_record_id=validated_pricing_record,
        runtime_builder=runtime_builder,
        runtime_observer=observer,
    )
    coordinator = PilotP2Coordinator(
        delegate, runtime_holder, close_state, observer=observer
    )
    task: TaskManagementPostgresComposition | None = None
    primary_input: PrimaryInputPostgresComposition | None = None
    result: DeterministicResultPostgresComposition | None = None
    try:
        task = compose_task_management_postgres(postgres_config, schema=schema)
        primary_input = compose_primary_input_postgres(postgres_config, schema=schema)
        result = compose_deterministic_result_postgres(
            postgres_config,
            schema=schema,
            coordinator=coordinator,
        )
        application = create_task_http_application(
            config=http_config,
            task_application=task.application,
            primary_input_application=primary_input.application,
            result_application=result.application,
            pipeline_coordinator=coordinator,
            export_application=result.export_application,
        )
        return PilotP2PostgresComposition(
            application=application,
            task=task,
            primary_input=primary_input,
            result=result,
            coordinator=coordinator,
            observer=observer,
        )
    except BaseException:
        try:
            _close_all(coordinator, result, primary_input, task)
        except BaseException:
            pass
        raise
