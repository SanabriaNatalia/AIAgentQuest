import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path(".quest_progress.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS apprentice (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                username TEXT NOT NULL,
                current_rank TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS quest_completion (
                quest_id TEXT PRIMARY KEY,
                completed_at TEXT NOT NULL
            )
        """)

def record_quest_completion(quest_id: str, rank: str) -> None:

    init_db()

    with get_connection() as conn:
        apprentice = conn.execute(
            "SELECT id FROM apprentice WHERE id = 1"
        ).fetchone()

        if apprentice is None:
            raise RuntimeError(
                "No apprentice registered. "
                "Run: uv run python -m common.progress.init_user"
            )

        conn.execute(
            """
            INSERT OR IGNORE INTO quest_completion (quest_id, completed_at)
            VALUES (?, ?)
            """,
            (quest_id, datetime.now().isoformat(timespec="seconds")),
        )

        conn.execute(
            """
            UPDATE apprentice
            SET current_rank = ?
            WHERE id = 1
            """,
            (rank,),
        )