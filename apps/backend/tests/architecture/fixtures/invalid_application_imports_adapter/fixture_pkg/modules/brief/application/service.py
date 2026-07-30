"""VIOLATION: application imports a concrete infrastructure implementation."""

from fixture_pkg.modules.brief.infrastructure.adapter import serialize

RESULT = serialize("application-should-define-a-port-instead")
