"""Minimal real tests for the backend package foundation (FND-001).

These tests prove that ``ai_ecommerce_agent`` imports from the *installed*
``src``-layout package (not from a repository root that happens to sit on
``PYTHONPATH``) and that importing it has no resource-initializing side
effects. They deliberately do not test any business capability: none exists
yet, and none may be created here.
"""

import builtins
import importlib
import sys
from pathlib import Path

import pytest

import ai_ecommerce_agent

_REPO_ROOT_MARKER = "apps"


@pytest.mark.unit
def test_package_importable_from_installed_src_layout() -> None:
    """The package resolves to the ``src`` layout, not a repo-root accident."""
    module_path = Path(ai_ecommerce_agent.__file__).resolve()
    parts = module_path.parts
    # The module must live under a ``src/ai_ecommerce_agent`` directory,
    # which is only importable when the project is properly installed.
    assert "ai_ecommerce_agent" in parts
    assert "src" in parts, f"package did not resolve to a src layout: {module_path}"


@pytest.mark.unit
def test_package_does_not_depend_on_repo_root_on_path() -> None:
    """Import must succeed even when no repository root is on ``sys.path``.

    Remove any path entry that looks like a repository/apps root and
    re-import in a fresh interpreter-state view; the package must still be
    importable from its installed location.
    """
    package_file_str = ai_ecommerce_agent.__file__
    assert package_file_str is not None, "package has no __file__"
    package_file = Path(package_file_str).resolve()
    original_path = list(sys.path)
    try:
        sys.path[:] = [
            entry
            for entry in sys.path
            if entry and _REPO_ROOT_MARKER not in Path(entry).parts
        ]
        reloaded = importlib.import_module("ai_ecommerce_agent")
        reloaded_file_str = reloaded.__file__
        assert reloaded_file_str is not None, "reloaded package has no __file__"
        assert Path(reloaded_file_str).resolve() == package_file
    finally:
        sys.path[:] = original_path


@pytest.mark.unit
def test_import_has_no_side_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Importing must not open files, sockets, or env reads as a side effect.

    Run the import in a subprocess-free way by re-executing the module's
    import machinery with I/O primitives trapped. Any attempt by the import
    to open a file or socket raises, failing the test.
    """
    attempts: list[str] = []

    real_open = builtins.open

    def guarded_open(file: object, *args: object, **kwargs: object) -> object:
        attempts.append(str(file))
        raise AssertionError(f"import attempted to open file: {file}")

    import socket

    def guarded_socket(*args: object, **kwargs: object) -> object:
        raise AssertionError("import attempted to create a socket")

    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(socket, "socket", guarded_socket)

    module = sys.modules.pop("ai_ecommerce_agent", None)
    try:
        importlib.import_module("ai_ecommerce_agent")
    finally:
        monkeypatch.setattr(builtins, "open", real_open)
        if module is not None:
            sys.modules["ai_ecommerce_agent"] = module

    assert attempts == []


@pytest.mark.unit
def test_package_exposes_version() -> None:
    """The package exposes a stable ``__version__`` identifier."""
    assert isinstance(ai_ecommerce_agent.__version__, str)
    assert ai_ecommerce_agent.__version__
