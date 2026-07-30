"""VIOLATION: public facade exposes ORM, workflow and technical types.

The technical imports are deliberately unresolvable: leakage detection is
pure AST analysis and must not require the technologies to be installed
(FND-002 installs no ORM and no LangGraph).
"""

from dataclasses import dataclass

from langgraph.graph import StateGraph
from sqlalchemy.orm import DeclarativeBase, Session


@dataclass(frozen=True)
class BriefView:
    """A legitimate technology-neutral view (kept to show contrast)."""

    title: str


class BriefRecord(DeclarativeBase):
    """Simulated ORM model leaking through the public contract."""


def submit(session: Session, graph: StateGraph) -> BriefView:
    """Technical parameter types leaking into the public signature."""
    raise NotImplementedError
