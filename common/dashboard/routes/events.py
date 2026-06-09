"""Endpoints que reciben eventos del laboratorio (notify.py, arkanum run, etc.).

Cada evento se persiste en la tabla `events` con `seen=0`. El dashboard
los consume vía `GET /api/events/recent`, que los marca como vistos al
servirlos para evitar repetir celebraciones.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from common.progress.db import get_connection, init_db

router = APIRouter()


class QuestCompletedPayload(BaseModel):
    quest_id: str
    difficulty: int | None = None
    rank: str | None = None
    # Snapshot del estado del aprendiz antes/después del INSERT.
    # Permite que /celebrate detecte level-up sin volver a consultar la BD
    # del estado anterior (que ya cambió).
    xp_before: int | None = None
    xp_after: int | None = None
    xp_reward: int | None = None
    level_before: int | None = None
    level_after: int | None = None
    # F13: tracking de intentos + tiempo total (segundos)
    attempts: int | None = None
    total_time_seconds: int | None = None


def _store_event(kind: str, payload: dict[str, Any]) -> int:
    init_db()
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO events (kind, payload, seen, created_at) VALUES (?, ?, 0, ?)",
            (kind, json.dumps(payload, ensure_ascii=False), now),
        )
        event_id = cur.lastrowid
    return int(event_id)


@router.post("/events/quest-completed")
def quest_completed(payload: QuestCompletedPayload) -> dict:
    event_id = _store_event("quest_completed", payload.model_dump(exclude_none=False))
    return {
        "ok": True,
        "event_id": event_id,
        "redirect": f"/celebrate?quest={payload.quest_id}",
    }


class ActClosedPayload(BaseModel):
    act_number: int


@router.post("/events/act-closed")
def act_closed(payload: ActClosedPayload) -> dict:
    event_id = _store_event("act_closed", payload.model_dump())
    return {
        "ok": True,
        "event_id": event_id,
        "redirect": "/milestones",
    }


class TracePayload(BaseModel):
    trace_id: str
    step_type: str
    name: str | None = None
    payload: str | None = None
    quest_db_id: str | None = None


@router.post("/events/trace")
def trace_event(payload: TracePayload) -> dict:
    """Recibe un step del agent loop capturado por `arkanum run` (Q07/Q08).

    No usa la tabla `events` (que es para notificaciones one-shot);
    los traces viven en `agent_traces` para que `/live-agent` pueda
    paginarlos y filtrar por `trace_id`.
    """
    from common.dashboard.services.trace import record_step

    step_id = record_step(
        trace_id=payload.trace_id,
        step_type=payload.step_type,
        name=payload.name,
        payload=payload.payload,
        quest_db_id=payload.quest_db_id,
    )
    return {"ok": True, "step_id": step_id}
