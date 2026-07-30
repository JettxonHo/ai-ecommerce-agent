"""VIOLATION: production-style code imports throwaway spike code.

The ``spikes`` package is deliberately NOT provided in this fixture: the
check must catch the illegal import even when the target is unresolvable
(matching production reality, where spikes/ is never importable).
"""

import spikes.prototype_client


def run() -> str:
    """Use the spike import so static analysis sees a live reference."""
    return spikes.prototype_client.invoke()
