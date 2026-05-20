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

        # F13: buffer pre-completion. quest_completion sigue siendo "quest
        # cerrado"; aquí trackeamos first_attempt_at + attempts running counter
        # mientras el quest está en progreso.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quest_progress (
                quest_id TEXT PRIMARY KEY,
                first_attempt_at TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0
            )
        """)

        _add_column_if_missing(conn, "apprentice", "created_at", "TEXT")
        _add_column_if_missing(conn, "apprentice", "avatar", "TEXT DEFAULT 'default'")
        _add_column_if_missing(conn, "quest_completion", "attempts", "INTEGER DEFAULT 1")
        _add_column_if_missing(conn, "quest_completion", "first_attempt_at", "TEXT")
        _add_column_if_missing(conn, "quest_completion", "total_time_seconds", "INTEGER")


def register_first_attempt(quest_id: str) -> None:
    """Marca el primer touch del aprendiz en un quest. Idempotente.

    Se llama desde `arkanum start` y `arkanum check`. Si el quest ya está
    completado, no hace nada. Si quest_progress ya tiene la entrada, tampoco.
    """
    init_db()
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        done = conn.execute(
            "SELECT 1 FROM quest_completion WHERE quest_id = ?", (quest_id,)
        ).fetchone()
        if done is not None:
            return
        conn.execute(
            "INSERT OR IGNORE INTO quest_progress (quest_id, first_attempt_at, attempts) "
            "VALUES (?, ?, 0)",
            (quest_id, now),
        )


def record_quest_attempt(
    quest_id: str,
    passed: bool,
    failure_reason: str | None = None,
) -> None:
    """Registra un intento de validación de check.py.

    Siempre inserta en quest_attempts (histórico completo). El contador
    `attempts` de quest_progress sólo se incrementa si el quest todavía
    no está completado — los intentos posteriores a la completación se
    guardan en el histórico pero no inflan el contador.
    """
    init_db()
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO quest_attempts (quest_id, attempted_at, passed, failure_reason) "
            "VALUES (?, ?, ?, ?)",
            (quest_id, now, 1 if passed else 0, failure_reason),
        )
        done = conn.execute(
            "SELECT 1 FROM quest_completion WHERE quest_id = ?", (quest_id,)
        ).fetchone()
        if done is not None:
            return
        # Asegura row de quest_progress por si arkanum check se invoca sin
        # un arkanum start previo.
        conn.execute(
            "INSERT OR IGNORE INTO quest_progress (quest_id, first_attempt_at, attempts) "
            "VALUES (?, ?, 0)",
            (quest_id, now),
        )
        conn.execute(
            "UPDATE quest_progress SET attempts = attempts + 1 WHERE quest_id = ?",
            (quest_id,),
        )


def get_quest_progress(quest_id: str) -> tuple[str | None, int]:
    """Devuelve (first_attempt_at, attempts) o (None, 0) si no hay row."""
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT first_attempt_at, attempts FROM quest_progress WHERE quest_id = ?",
            (quest_id,),
        ).fetchone()
    if row is None:
        return None, 0
    return row[0], int(row[1])

def record_quest_completion(quest_id: str, difficulty : int, rank: str) -> None:

    init_db()

    completion_was_new = False
    xp_before = 0
    level_before = 1
    new_xp = 0
    new_level = 1
    xp_reward = 0
    final_attempts = 1
    first_attempt_at: str | None = None
    total_time_seconds: int | None = None

    now_iso = datetime.now().isoformat(timespec="seconds")

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

        # Lee quest_progress: si el aprendiz vino vía arkanum start/check, ya
        # existe. Si invocó check.py directamente, no hay row y caemos a
        # attempts=1 + first_attempt_at=now.
        progress_row = conn.execute(
            "SELECT first_attempt_at, attempts FROM quest_progress WHERE quest_id = ?",
            (quest_id,),
        ).fetchone()

        if progress_row is not None:
            first_attempt_at = progress_row[0]
            # +1 porque éste es el intento que pasa; record_quest_attempt no
            # lo cuenta para evitar que llegue aquí ya incrementado.
            final_attempts = int(progress_row[1]) + 1
        else:
            first_attempt_at = now_iso
            final_attempts = 1

        try:
            start_dt = datetime.fromisoformat(first_attempt_at)
            end_dt = datetime.fromisoformat(now_iso)
            total_time_seconds = max(0, int((end_dt - start_dt).total_seconds()))
        except ValueError:
            total_time_seconds = None

        xp_reward = get_xp_reward(difficulty)
        new_xp = xp_before + xp_reward
        new_level = calculate_level(new_xp)

        conn.execute(
            """
            INSERT INTO quest_completion (
                quest_id, difficulty, completed_at,
                attempts, first_attempt_at, total_time_seconds
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                quest_id,
                difficulty,
                now_iso,
                final_attempts,
                first_attempt_at,
                total_time_seconds,
            ),
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
            attempts=final_attempts,
            total_time_seconds=total_time_seconds,
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
    attempts: int = 1,
    total_time_seconds: int | None = None,
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
                "attempts": attempts,
                "total_time_seconds": total_time_seconds,
            },
        )
    except Exception:
        pass

    try:
        open_celebration(quest_id)
    except Exception:
        pass