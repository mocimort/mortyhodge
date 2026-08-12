"""SQLite knowledge store with FTS5 full-text search.

One file (data/knowledge.db), zero servers. Embedding-based search can be
layered on later (sqlite-vec) without touching the pipeline.
"""
from __future__ import annotations

import json
import sqlite3
from typing import Any

from .config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS knowledge (
    id INTEGER PRIMARY KEY,
    source_job_id INTEGER UNIQUE,
    completed_on TEXT,
    symptom TEXT,
    root_cause TEXT,
    fix TEXT,
    equipment TEXT,
    parts_used TEXT,      -- JSON array
    industry TEXT,
    tags TEXT,            -- JSON array
    confidence TEXT,
    quality_note TEXT
);
CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
    symptom, root_cause, fix, equipment, tags,
    content='knowledge', content_rowid='id'
);
CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge BEGIN
    INSERT INTO knowledge_fts(rowid, symptom, root_cause, fix, equipment, tags)
    VALUES (new.id, new.symptom, new.root_cause, new.fix, new.equipment, new.tags);
END;
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path)
    conn.executescript(SCHEMA)
    conn.row_factory = sqlite3.Row
    return conn


def upsert(conn: sqlite3.Connection, k: dict[str, Any]) -> None:
    conn.execute(
        """INSERT INTO knowledge
           (source_job_id, completed_on, symptom, root_cause, fix, equipment,
            parts_used, industry, tags, confidence, quality_note)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(source_job_id) DO NOTHING""",
        (
            k.get("source_job_id"), k.get("completed_on"), k.get("symptom"),
            k.get("root_cause"), k.get("fix"), k.get("equipment"),
            json.dumps(k.get("parts_used", [])), k.get("industry"),
            json.dumps(k.get("tags", [])), k.get("confidence"),
            k.get("quality_note"),
        ),
    )
    conn.commit()


def search(conn: sqlite3.Connection, query: str, limit: int = 10) -> list[dict[str, Any]]:
    rows = conn.execute(
        """SELECT k.* FROM knowledge_fts f
           JOIN knowledge k ON k.id = f.rowid
           WHERE knowledge_fts MATCH ? ORDER BY rank LIMIT ?""",
        (query, limit),
    ).fetchall()
    return [dict(r) for r in rows]
