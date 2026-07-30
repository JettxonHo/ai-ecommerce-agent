"""Temporary FND-003 negative verification probe: architecture violation.

Domain imports the application layer — violates the Import Linter
"Module layer direction" contract (domain must never reach upward).
"""

from ai_ecommerce_agent.modules.verification_probe.application import service


def probe_leak() -> str:
    return service.probe_service()
