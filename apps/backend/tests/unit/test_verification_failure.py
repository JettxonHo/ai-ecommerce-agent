"""Temporary FND-003 negative verification probe: intentional unit failure."""

import pytest


@pytest.mark.unit
def test_verification_probe_fails() -> None:
    assert False, "FND-003 negative verification: intentional unit failure (temporary probe)"
