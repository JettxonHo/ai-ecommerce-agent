"""In-memory test-only Business Current Truth probe.

The probe deliberately has no relationship to LangGraph's checkpoint store.
It lets tests assert that stale/foreign/incompatible requests leave business
truth untouched without creating production tables or models in this slice.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class BusinessTruthProbe:
    current_result: str | None = None
    commit_keys: list[str] = field(default_factory=list[str])

    def snapshot(self) -> tuple[str | None, tuple[str, ...]]:
        return self.current_result, tuple(self.commit_keys)

    def commit(self, *, idempotency_key: str, result: str) -> None:
        if idempotency_key in self.commit_keys:
            return
        self.commit_keys.append(idempotency_key)
        self.current_result = result
