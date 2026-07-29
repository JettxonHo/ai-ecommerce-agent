"""Review Submit — a SEPARATE business transaction (DEC-029 in miniature).

    Review Submit Request
    -> Review Package Validation (current & not stale)
    -> Approved Strategy Commit (atomic, idempotent)
    -> Current Truth Update
    -> Audit Record

Hard rules honored:
  * No stale Review Package submission (the package must still be current).
  * Duplicate submit is idempotent — no duplicate Approved Strategy Version.
"""

from __future__ import annotations

import json
import sqlite3

from . import ids
from .commit import BusinessCommitError, BusinessCommitService


class StaleReviewError(Exception):
    """Raised when a review package is no longer current / already superseded."""


class ReviewService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.commit = BusinessCommitService(conn)

    def _package_current(self, review_id: str) -> bool:
        cur = self.commit.current_truth("review_package")
        return cur == review_id

    def submit(
        self,
        *,
        task_id: str,
        review_id: str,
        chosen_candidate: dict,
        idempotency_key: str,
    ) -> dict:
        """Submit a human review decision. Returns the Approved Strategy reference.

        Idempotent: the same idempotency_key replays without creating a second
        Approved Strategy Version.
        """
        # Idempotency first (duplicate submit).
        existing = self.commit._already_committed(idempotency_key)  # noqa: SLF001 (spike-local reuse)
        if existing is not None:
            return {"approved_strategy_version_id": existing, "committed": False, "stale": False}

        # Stale Review guard.
        if not self._package_current(review_id):
            raise StaleReviewError(f"review package {review_id} is stale or not current")

        res = self.commit.commit_domain_version(
            domain="approved_strategy",
            payload={
                "review_id": review_id,
                "value_proposition": chosen_candidate.get("value_proposition", ""),
                "target_segment": chosen_candidate.get("target_segment", ""),
                "differentiation": chosen_candidate.get("differentiation", ""),
                "proof_points": chosen_candidate.get("proof_points", []),
            },
            idempotency_key=idempotency_key,
            stage_state="strategy_approved",
        )

        # Mark the review package as submitted (superseded as a pending package).
        with self.conn:
            self.conn.execute(
                "UPDATE domain_version SET status = 'superseded' WHERE version_id = ? AND domain = 'review_package'",
                (review_id,),
            )
            self.conn.execute(
                "INSERT INTO business_audit(action, ref_id, detail_json, seq)"
                " VALUES ('review_submit', ?, ?, (SELECT COALESCE(MAX(seq),0)+1 FROM business_audit))",
                (res.version_id, json.dumps({"review_id": review_id})),
            )

        return {"approved_strategy_version_id": res.version_id, "committed": True, "stale": False}
