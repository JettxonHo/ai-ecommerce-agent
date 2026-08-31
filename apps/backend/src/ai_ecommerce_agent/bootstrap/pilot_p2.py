"""Lazy, P01-only P2 composition bound to the DeepSeek runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest,
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
    "PilotP2Composition",
    "PilotP2PostgresComposition",
    "PilotP2Coordinator",
    "compose_pilot_p2_pipeline",
    "compose_pilot_p2_postgres",
]

_P2_SAMPLE_ID: Final[str] = "P01"
_P2_ATTEMPT_ID: Final[str] = "P2-P01-A1"
_P2_CONTEXT_ASSEMBLY_VERSION: Final[str] = "pilot-p2-v1"
_P2_INPUT_ID_MARKERS: Final[tuple[str, ...]] = (
    "sample_id: P01",
    "attempt_id: P2-P01-A1",
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
    lines = frozenset(line.strip() for line in input_text.splitlines())
    if any(marker not in lines for marker in _P2_INPUT_ID_MARKERS):
        raise ValueError("P2 input identity markers are invalid")


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
) -> tuple[DeterministicPipelineCoordinator, list[ModelRuntimePort], list[bool]]:
    runtime_holder: list[ModelRuntimePort] = []
    close_state = _empty_close_state()

    def runtime_factory(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> ModelRuntimePort:
        runtime = _create_deepseek_runtime(requests, payloads)
        runtime_holder.append(runtime)
        return runtime

    admission = DeepSeekRuntimeAdmissionGate(
        runtime_factory=runtime_factory,
        owner_cap_micro_usd=owner_cap_micro_usd,
        pricing_record_id=pricing_record_id,
    )
    coordinator = DeterministicPipelineCoordinator(
        _SPEC_FACTORIES,
        runtime_factory=admission.runtime_factory,
        input_preflight=lambda _input_text: (),
        pipeline_invocation=PipelineInvocation(
            sample_id=sample_id,
            attempt_id=attempt_id,
            context_assembly_version=_P2_CONTEXT_ASSEMBLY_VERSION,
        ),
        runtime_admission_gate=admission.authorize,
    )
    return coordinator, runtime_holder, close_state


def _close_runtime_once(
    runtime_holder: list[ModelRuntimePort], close_state: list[bool]
) -> None:
    if close_state[0]:
        return
    close_state[0] = True
    for runtime in runtime_holder:
        close = getattr(runtime, "close", None)
        if callable(close):
            close()


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

    def generate(self) -> PipelineResult:
        """Execute the one authorized P2 composition and close its runtime."""

        try:
            return self._coordinator.generate(input_text=self.input_text)
        finally:
            self._close_runtime_once()

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
    ) -> None:
        self._delegate = delegate
        self._runtime_holder = runtime_holder
        self._close_state = close_state

    def generate(self, *, input_text: str) -> PipelineResult:
        try:
            return self._delegate.generate(input_text=input_text)
        finally:
            _close_runtime_once(self._runtime_holder, self._close_state)

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
    _closed: bool = field(default=False, init=False, repr=False, compare=False)

    def close(self) -> None:
        if self._closed:
            return
        object.__setattr__(self, "_closed", True)
        first_error: BaseException | None = None
        self.coordinator.close()
        for participant in (self.result, self.primary_input, self.task):
            try:
                participant.close()
            except BaseException as error:
                if first_error is None:
                    first_error = error
        if first_error is not None:
            raise first_error


def compose_pilot_p2_pipeline(
    *,
    sample_id: str,
    attempt_id: str,
    input_text: str,
    owner_cap_micro_usd: int | None,
    pricing_record_id: str | None,
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
    coordinator, runtime_holder, close_state = _build_p2_coordinator(
        sample_id=sample_id,
        attempt_id=attempt_id,
        owner_cap_micro_usd=validated_owner_cap,
        pricing_record_id=validated_pricing_record,
    )
    return PilotP2Composition(
        sample_id=sample_id,
        attempt_id=attempt_id,
        input_text=input_text,
        _coordinator=coordinator,
        _runtime_holder=runtime_holder,
        _closed=close_state,
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
    delegate, runtime_holder, close_state = _build_p2_coordinator(
        sample_id=sample_id,
        attempt_id=attempt_id,
        owner_cap_micro_usd=validated_owner_cap,
        pricing_record_id=validated_pricing_record,
    )
    coordinator = PilotP2Coordinator(delegate, runtime_holder, close_state)
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
        )
    except BaseException:
        coordinator.close()
        for participant in (result, primary_input, task):
            if participant is not None:
                participant.close()
        raise
