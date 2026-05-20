"""Lectura del estado del aprendiz para el dashboard.

Wrappea las queries simples de `common.progress.db` y aplica la lógica de
visibilidad (completed / current / locked) por quest según el orden global
del catálogo.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from common.dashboard.services.quest_catalog import QUESTS, QuestMeta, quest_by_slug
from common.progress.db import get_connection, init_db
from common.progress.levels import xp_progress

QuestStatus = Literal["completed", "current", "locked"]


@dataclass(frozen=True)
class Apprentice:
    username: str
    current_rank: str
    xp: int
    level: int


def get_apprentice() -> Apprentice | None:
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT username, current_rank, xp, level FROM apprentice WHERE id = 1"
        ).fetchone()
    if row is None:
        return None
    return Apprentice(*row)


def get_completed_quest_ids() -> set[str]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute("SELECT quest_id FROM quest_completion").fetchall()
    return {r[0] for r in rows}


def get_completed_count() -> int:
    return len(get_completed_quest_ids())


def get_xp_breakdown(total_xp: int) -> tuple[int, int, int, int]:
    """Devuelve (level, xp_in_level, xp_required_for_next_level, percentage)."""
    level, xp_in_level, required = xp_progress(total_xp)
    percentage = int(100 * xp_in_level / required) if required else 0
    return level, xp_in_level, required, percentage


def get_quest_status_map() -> dict[str, QuestStatus]:
    """Mapa `slug -> status`. La primera quest no completada se marca 'current'."""
    completed_db_ids = get_completed_quest_ids()
    statuses: dict[str, QuestStatus] = {}
    current_assigned = False
    for quest in QUESTS:
        if quest.db_id in completed_db_ids:
            statuses[quest.slug] = "completed"
        elif not current_assigned:
            statuses[quest.slug] = "current"
            current_assigned = True
        else:
            statuses[quest.slug] = "locked"
    return statuses


def get_current_quest() -> QuestMeta | None:
    for slug, status in get_quest_status_map().items():
        if status == "current":
            return quest_by_slug(slug)
    return None
