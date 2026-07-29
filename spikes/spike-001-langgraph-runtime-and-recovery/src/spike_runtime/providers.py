"""ScriptedModelProvider + MockRetrievalRuntime (DEC-035).

Deterministic, scripted model + mock retrieval. No real API key, no network,
no real user data. Produces fixed structured outputs so scenarios are
reproducible. The model never invents Explicit Facts — it returns scripted
candidates that the deterministic layer validates before any commit.
"""

from __future__ import annotations

from typing import Any


class ScriptedModelProvider:
    """Returns scripted, deterministic outputs per skill call."""

    def generate_facts(self, product_input: dict) -> dict:
        name = product_input.get("name", "unnamed-product")
        return {
            "facts": [
                {"key": "product_name", "value": name, "claim_type": "direct_fact", "fragment_id": "frag_1"},
                {"key": "category", "value": product_input.get("category", "unknown"), "claim_type": "direct_fact", "fragment_id": "frag_1"},
            ]
        }

    def generate_insights(self, facts_version: dict, reviews: list[dict]) -> dict:
        return {
            "themes": [{"theme": "usability", "coverage": "repeated_signal"}],
            "insights": [
                {"statement": "users value ease of use", "evidence": ["frag_r1", "frag_r2"], "coverage": "repeated_signal"}
            ],
        }

    def generate_positioning(self, facts_version: dict, insights_version: dict) -> dict:
        return {
            "candidates": [
                {
                    "candidate_id": "pos_1",
                    "value_proposition": "the easy default choice",
                    "target_segment": "beginners",
                    "differentiation": "lowest setup friction",
                    "proof_points": ["frag_1"],
                }
            ]
        }

    def generate_marketing_brief(self, approved_strategy: dict) -> dict:
        return {
            "core_message": approved_strategy.get("value_proposition", ""),
            "key_benefits": ["easy to start", "low friction"],
            "prohibited_claims": ["#1 guaranteed"],
        }


class MockRetrievalRuntime:
    """Mock retrieval: returns candidate fragments from an in-memory source set.

    Honors the DEC-032 boundary in miniature: results are CANDIDATE fragments
    (not formal evidence); a degraded mode returns zero results so callers must
    fall back without fabricating.
    """

    def __init__(self, fragments: dict[str, dict] | None = None, degraded: bool = False):
        self._fragments = fragments or {
            "frag_1": {"text": "product source fragment", "product_scope": "current_product"},
            "frag_r1": {"text": "review: very easy to set up", "product_scope": "current_product"},
            "frag_r2": {"text": "review: simple and intuitive", "product_scope": "current_product"},
        }
        self.degraded = degraded

    def retrieve(self, query: str, *, product_scope: str = "current_product") -> dict:
        if self.degraded:
            # Retrieval degraded: zero results, caller must NOT fabricate.
            return {"candidates": [], "coverage": "none", "degraded": True}
        cands = [
            {"fragment_id": fid, "text": f["text"], "score": 1.0}
            for fid, f in self._fragments.items()
            if f.get("product_scope") == product_scope
        ]
        return {"candidates": cands, "coverage": "dataset_supported" if cands else "none", "degraded": False}
