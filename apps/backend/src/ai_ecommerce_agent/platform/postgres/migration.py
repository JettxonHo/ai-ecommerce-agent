"""Pure schema-scope helpers shared by the Business migration environment."""

from __future__ import annotations


def business_schema_scope(business_schema: str) -> frozenset[str | None]:
    """Return the only schemas a Business autogenerate may inspect.

    PostgreSQL's default schema is represented as ``None`` by some SQLAlchemy
    reflection paths.  It is equivalent to ``public`` only when ``public`` is
    the explicit Business target; an isolated non-public test schema must not
    accidentally inspect the default schema.
    """

    if business_schema == "public":
        return frozenset({None, "public"})
    return frozenset({business_schema})


__all__ = ["business_schema_scope"]
