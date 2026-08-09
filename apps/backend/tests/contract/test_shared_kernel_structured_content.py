"""Public contract checks for the shared structured-content value."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import ai_ecommerce_agent.shared_kernel as shared_kernel
import ai_ecommerce_agent.shared_kernel.structured_content as structured_content

pytestmark = pytest.mark.contract


def test_shared_kernel_adds_only_structured_content_to_its_public_exports() -> None:
    assert "StructuredContent" in shared_kernel.__all__
    assert shared_kernel.__all__.count("StructuredContent") == 1
    assert structured_content.__all__ == ["StructuredContent"]
    assert shared_kernel.StructuredContent is structured_content.StructuredContent


def test_public_interface_has_the_exact_two_methods() -> None:
    assert hasattr(structured_content.StructuredContent, "from_mapping")
    assert hasattr(structured_content.StructuredContent, "to_mapping")
    assert not hasattr(structured_content.StructuredContent, "freeze")
    assert not hasattr(structured_content.StructuredContent, "as_dict")


def test_structured_content_module_uses_only_stdlib_imports() -> None:
    module_path = Path(structured_content.__file__ or "")
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_roots.add(node.module.split(".", 1)[0])

    assert imported_roots <= {
        "__future__",
        "collections",
        "dataclasses",
        "math",
        "typing",
    }


def test_structured_content_has_no_import_time_file_or_socket_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import builtins
    import importlib
    import socket
    import sys

    original_open = builtins.open
    original_socket = socket.socket
    module = sys.modules.pop(structured_content.__name__, None)

    def guarded_open(*args: object, **kwargs: object) -> object:
        raise AssertionError("structured_content attempted file I/O at import time")

    def guarded_socket(*args: object, **kwargs: object) -> object:
        raise AssertionError("structured_content attempted socket I/O at import time")

    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(socket, "socket", guarded_socket)
    try:
        importlib.import_module(structured_content.__name__)
    finally:
        monkeypatch.setattr(builtins, "open", original_open)
        monkeypatch.setattr(socket, "socket", original_socket)
        if module is not None:
            sys.modules[structured_content.__name__] = module
