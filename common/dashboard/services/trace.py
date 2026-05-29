"""Servicio de traces del agent loop (F16).

`arkanum run` captura el stdout de Q07-Q08 línea-por-línea y, por cada
patrón reconocido, llama `record_step(...)`. La página `/live-agent`
hace polling de `recent_steps()` cada segundo para renderizar el grafo.

Parser de líneas:
- `Calling function: NAME(ARGS)` → step_type=`function_call`, payload=ARGS.
- `-> {...}` o `-> ...`        → step_type=`function_result`.
- `Prompt tokens: N`           → step_type=`tokens` (prompt).
- `Response tokens: N`         → step_type=`tokens` (response).

El parser vive en `arkanum.cli.commands.run` para no acoplar este
servicio al formato concreto; este módulo sólo persiste y consulta.
"""
from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from datetime import datetime

from common.dashboard.services.quest_catalog import QuestMeta, quest_by_db_id
from common.progress.db import get_connection, init_db


@dataclass(frozen=True)
class TraceStep:
    id: int
    trace_id: str
    quest: QuestMeta | None
    step_type: str
    name: str | None
    payload: str | None
    created_at: str


@dataclass(frozen=True)
class TraceSummary:
    trace_id: str
    quest: QuestMeta | None
    started_at: str
    last_step_at: str
    steps: int


def start_trace() -> str:
    """Genera un trace_id corto y aleatorio. No reserva nada en DB."""
    return secrets.token_hex(6)


def record_step(
    trace_id: str,
    step_type: str,
    name: str | None = None,
    payload: str | None = None,
    quest_db_id: str | None = None,
    created_at: str | None = None,
) -> int:
    """Persiste un step y devuelve su id."""
    init_db()
    when = created_at or datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO agent_traces (trace_id, quest_id, step_type, name, payload, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (trace_id, quest_db_id, step_type, name, payload, when),
        )
        return int(cur.lastrowid or 0)


def recent_steps(limit: int = 200, trace_id: str | None = None) -> list[TraceStep]:
    """Devuelve los pasos más recientes (DESC). Si `trace_id` se da, filtra."""
    init_db()
    with get_connection() as conn:
        if trace_id is None:
            rows = conn.execute(
                "SELECT id, trace_id, quest_id, step_type, name, payload, created_at "
                "FROM agent_traces ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, trace_id, quest_id, step_type, name, payload, created_at "
                "FROM agent_traces WHERE trace_id = ? ORDER BY id DESC LIMIT ?",
                (trace_id, limit),
            ).fetchall()

    return [
        TraceStep(
            id=int(r[0]),
            trace_id=r[1],
            quest=quest_by_db_id(r[2]) if r[2] else None,
            step_type=r[3],
            name=r[4],
            payload=r[5],
            created_at=r[6],
        )
        for r in rows
    ]


def recent_trace_summaries(limit: int = 10) -> list[TraceSummary]:
    """Devuelve los N últimos traces como summaries, sin sus steps.

    Útil para el historial de `/live-agent` (mejora #4): permite mostrar
    una lista clickable de ejecuciones previas sin cargar todos los
    payloads. La consulta agrupa por `trace_id` y ordena por el step
    más reciente de cada uno.
    """
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT trace_id, "
            "       MIN(created_at) AS started_at, "
            "       MAX(created_at) AS last_step_at, "
            "       COUNT(*)        AS steps, "
            "       MIN(quest_id)   AS quest_id, "
            "       MAX(id)         AS last_step_id "
            "FROM agent_traces "
            "GROUP BY trace_id "
            "ORDER BY last_step_id DESC "
            "LIMIT ?",
            (limit,),
        ).fetchall()

    return [
        TraceSummary(
            trace_id=r[0],
            quest=quest_by_db_id(r[4]) if r[4] else None,
            started_at=r[1] or "",
            last_step_at=r[2] or "",
            steps=int(r[3] or 0),
        )
        for r in rows
    ]


def trace_first_user_prompt(trace_id: str) -> str | None:
    """Extrae el `user_prompt` del primer session_start de un trace.

    Devuelve None si no hay session_start, si su payload no es JSON o
    si no contiene `user_prompt`. Usado por el historial para mostrar
    una preview del prompt original.
    """
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT payload FROM agent_traces "
            "WHERE trace_id = ? AND step_type = 'session_start' "
            "ORDER BY id ASC LIMIT 1",
            (trace_id,),
        ).fetchone()
    if row is None or not row[0]:
        return None
    try:
        data = json.loads(row[0])
    except (TypeError, ValueError):
        return None
    if isinstance(data, dict):
        prompt = data.get("user_prompt")
        if isinstance(prompt, str):
            return prompt
    return None


def latest_trace_summary() -> TraceSummary | None:
    """Resumen del trace más reciente, para mostrar al tope de /live-agent."""
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT trace_id FROM agent_traces ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        trace_id = row[0]
        stats = conn.execute(
            "SELECT MIN(created_at), MAX(created_at), COUNT(*), MIN(quest_id) "
            "FROM agent_traces WHERE trace_id = ?",
            (trace_id,),
        ).fetchone()

    if stats is None:
        return None
    started_at, last_step_at, count, q_db_id = stats
    return TraceSummary(
        trace_id=trace_id,
        quest=quest_by_db_id(q_db_id) if q_db_id else None,
        started_at=started_at or "",
        last_step_at=last_step_at or "",
        steps=int(count or 0),
    )


def safe_parse_payload(payload: str | None) -> object:
    """Intenta cargar el payload como JSON. Devuelve el string crudo si falla."""
    if payload is None:
        return None
    try:
        return json.loads(payload)
    except (TypeError, ValueError):
        return payload
