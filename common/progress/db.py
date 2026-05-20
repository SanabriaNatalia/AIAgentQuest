import sqlite3
from pathlib import Path
from datetime import datetime
from common.progress.levels import calculate_level, get_xp_reward


DB_PATH = Path(".quest_progress.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def _column_exists(conn, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def _add_column_if_missing(conn, table: str, column: str, definition: str) -> None:
    if not _column_exists(conn, table, column):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


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

        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                payload TEXT NOT NULL,
                seen INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS quest_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quest_id TEXT NOT NULL,
                attempted_at TEXT NOT NULL,
                passed INTEGER NOT NULL,
                failure_reason TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS hint_usage (
                quest_id TEXT NOT NULL,
                hint_level INTEGER NOT NULL,
                requested_at TEXT NOT NULL,
                PRIMARY KEY (quest_id, hint_level)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS quest_reading (
                quest_id TEXT PRIMARY KEY,
                read_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS act_milestones (
                act_number INTEGER PRIMARY KEY,
                closed_at TEXT NOT NULL
            )
        """)

        _add_column_if_missing(conn, "apprentice", "created_at", "TEXT")
        _add_column_if_missing(conn, "apprentice", "avatar", "TEXT DEFAULT 'default'")
        _add_column_if_missing(conn, "quest_completion", "attempts", "INTEGER DEFAULT 1")
        _add_column_if_missing(conn, "quest_completion", "first_attempt_at", "TEXT")
        _add_column_if_missing(conn, "quest_completion", "total_time_seconds", "INTEGER")

def record_quest_completion(quest_id: str, difficulty : int, rank: str) -> None:

    init_db()

    completion_was_new = False
    xp_before = 0
    level_before = 1
    new_xp = 0
    new_level = 1
    xp_reward = 0

    with get_connection() as conn:
        apprentice = conn.execute(
            "SELECT id, xp, level FROM apprentice WHERE id = 1"
        ).fetchone()

        if apprentice is None:
            raise RuntimeError(
                "No se ha registrado el aprendiz. "
                "Corre primero: uv run python -m common.progress.init_user"
            )

        _, xp_before, level_before = apprentice

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
        new_xp = xp_before + xp_reward
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

        completion_was_new = True

    if completion_was_new:
        _notify_dashboard(
            quest_id=quest_id,
            difficulty=difficulty,
            rank=rank,
            xp_before=xp_before,
            xp_after=new_xp,
            xp_reward=xp_reward,
            level_before=level_before,
            level_after=new_level,
        )


def _notify_dashboard(
    *,
    quest_id: str,
    difficulty: int,
    rank: str,
    xp_before: int,
    xp_after: int,
    xp_reward: int,
    level_before: int,
    level_after: int,
) -> None:
    """Side-effects best-effort. Cualquier fallo aquí NO debe revertir el commit."""
    try:
        from common.dashboard.lifecycle import ensure_started
        from common.progress.notify import emit_event, open_celebration
    except Exception:
        return

    try:
        ensure_started()
    except Exception:
        pass

    try:
        emit_event(
            "quest-completed",
            {
                "quest_id": quest_id,
                "difficulty": difficulty,
                "rank": rank,
                "xp_before": xp_before,
                "xp_after": xp_after,
                "xp_reward": xp_reward,
                "level_before": level_before,
                "level_after": level_after,
            },
        )
    except Exception:
        pass

    try:
        open_celebration(quest_id)
    except Exception:
        pass