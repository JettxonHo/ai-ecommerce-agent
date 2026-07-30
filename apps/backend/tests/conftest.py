"""Shared pytest configuration for the backend test suite (FND-002).

Default network protection (RFC-001-DQ-09): every test is hermetic unless
it is explicitly marked ``live``. Socket creation is blocked at the socket
level via ``pytest-socket``, so undeclared network access in ``unit``,
``contract`` and ``architecture`` tests fails loudly instead of reaching
external services. Marker semantics are documented in
``apps/backend/README.md`` and ``tests/architecture/README.md``.
"""

# pyright: reportUnusedFunction=false
# Pytest fixtures are consumed by the framework via their decorator, not by
# direct calls; the unused-function diagnostic is a false positive for
# conftest entry points. This exception is file-scoped and precise.

from collections.abc import Iterator

import pytest
from pytest_socket import disable_socket, enable_socket


@pytest.fixture(autouse=True)
def _default_network_block(request: pytest.FixtureRequest) -> Iterator[None]:
    """Block socket-level network access unless the test is marked ``live``.

    ``live`` tests are the only opt-out and are excluded from every default
    local selection (``test-fast`` and ``test-all-local`` both filter them
    out). The guard is installed per test and removed afterwards so it can
    never leak into tooling that imports these modules.
    """
    if "live" in request.keywords:
        yield
        return
    disable_socket()
    try:
        yield
    finally:
        enable_socket()
