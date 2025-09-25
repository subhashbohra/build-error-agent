import os
import sqlite3
from typing import Dict, Any


DB_PATH = os.environ.get("SLM_DB_PATH", "slm_data.sqlite")


def init_db(path: str = DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT,
            pr_number INTEGER,
            logs TEXT,
            suggestion TEXT,
            outcome TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def store_incident(repo: str, pr_number: int, logs: str, suggestion: str, outcome: str | None = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO incidents (repo, pr_number, logs, suggestion, outcome) VALUES (?, ?, ?, ?, ?)",
        (repo, pr_number, logs, suggestion, outcome or ""),
    )
    conn.commit()
    conn.close()


def sample_incidents(limit: int = 100):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, repo, pr_number, logs, suggestion, outcome FROM incidents ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


def retrain_with_gemma(incidents: list[Dict[str, Any]]):
    """Stub: call Vertex AI to retrain or generate new prompt templates based on incidents.

    Real implementation: export incidents, create a dataset in Vertex AI, and run a fine-tune or a prompt engineering job.
    """
    # Placeholder - actual training requires Vertex AI APIs and dataset creation
    print(f"Retrainer invoked on {len(incidents)} incidents")
    return {"status": "queued", "count": len(incidents)}
