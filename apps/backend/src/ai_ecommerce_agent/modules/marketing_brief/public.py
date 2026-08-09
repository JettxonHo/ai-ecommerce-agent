"""Narrow Marketing Brief public facade.

Only immutable, framework-neutral version projections cross the module
boundary. Generation, revision, comparison, persistence, and rendering
remain private to later Marketing Brief slices.
"""

from .domain.contracts import (
    MarketingBriefSemanticGroup,
    MarketingBriefSemanticGroupName,
    MarketingBriefVersionSnapshot,
)

__all__ = [
    "MarketingBriefSemanticGroupName",
    "MarketingBriefSemanticGroup",
    "MarketingBriefVersionSnapshot",
]
