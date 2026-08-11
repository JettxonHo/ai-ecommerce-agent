"""Local JSON-line sink for validated runtime diagnostic events."""

from __future__ import annotations

import logging
from typing import TextIO

from ai_ecommerce_agent.application.runtime_diagnostics import (
    RuntimeDiagnosticEvent,
    RuntimeDiagnosticLevel,
    encode_runtime_diagnostic_event,
)

__all__ = ["RuntimeDiagnosticJsonLineSink"]


class RuntimeDiagnosticJsonLineSink:
    """Write one canonical encoded diagnostic event per stream line."""

    __slots__ = ("_logger", "_handler")

    def __init__(self, *, stream: TextIO) -> None:
        if not callable(getattr(stream, "write", None)):
            raise TypeError("stream must be a writable text stream")

        logger = logging.Logger("ai_ecommerce_agent.runtime_diagnostics")
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.propagate = False
        logger.addHandler(handler)
        self._logger = logger
        self._handler = handler

    def emit(self, event: RuntimeDiagnosticEvent) -> None:
        """Encode and write one validated event without retaining the event."""

        if type(event) is not RuntimeDiagnosticEvent:
            raise TypeError("event must be a RuntimeDiagnosticEvent")
        message = encode_runtime_diagnostic_event(event)
        self._logger.log(self._logging_level(event.level), message)

    @staticmethod
    def _logging_level(level: RuntimeDiagnosticLevel) -> int:
        if level is RuntimeDiagnosticLevel.INFO:
            return logging.INFO
        if level is RuntimeDiagnosticLevel.WARNING:
            return logging.WARNING
        if level is RuntimeDiagnosticLevel.ERROR:
            return logging.ERROR
        if level is RuntimeDiagnosticLevel.CRITICAL:
            return logging.CRITICAL
        raise TypeError("level must be a RuntimeDiagnosticLevel")
