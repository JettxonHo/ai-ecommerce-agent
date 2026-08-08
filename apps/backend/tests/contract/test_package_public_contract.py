"""Public contract tests for the ``ai_ecommerce_agent`` package surface.

Marker: ``contract``. These tests pin the package's public API so future
growth cannot silently widen or rename the facade. Today the package exposes
exactly ``__version__`` (FND-001); when real public contracts land they must
be added here deliberately, with their own contract tests.
"""

import re
import types

import pytest

import ai_ecommerce_agent

pytestmark = pytest.mark.contract

_SEMVER_PATTERN = re.compile(r"\d+\.\d+\.\d+")


def test_public_api_is_exactly_version() -> None:
    """The declared public surface is exactly ``__version__``."""
    assert ai_ecommerce_agent.__all__ == ["__version__"]


def test_version_is_semver_shaped() -> None:
    """The exposed version follows the major.minor.patch shape."""
    assert _SEMVER_PATTERN.fullmatch(ai_ecommerce_agent.__version__)


def test_no_undeclared_public_names() -> None:
    """No public name may exist outside the declared ``__all__``."""
    declared = set(ai_ecommerce_agent.__all__)
    # Importing ``ai_ecommerce_agent.shared_kernel`` records the submodule on
    # the parent package automatically.  That importability detail is not a
    # root-facade export; other undeclared public values remain forbidden.
    public = {
        name
        for name in dir(ai_ecommerce_agent)
        if not name.startswith("_")
        and not isinstance(getattr(ai_ecommerce_agent, name), types.ModuleType)
    }
    assert public <= declared
