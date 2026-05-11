import sqlite3
from pathlib import Path
from datetime import datetime
from common.progress.levels import calculate_level, get_xp_reward


DB_PATH = Path(".quest_progress.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS apprentice (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                username TEXT NOT NULL,
                current_rank TEXT NOT NULL,
                xp INTEGER NOT NULL DEFAULT 0,
                level INTEGER NOT NULL DEFAULT 1
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS quest_completion (
                quest_id TEXT PRIMARY KEY,
                difficulty INTEGER NOT NULL DEFAULT 1,
                completed_at TEXT NOT NULL
            )
        """)

def record_quest_completion(quest_id: str, difficulty : int, rank: str) -> None:

    init_db()

    with get_connection() as conn:
        apprentice = conn.execute(
            "SELECT id, xp FROM apprentice WHERE id = 1"
        ).fetchone()

        if apprentice is None:
            raise RuntimeError(
                "No se ha registrado el aprendiz. "
                "Corre primero: uv run python -m common.progress.init_user"
            )
        
        _, current_xp = apprentice

        existing_completion = conn.execute(
            """
            SELECT quest_id
            FROM quest_completion
            WHERE quest_id = ?
            """,
            (quest_id,),
        ).fetchone()

        if existing_completion is not None:
            return

        xp_reward = get_xp_reward(difficulty)
        new_xp = current_xp + xp_reward
        new_level = calculate_level(new_xp)

        conn.execute(
            """
            INSERT INTO quest_completion (quest_id, difficulty, completed_at)
            VALUES (?, ?, ?)
            """,
            (quest_id, difficulty, datetime.now().isoformat(timespec="seconds")),
        )

        conn.execute(
            """
            UPDATE apprentice
            SET current_rank = ?,
                xp = ?,
                level = ?
            WHERE id = 1
            """,
            (
                rank, 
                new_xp, 
                new_level
            ),
        )