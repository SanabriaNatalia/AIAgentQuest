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

        # F14: cada check.py que llama a Gemini imprime "Prompt tokens: X" y
        # "Response tokens: Y". El CLI las captura por línea y persiste aquí.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quest_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quest_id TEXT NOT NULL,
                attempted_at TEXT NOT NULL,
                prompt_tokens INTEGER NOT NULL DEFAULT 0,
                response_tokens INTEGER NOT NULL DEFAULT 0
            )
        """)

        # F16: traces del agent loop capturados por `arkanum run` en
        # Q07/Q08. Cada step es una línea parseada del stdout del starter
        # (function_call, function_result, tokens). `trace_id` agrupa todos
        # los steps de una misma corrida.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT NOT NULL,
                quest_id TEXT,
                step_type TEXT NOT NULL,
                name TEXT,
                payload TEXT,
                created_at TEXT NOT NULL
            )
        """)

        _add_column_if_missing(conn, "apprentice", "created_at", "TEXT")
        _add_column_if_missing(conn, "apprentice", "avatar", "TEXT DEFAULT 'default'")
        _add_column_if_missing(conn, "quest_completion", "attempts", "INTEGER DEFAULT 1")
        _add_column_if_missing(conn, "quest_completion", "first_attempt_at", "TEXT")
        _add_column_if_missing(conn, "quest_completion", "total_time_seconds", "INTEGER")
        # Marca si el aprendiz arrancó el cronómetro pulsando "⚜ Empezar ahora"
        # en el dashboard. Si vale 0 al completarse el quest, no podemos
        # contabilizar el tiempo y guardamos total_time_seconds = NULL (N/A).
        _add_column_if_missing(conn, "quest_progress", "started_explicitly", "INTEGER DEFAULT 0")


def register_first_attempt(quest_id: str) -> None:
    """Marca el arranque explícito del cronómetro al pulsar "⚜ Empezar ahora".

    - Si no hay row de quest_progress: la crea con `started_explicitly = 1`.
    - Si ya existe pero todavía no se inició explícitamente (fue creada por
      el fallback de `record_quest_attempt`), la "rebobina": `first_attempt_at`
      pasa a este momento y `started_explicitly` queda en 1. Razonamiento:
      si el aprendiz pulsa el botón después de un check fallido, el cronómetro
      debería arrancar ahora, no desde el check fallido.
    - Si ya estaba marcada como iniciada explícitamente, es no-op (idempotente).
    - Si el quest ya está completado, no toca nada.
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
            "INSERT OR IGNORE INTO quest_progress "
            "(quest_id, first_attempt_at, attempts, started_explicitly) "
            "VALUES (?, ?, 0, 1)",
            (quest_id, now),
        )
        conn.execute(
            "UPDATE quest_progress "
            "SET started_explicitly = 1, first_attempt_at = ? "
            "WHERE quest_id = ? AND started_explicitly = 0",
            (now, quest_id),
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
        # un arkanum run previo.
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

def _check_and_close_acts(conn) -> list[int]:
    """Marca como cerrados todos los actos cuyas quests están completadas.

    Idempotente vía `INSERT OR IGNORE` en `act_milestones`. Recorre el
    catálogo de actos (sólo los `available`, con `quest_slugs` no vacío)
    para soportar también el cierre retroactivo de actos cerrados antes
    de F15 — la primera completación post-F15 dispara el backfill.

    Devuelve la lista de `act_number` recién cerrados (los que no
    estaban ya en la tabla). Si no hay ninguno nuevo, lista vacía.
    """
    # Import diferido: quest_catalog no debería forzar carga de dashboard
    # cuando se usa db.py desde un script aislado.
    try:
        from common.dashboard.services.quest_catalog import ACTS, quest_by_slug
    except Exception:
        return []

    newly_closed: list[int] = []
    now = datetime.now().isoformat(timespec="seconds")

    for act_num, act in ACTS.items():
        if act.status != "available" or not act.quest_slugs:
            continue

        db_ids: list[str] = []
        for slug in act.quest_slugs:
            meta = quest_by_slug(slug)
            if meta is not None:
                db_ids.append(meta.db_id)
        if not db_ids:
            continue

        placeholders = ",".join("?" * len(db_ids))
        count_row = conn.execute(
            f"SELECT COUNT(*) FROM quest_completion WHERE quest_id IN ({placeholders})",
            db_ids,
        ).fetchone()
        if count_row is None or int(count_row[0]) != len(db_ids):
            continue

        cur = conn.execute(
            "INSERT OR IGNORE INTO act_milestones (act_number, closed_at) VALUES (?, ?)",
            (act_num, now),
        )
        if cur.rowcount > 0:
            newly_closed.append(act_num)

    return newly_closed


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
    newly_closed_acts: list[int] = []

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

        # Lee quest_progress: si el aprendiz vino vía arkanum check o pulsó
        # el botón "⚜ Empezar ahora", ya existe. Si invocó check.py
        # directamente sin pasar por el CLI, no hay row.
        progress_row = conn.execute(
            "SELECT first_attempt_at, attempts, started_explicitly "
            "FROM quest_progress WHERE quest_id = ?",
            (quest_id,),
        ).fetchone()

        started_explicitly = False
        if progress_row is not None:
            first_attempt_at = progress_row[0]
            # +1 porque éste es el intento que pasa; record_quest_attempt no
            # lo cuenta para evitar que llegue aquí ya incrementado.
            final_attempts = int(progress_row[1]) + 1
            started_explicitly = bool(progress_row[2])
        else:
            first_attempt_at = now_iso
            final_attempts = 1

        # El cronómetro sólo cuenta si el aprendiz pulsó "⚜ Empezar ahora".
        # Sin ese arranque explícito no podemos contabilizar el tiempo y
        # guardamos NULL → el dashboard mostrará "N/A".
        if not started_explicitly:
            total_time_seconds = None
        else:
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
        newly_closed_acts = _check_and_close_acts(conn)

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
        for act_num in newly_closed_acts:
            _notify_act_closed(act_num)


def _notify_act_closed(act_number: int) -> None:
    """Best-effort: arranca dashboard si no está y emite evento act_closed."""
    try:
        from common.dashboard.lifecycle import ensure_started
        from common.progress.notify import emit_event
    except Exception:
        return

    try:
        ensure_started()
    except Exception:
        pass

    try:
        emit_event("act-closed", {"act_number": act_number})
    except Exception:
        pass


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