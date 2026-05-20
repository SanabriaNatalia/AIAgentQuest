"""Construye el contexto de `/celebrate`.

La página intenta hidratarse con el último evento `quest_completed`
disponible para el quest indicado. Si no hay evento (porque el aprendiz
abrió la URL manualmente o ya está marcado como `seen=1`), cae a una
versión "diferida" usando lo poco que sabemos por slug + estado actual.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from common.dashboard.services.achievements import Achievement, achievements_for
from common.dashboard.services.progress import get_apprentice
from common.dashboard.services.quest_catalog import ACTS, QuestMeta
from common.progress.db import get_connection, init_db


@dataclass(frozen=True)
class CelebrationData:
    quest: QuestMeta | None
    act_name: str | None
    xp_reward: int | None
    xp_total: int | None
    level_before: int | None
    level_after: int | None
    leveled_up: bool
    apprentice_name: str | None
    attempts: int | None = None
    total_time_seconds: int | None = None
    achievements: list[Achievement] = field(default_factory=list)


def _find_event(quest_meta: QuestMeta | None) -> dict[str, Any] | None:
    """Busca el evento quest_completed más reciente.

    No filtramos por `seen` — `/celebrate` puede abrirse después del
    polling que ya lo marcó. Si quest_meta está dado, intentamos primero
    eventos cuyo payload.quest_id coincida con su `slug` o `db_id`.
    """
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT payload FROM events WHERE kind = 'quest_completed' "
            "ORDER BY id DESC LIMIT 10"
        ).fetchall()

    parsed: list[dict[str, Any]] = []
    for (payload,) in rows:
        try:
            parsed.append(json.loads(payload))
        except (TypeError, ValueError):
            continue

    if not parsed:
        return None

    if quest_meta is not None:
        targets = {quest_meta.slug, quest_meta.db_id}
        for ev in parsed:
            if ev.get("quest_id") in targets:
                return ev

    return parsed[0]


def build_celebration_context(quest_meta: QuestMeta | None) -> dict[str, Any]:
    event = _find_event(quest_meta)
    apprentice = get_apprentice()

    xp_reward: int | None = None
    xp_total: int | None = None
    level_before: int | None = None
    level_after: int | None = None
    attempts: int | None = None
    total_time_seconds: int | None = None

    if event is not None:
        xp_reward = event.get("xp_reward")
        xp_total = event.get("xp_after")
        level_before = event.get("level_before")
        level_after = event.get("level_after")
        attempts = event.get("attempts")
        total_time_seconds = event.get("total_time_seconds")

    if xp_total is None and apprentice is not None:
        xp_total = apprentice.xp
    if level_after is None and apprentice is not None:
        level_after = apprentice.level

    leveled_up = (
        level_before is not None
        and level_after is not None
        and level_after > level_before
    )

    act_name = ACTS[quest_meta.act].name if quest_meta else None
    achievements = achievements_for(quest_meta) if quest_meta else []
    data = CelebrationData(
        quest=quest_meta,
        act_name=act_name,
        xp_reward=xp_reward,
        xp_total=xp_total,
        level_before=level_before,
        level_after=level_after,
        leveled_up=leveled_up,
        apprentice_name=apprentice.username if apprentice else None,
        attempts=attempts,
        total_time_seconds=total_time_seconds,
        achievements=achievements,
    )
    return {"celebration": data}
