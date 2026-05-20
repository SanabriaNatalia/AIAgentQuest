"""Servicio de hitos de la travesía (F15).

Cada acto que cierra (todas sus quests completadas) deja una fila en
`act_milestones(act_number, closed_at)`. Este módulo agrega esa data
con el catálogo para exponer información rica al template.
"""
from __future__ import annotations

from dataclasses import dataclass

from common.dashboard.services.quest_catalog import ACTS, ActMeta, QUESTS, QuestMeta
from common.progress.db import get_connection, init_db


@dataclass(frozen=True)
class ClosedAct:
    act: ActMeta
    closed_at: str
    quests: tuple[QuestMeta, ...]
    ranks: tuple[str, ...]


def closed_acts() -> list[ClosedAct]:
    """Lista de actos cerrados ordenada por número de acto."""
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT act_number, closed_at FROM act_milestones ORDER BY act_number"
        ).fetchall()

    out: list[ClosedAct] = []
    for act_number, closed_at in rows:
        act = ACTS.get(int(act_number))
        if act is None:
            continue
        quests = tuple(q for q in QUESTS if q.act == act.number)
        ranks = tuple(q.rank_unlocked for q in quests)
        out.append(
            ClosedAct(
                act=act,
                closed_at=closed_at,
                quests=quests,
                ranks=ranks,
            )
        )
    return out


def closed_act_numbers() -> set[int]:
    """Sólo los números, útil para el mapa (banner luminoso por acto)."""
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT act_number FROM act_milestones"
        ).fetchall()
    return {int(r[0]) for r in rows}
