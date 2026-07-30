"""VIOLATION: orchestration reaches into a module's infrastructure layer."""

from fixture_pkg.modules.brief.infrastructure.adapter import build_connection

CONNECTION = build_connection()
