"""Default network blocking guarantees (RFC-001-DQ-09, FND-002).

These tests are permanent regression tests for the socket-level guard
installed in ``tests/conftest.py``. They prove that any undeclared network
access in a non-``live`` test fails immediately with ``SocketBlockedError``.

No real external service is contacted: the guard raises before any
connection can be attempted.
"""

import socket

import pytest
from pytest_socket import SocketBlockedError

pytestmark = pytest.mark.unit


def test_socket_creation_is_blocked_in_non_live_tests() -> None:
    """Creating a socket in a default (non-live) test must fail."""
    with pytest.raises(SocketBlockedError):
        socket.socket()


def test_socket_connect_is_blocked_in_non_live_tests() -> None:
    """Connection helpers must fail before reaching the network."""
    with pytest.raises(SocketBlockedError):
        # Numeric address: no DNS lookup happens before the guard fires.
        socket.create_connection(("127.0.0.1", 1))
