"""BusinessCommitService — the ONLY path that writes Business Current Truth.

Atomic Commit Contract (DEC-035 execution-brief): every formal business commit
happens in ONE transaction:

    Create Domain Version
    + Create Formal Evidence Links
    + Update Current Truth Pointer
    + Update Stage State
    + Write Business Audit Record
    + Write Idempotency Record

On ANY failure: whole-transaction rollback; pointer unchanged; stage not
advanced; no partial domain version; no partial evidence link; no false
success audit. Retry reuses the SAME logical idempotency key.

Graph nodes must NEVER bypass BusinessCommitService to write separately.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass

from . import ids


class BusinessCommitError(Exception):
    """Raised when a business commit must be rolled back."""


@dataclass(frozen=True)
class CommitResult:
    version_id: str
    idempotency_key: str
    committed: bool  # False if it was an idempotent replay (no new version)


class BusinessCommitService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # -- idempotency -------------------------------------------------------
    def _already_committed(self, idempotency_key: str) -> str | None:
        row = self.conn.execute(
            "SELECT ref_id FROM idempotency_record WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()
        return row["ref_id"] if row else None

    def _next_seq(self, table: str, column: str = "seq") -> int:
        row = self.conn.execute(f"SELECT COALESCE(MAX({column}), 0) + 1 AS n FROM {table}").fetchone()
        return int(row["n"])

    # -- atomic commit -----------------------------------------------------
    def commit_domain_version(
        self,
        *,
        domain: str,
        payload: dict,
        idempotency_key: str,
        stage_state: str | None = None,
        evidence_links: list[dict] | None = None,
        fail_after_version: bool = False,
    ) -> CommitResult:
        """Atomically create a domain version and advance the current-truth pointer.

        fail_after_version is a deterministic fault-injection hook used by
        scenarios to prove rollback (it raises AFTER the version insert but
        BEFORE the pointer update, inside the same transaction).
        """
        prior = self._already_committed(idempotency_key)
        if prior is not None:
            # Idempotent replay: no duplicate business version.
            return CommitResult(version_id=prior, idempotency_key=idempotency_key, committed=False)

        version_id = ids.version_id(domain)
        seq = self._next_seq("domain_version")
        try:
            with self.conn:  # BEGIN ... COMMIT / ROLLBACK on exception
                self.conn.execute(
                    "INSERT INTO domain_version(version_id, domain, payload_json, seq, status)"
                    " VALUES (?, ?, ?, ?, 'valid')",
                    (version_id, domain, json.dumps(payload, ensure_ascii=False), seq),
                )
                if fail_after_version:
                    raise BusinessCommitError("injected failure after version insert (rollback test)")

                # Supersede prior pointer target, then move the pointer.
                self.conn.execute(
                    "UPDATE domain_version SET status = 'superseded'"
                    " WHERE domain = ? AND status = 'valid' AND version_id != ?",
                    (domain, version_id),
                )
                self.conn.execute(
                    "INSERT INTO current_truth_pointer(domain, version_id) VALUES (?, ?)"
                    " ON CONFLICT(domain) DO UPDATE SET version_id = excluded.version_id",
                    (domain, version_id),
                )

                for link in evidence_links or []:
                    self.conn.execute(
                        "INSERT INTO business_audit(action, ref_id, detail_json, seq) VALUES (?, ?, ?, ?)",
                        (
                            "evidence_link",
                            version_id,
                            json.dumps(link, ensure_ascii=False),
                            self._next_seq("business_audit"),
                        ),
                    )

                if stage_state is not None:
                    self.conn.execute(
                        "INSERT INTO business_audit(action, ref_id, detail_json, seq) VALUES (?, ?, ?, ?)",
                        ("stage_state", version_id, json.dumps({"stage": stage_state}), self._next_seq("business_audit")),
                    )

                self.conn.execute(
                    "INSERT INTO business_audit(action, ref_id, detail_json, seq) VALUES (?, ?, ?, ?)",
                    ("commit", version_id, json.dumps({"domain": domain, "idempotency_key": idempotency_key}), self._next_seq("business_audit")),
                )
                self.conn.execute(
                    "INSERT INTO idempotency_record(idempotency_key, action, ref_id, seq) VALUES (?, ?, ?, ?)",
                    (idempotency_key, f"commit:{domain}", version_id, self._next_seq("idempotency_record")),
                )
        except sqlite3.Error as exc:  # pragma: no cover - defensive
            raise BusinessCommitError(str(exc)) from exc

        return CommitResult(version_id=version_id, idempotency_key=idempotency_key, committed=True)

    # -- read helpers --------------------------------------------------------
    def current_truth(self, domain: str) -> str | None:
        row = self.conn.execute(
            "SELECT version_id FROM current_truth_pointer WHERE domain = ?", (domain,)
        ).fetchone()
        return row["version_id"] if row else None

    def valid_version_count(self, domain: str) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) AS n FROM domain_version WHERE domain = ? AND status = 'valid'", (domain,)
        ).fetchone()
        return int(row["n"])

    def partial_write_count(self) -> int:
        """Count domain_versions that have no pointer AND no commit audit — partial writes.

        In a correct atomic implementation this is always 0.
        """
        row = self.conn.execute(
            "SELECT COUNT(*) AS n FROM domain_version dv"
            " WHERE NOT EXISTS (SELECT 1 FROM idempotency_record ir WHERE ir.ref_id = dv.version_id)"
        ).fetchone()
        return int(row["n"])
