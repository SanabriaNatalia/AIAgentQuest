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


def live_agent_unlocked() -> bool:
    """True si el aprendiz ya llegó al primer quest con agent loop (Q07).

    La vista `/live-agent` solo tiene sentido a partir de ahí: antes el agente
    no ejecuta tools ni se traza, así que mostrar la Constelación con sus 4
    herramientas confundiría (parecería que ya están construidas). "Llegó" =
    algún quest con `live_agent=True` está `current` o `completed` (no `locked`).
    """
    status_map = get_quest_status_map()
    for quest in QUESTS:
        if getattr(quest, "live_agent", False) and \
                status_map.get(quest.slug) in ("current", "completed"):
            return True
    return False


def is_quest_readme_read(quest_db_id: str) -> bool:
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM quest_reading WHERE quest_id = ?",
            (quest_db_id,),
        ).fetchone()
    return row is not None
