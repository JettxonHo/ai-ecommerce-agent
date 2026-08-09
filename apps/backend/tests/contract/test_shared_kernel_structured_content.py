"""Public contract checks for the shared structured-content value."""

from __future__ import annotations

import ast
from collections.abc import Hashable
from pathlib import Path
from typing import Any, cast

import pytest

import ai_ecommerce_agent.shared_kernel as shared_kernel
import ai_ecommerce_agent.shared_kernel.content_origin as content_origin
import ai_ecommerce_agent.shared_kernel.structured_content as structured_content

pytestmark = pytest.mark.contract


def test_shared_kernel_adds_only_structured_content_to_its_public_exports() -> None:
    assert "StructuredContent" in shared_kernel.__all__
    assert shared_kernel.__all__.count("StructuredContent") == 1
    assert structured_content.__all__ == ["StructuredContent"]
    assert shared_kernel.StructuredContent is structured_content.StructuredContent


def test_shared_kernel_exposes_the_shared_content_origin_catalog() -> None:
    assert list(content_origin.ContentOrigin.__members__) == ["MODEL", "USER"]
    assert [member.value for member in content_origin.ContentOrigin] == [
        "model",
        "user",
    ]
    assert "ContentOrigin" in shared_kernel.__all__
    assert shared_kernel.__all__.count("ContentOrigin") == 1
    assert shared_kernel.ContentOrigin is content_origin.ContentOrigin
    assert content_origin.__all__ == ["ContentOrigin"]


def test_public_interface_has_the_exact_two_methods() -> None:
    assert hasattr(structured_content.StructuredContent, "from_mapping")
    assert hasattr(structured_content.StructuredContent, "to_mapping")
    assert not hasattr(structured_content.StructuredContent, "freeze")
    assert not hasattr(structured_content.StructuredContent, "as_dict")
    assert {
        name
        for name in dir(structured_content.StructuredContent)
        if not name.startswith("_")
    } == {"from_mapping", "to_mapping"}
    assert structured_content.StructuredContent.__slots__ == ("_value",)


@pytest.mark.parametrize(
    "args, kwargs",
    [
        ((), {}),
        (({"value": 1},), {}),
        ((), {"values": {"value": 1}}),
        ((), {"_value": ()}),
    ],
)
def test_structured_content_is_factory_only(
    args: tuple[object, ...], kwargs: dict[str, object]
) -> None:
    constructor = cast(Any, structured_content.StructuredContent)
    with pytest.raises(TypeError):
        constructor(*args, **kwargs)


def test_instances_are_opaque_non_hashable_and_immutable() -> None:
    content = structured_content.StructuredContent.from_mapping(
        {"secret": "private", "nested": {"value": 1}}
    )

    assert repr(content) == "StructuredContent(...)"
    assert "private" not in repr(content)
    assert "_value" not in repr(content)
    assert not isinstance(content, Hashable)
    with pytest.raises(TypeError):
        hash(content)
    with pytest.raises(TypeError):
        cast(Any, content)._value = ()
    with pytest.raises(TypeError):
        delattr(content, "_value")


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
