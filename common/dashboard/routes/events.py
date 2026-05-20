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
