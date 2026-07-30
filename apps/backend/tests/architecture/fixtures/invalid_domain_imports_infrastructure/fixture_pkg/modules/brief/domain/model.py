"""VIOLATION: domain imports same-module infrastructure (upward dependency)."""

from fixture_pkg.modules.brief.infrastructure.adapter import serialize

VALUE = serialize("domain-should-not-know-this")
