"""Three physically-separated SQLite stores (DEC-035 execution-brief).

    business.sqlite    -> Business Current Truth (single authoritative source)
    runtime.sqlite     -> Workflow/skill/node execution records, runtime events
    checkpoints.sqlite -> LangGraph SqliteSaver graph checkpoints

Business State != Runtime State != Checkpoint State. The checkpoint store
must never overwrite or substitute for Business Current Truth.

These SQLite stores are Spike-experiment storage ONLY — they are NOT a
production database design.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

BUSINESS_DB = "business.sqlite"
RUNTIME_DB = "runtime.sqlite"
CHECKPOINTS_DB = "checkpoints.sqlite"


@dataclass(frozen=True)
class StorePaths:
    """Filesystem locations of the three separated stores for one workspace."""

    workspace: Path

    @property
    def business(self) -> Path:
        return self.workspace / BUSINESS_DB

    @property
    def runtime(self) -> Path:
        return self.workspace / RUNTIME_DB

    @property
    def checkpoints(self) -> Path:
        return self.workspace / CHECKPOINTS_DB


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


# ---------------------------------------------------------------------------
# Business store: the ONLY authoritative source of Business Current Truth.
# ---------------------------------------------------------------------------
_BUSINESS_SCHEMA = """
CREATE TABLE IF NOT EXISTS task (
    task_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    current_stage TEXT NOT NULL,
    created_seq INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS domain_version (
    version_id TEXT PRIMARY KEY,
    domain TEXT NOT NULL,           -- facts | insights | positioning | approved_strategy | marketing_brief | review_package
    payload_json TEXT NOT NULL,
    seq INTEGER NOT NULL,
    status TEXT NOT NULL            -- valid | superseded | invalid
);

CREATE TABLE IF NOT EXISTS current_truth_pointer (
    domain TEXT PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES domain_version(version_id)
);

CREATE TABLE IF NOT EXISTS review_package (
    review_id TEXT PRIMARY KEY,
    payload_json TEXT NOT NULL,
    facts_version_id TEXT NOT NULL,
    insights_version_id TEXT NOT NULL,
    positioning_version_id TEXT NOT NULL,
    status TEXT NOT NULL,           -- pending | submitted | superseded | stale
    seq INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS business_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    ref_id TEXT NOT NULL,
    detail_json TEXT NOT NULL,
    seq INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS idempotency_record (
    idempotency_key TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    ref_id TEXT NOT NULL,
    seq INTEGER NOT NULL
);
"""

# ---------------------------------------------------------------------------
# Runtime store: execution records. Never holds Business Current Truth.
# ---------------------------------------------------------------------------
_RUNTIME_SCHEMA = """
CREATE TABLE IF NOT EXISTS workflow_run (
    workflow_run_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    status TEXT NOT NULL,           -- running | interrupted | completed | failed | cancelled
    started_seq INTEGER NOT NULL,
    ended_seq INTEGER
);

CREATE TABLE IF NOT EXISTS node_execution (
    node_execution_id TEXT PRIMARY KEY,
    workflow_run_id TEXT NOT NULL,
    node_name TEXT NOT NULL,
    status TEXT NOT NULL,           -- started | succeeded | failed | retried
    attempt INTEGER NOT NULL,
    seq INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS runtime_error (
    error_id TEXT PRIMARY KEY,
    node_execution_id TEXT,
    category TEXT NOT NULL,         -- transient | invalid_output | budget_exhausted | cancelled | stale | unknown
    message TEXT NOT NULL,
    seq INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS recovery_case (
    recovery_case_id TEXT PRIMARY KEY,
    workflow_run_id TEXT,
    reason TEXT NOT NULL,
    action TEXT NOT NULL,
    seq INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS runtime_event (
    event_seq INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,
    workflow_run_id TEXT,
    node_execution_id TEXT,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
"""


def init_business_store(workspace: Path) -> sqlite3.Connection:
    conn = connect(StorePaths(workspace).business)
    conn.executescript(_BUSINESS_SCHEMA)
    conn.commit()
    return conn


def init_runtime_store(workspace: Path) -> sqlite3.Connection:
    conn = connect(StorePaths(workspace).runtime)
    conn.executescript(_RUNTIME_SCHEMA)
    conn.commit()
    return conn


def init_all(workspace: Path) -> StorePaths:
    """Create the workspace and initialize business + runtime stores.

    The checkpoint store is created by LangGraph's SqliteSaver itself
    (S0 wires it in graph.py); we only guarantee the directory exists.
    """
    workspace = Path(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    init_business_store(workspace).close()
    init_runtime_store(workspace).close()
    return StorePaths(workspace)
