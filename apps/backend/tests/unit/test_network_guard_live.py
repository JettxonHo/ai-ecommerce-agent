"""Live-marker exemption proof for the default network guard (FND-002).

This test is excluded from every default selection: ``test-fast`` runs
``-m "not live and not slow"`` and ``test-all-local`` runs ``-m "not live"``.
It executes only under an explicit ``pytest -m live``.

It creates a socket without ever connecting, so even this explicit ``live``
run performs no network I/O; it only proves that the ``live`` marker exempts
a test from the default guard (i.e. ``live`` tests must be deliberately
chosen, never run by accident).
"""

import socket

import pytest

pytestmark = pytest.mark.live


def test_live_marker_exempts_socket_guard() -> None:
    """A live-marked test may create a socket (here without connecting)."""
    sock = socket.socket()
    sock.close()
