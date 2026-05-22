"""Logros calculados on-the-fly (sin tabla `achievements`).

Catálogo MVP (F13):
- **One shot** — el quest se cerró en un único intento (`quest_completion.attempts == 1`).
- **Sin red** — no se solicitó ninguna pista (`hint_usage` vacía para el quest).

Los logros se calculan a partir de las tablas existentes; no se persisten.
Esto evita inconsistencias si los criterios cambian más adelante.
"""
from __future__ import annotations

from dataclasses import dataclass

from common.dashboard.services.hints import is_no_red_eligible
from common.dashboard.services.quest_catalog import QUESTS, QuestMeta, quest_by_db_id
from common.progress.db import get_connection, init_db


@dataclass(frozen=True)
class Achievement:
    code: str
    title: str
    description: str
    icon: str


ONE_SHOT = Achievement(
    code="one_shot",
    title="One shot",
    description="Completaste el quest a la primera. Sin titubeos.",
    icon="🎯",
)

NO_RED = Achievement(
    code="no_red",
    title="Sin red",
    description="Cerraste el quest sin solicitar ninguna pista.",
    icon="🕯️",
)

CATALOG: tuple[Achievement, ...] = (ONE_SHOT, NO_RED)


def one_shot_eligible(quest: QuestMeta) -> bool:
    """¿La completación de `quest` fue al primer intento?

    Sólo aplica a quests YA completados. Si el quest no está cerrado o
    `attempts` es None (datos legacy pre-F13), devuelve False.
    """
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT attempts FROM quest_completion WHERE quest_id = ?",
            (quest.db_id,),
        ).fetchone()
    if row is None or row[0] is None:
        return False
    return int(row[0]) == 1


def no_red_eligible(quest: QuestMeta) -> bool:
    """¿El quest se cerró sin pedir pistas?

    Sólo cuenta si el quest está completado; estar "limpio" antes de
    completar no otorga el logro hasta que cierras.
    """
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM quest_completion WHERE quest_id = ?",
            (quest.db_id,),
        ).fetchone()
    if row is None:
        return False
    return is_no_red_eligible(quest)


def achievements_for(quest: QuestMeta) -> list[Achievement]:
    """Lista de logros obtenidos por el aprendiz para este quest."""
    result: list[Achievement] = []
    if one_shot_eligible(quest):
        result.append(ONE_SHOT)
    if no_red_eligible(quest):
        result.append(NO_RED)
    return result


def total_achievements() -> dict[str, int]:
    """Conteo global de logros desbloqueados (para el panel del perfil)."""
    counts = {ach.code: 0 for ach in CATALOG}
    for quest in QUESTS:
        for ach in achievements_for(quest):
            counts[ach.code] += 1
    return counts


def achievements_by_quest() -> dict[str, list[Achievement]]:
    """Map slug → lista de logros, sólo para quests completados."""
    out: dict[str, list[Achievement]] = {}
    for quest in QUESTS:
        achs = achievements_for(quest)
        if achs:
            out[quest.slug] = achs
    return out


def quest_stats(quest: QuestMeta) -> dict | None:
    """Resumen numérico de la completación: attempts, total_time_seconds.

    Devuelve None si el quest no está completado.
    """
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT attempts, first_attempt_at, completed_at, total_time_seconds "
            "FROM quest_completion WHERE quest_id = ?",
            (quest.db_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "attempts": row[0],
        "first_attempt_at": row[1],
        "completed_at": row[2],
        "total_time_seconds": row[3],
    }


# Exponemos `quest_by_db_id` por re-export para mantener un único punto de
# entrada desde plantillas y rutas que necesiten resolver db_id → QuestMeta.
__all__ = [
    "Achievement",
    "CATALOG",
    "ONE_SHOT",
    "NO_RED",
    "one_shot_eligible",
    "no_red_eligible",
    "achievements_for",
    "total_achievements",
    "achievements_by_quest",
    "quest_stats",
    "quest_by_db_id",
]
