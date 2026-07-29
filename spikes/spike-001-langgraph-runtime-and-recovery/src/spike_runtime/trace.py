"""Local JSONL Trace recorder (DEC-035 LocalTraceRecorder).

Deterministic, file-backed, append-only trace. Each line is one JSON event
carrying the runtime identifier chain (DEC-033) so traces, runtime events,
and business commits can be joined offline.

Trace files live under the scenario workspace (e.g. .spike-runs/<id>/trace.jsonl)
and are sanitized JSON evidence — never SQLite binaries, never secrets.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any


class LocalTraceRecorder:
    def __init__(self, trace_path: Path, trace_id: str):
        self.trace_path = Path(trace_path)
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        self.trace_id = trace_id
        self._seq = 0
        self._lock = threading.Lock()

    def record(self, event_type: str, **fields: Any) -> dict:
        """Append one trace event; returns the recorded event dict."""
        with self._lock:
            self._seq += 1
            event = {
                "seq": self._seq,
                "trace_id": self.trace_id,
                "event_type": event_type,
                **fields,
            }
            with self.trace_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, ensure_ascii=False) + "\n")
            return event

    def read_all(self) -> list[dict]:
        if not self.trace_path.exists():
            return []
        with self.trace_path.open("r", encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]
