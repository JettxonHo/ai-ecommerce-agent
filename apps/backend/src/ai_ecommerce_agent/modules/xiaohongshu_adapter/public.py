"""Narrow Xiaohongshu Brief public facade.

Only immutable, framework-neutral version projections cross the module
boundary. Mapping, revision, comparison, persistence, and rendering remain
private to later Xiaohongshu adapter slices.
"""

from .domain.contracts import (
    XiaohongshuBriefSemanticGroup,
    XiaohongshuBriefSemanticGroupName,
    XiaohongshuBriefVersionSnapshot,
)

__all__ = [
    "XiaohongshuBriefSemanticGroupName",
    "XiaohongshuBriefSemanticGroup",
    "XiaohongshuBriefVersionSnapshot",
]
