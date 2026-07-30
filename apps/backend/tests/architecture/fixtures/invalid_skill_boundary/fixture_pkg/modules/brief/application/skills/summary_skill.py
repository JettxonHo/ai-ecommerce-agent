"""VIOLATION: skill breaks the skill boundary in several ways at once.

Illegal: imports the workflow runtime, imports a repository implementation,
imports spike code, reads the environment, and accepts a database Session.
All technical imports are deliberately unresolvable (detection is static).
"""

import os

from langgraph.graph import StateGraph
from spikes.prototype import helper
from sqlalchemy.orm import Session

from fixture_pkg.modules.brief.infrastructure.repository import BriefRepository


def run_skill(session: Session, repo: BriefRepository) -> str:
    """Every aspect of this signature and body violates RFC-001-DQ-05."""
    graph_name = StateGraph.__name__
    helper_name = helper.__name__
    key = os.getenv("SKILL_KEY", "default")
    return f"{graph_name}:{repo.fetch()}:{helper_name}:{key}:{session}"
