"""Servicio del sistema de pistas (mecánica F11).

Cada quest expone hasta 3 pistas en orden estricto:

| Nivel | Archivo                | Naturaleza                                       |
|-------|------------------------|--------------------------------------------------|
| 1     | `1_susurro.md`         | Pregunta orientadora                             |
| 2     | `2_revelacion.md`      | Nombre del concepto / función / estructura       |
| 3     | `3_manifestacion.md`   | Snippet mínimo (2-4 líneas)                      |

Reglas:
- La pista I siempre se puede solicitar.
- La II requiere la I previamente solicitada.
- La III requiere la II.
- Una vez solicitada, la pista persiste (idempotente).
- Sin penalización de XP; sólo afecta el logro "Sin red" calculado on-the-fly.

Persistencia: tabla `hint_usage(quest_id, hint_level, requested_at)`, ya
creada en F0. `quest_id` usa `db_id` (consistencia con el resto del schema).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from common.dashboard.services.markdown import (
    RenderedMarkdown,
    render_markdown_file,
)
from common.dashboard.services.quest_catalog import QuestMeta
from common.progress.db import get_connection, init_db

_REPO_ROOT = Path(__file__).resolve().parents[3]

HINT_LEVELS: tuple[tuple[int, str, str], ...] = (
    (1, "Susurro", "1_susurro.md"),
    (2, "Revelación", "2_revelacion.md"),
    (3, "Manifestación", "3_manifestacion.md"),
)

LEVEL_DESCRIPTIONS: dict[int, str] = {
    1: "Una pregunta orientadora para volver a observar lo que ya tienes.",
    2: "El nombre del concepto, función o estructura que falta.",
    3: "Un fragmento de código mínimo (2-4 líneas) que rompe el bloqueo.",
}


@dataclass(frozen=True)
class HintMeta:
    level: int
    title: str
    name: str
    description: str
    file_exists: bool
    eligible: bool
    requested: bool
    requested_at: str | None


def _hint_path(quest: QuestMeta, file_name: str) -> Path:
    return _REPO_ROOT / "quests" / quest.slug / "hints" / file_name


def used_hints(quest: QuestMeta) -> set[int]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT hint_level FROM hint_usage WHERE quest_id = ?",
            (quest.db_id,),
        ).fetchall()
    return {int(r[0]) for r in rows}


def _used_with_dates(quest: QuestMeta) -> dict[int, str]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT hint_level, requested_at FROM hint_usage WHERE quest_id = ?",
            (quest.db_id,),
        ).fetchall()
    return {int(level): requested_at for level, requested_at in rows}


def list_hints_for(quest: QuestMeta) -> list[HintMeta]:
    """Estado de las 3 pistas para `quest`. Eligibility se calcula en cascada."""
    used = _used_with_dates(quest)
    metas: list[HintMeta] = []
    previous_requested = True  # La I siempre arranca elegible.
    for level, title, file_name in HINT_LEVELS:
        path = _hint_path(quest, file_name)
        requested = level in used
        eligible = previous_requested
        metas.append(
            HintMeta(
                level=level,
                title=title,
                name=file_name,
                description=LEVEL_DESCRIPTIONS[level],
                file_exists=path.exists(),
                eligible=eligible,
                requested=requested,
                requested_at=used.get(level),
            )
        )
        previous_requested = requested
    return metas


def get_hint(quest: QuestMeta, level: int) -> RenderedMarkdown | None:
    """Renderiza el `.md` de una pista YA solicitada. Devuelve None si no lo ha sido."""
    if level not in used_hints(quest):
        return None
    file_name = next((name for lvl, _, name in HINT_LEVELS if lvl == level), None)
    if file_name is None:
        return None
    path = _hint_path(quest, file_name)
    if not path.exists():
        return None
    return render_markdown_file(path)


class HintRequestError(Exception):
    """Solicitud de pista inválida (fuera de orden / nivel inexistente)."""


def request_hint(quest: QuestMeta, level: int) -> str:
    """Marca la pista como solicitada. Devuelve la fecha (ISO).

    Levanta `HintRequestError` si:
    - `level` no está en {1,2,3}.
    - El archivo de la pista no existe en el repositorio.
    - La pista anterior no ha sido solicitada (orden estricto).
    """
    if level not in {1, 2, 3}:
        raise HintRequestError(f"Nivel inválido: {level}. Debe ser 1, 2 o 3.")

    file_name = next((name for lvl, _, name in HINT_LEVELS if lvl == level), None)
    if file_name is None or not _hint_path(quest, file_name).exists():
        raise HintRequestError(
            f"La pista nivel {level} no existe para este quest todavía."
        )

    used = used_hints(quest)
    if level > 1 and (level - 1) not in used:
        raise HintRequestError(
            "Las pistas se solicitan en orden estricto. Primero pide la anterior."
        )

    init_db()
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO hint_usage (quest_id, hint_level, requested_at) "
            "VALUES (?, ?, ?)",
            (quest.db_id, level, now),
        )
        row = conn.execute(
            "SELECT requested_at FROM hint_usage WHERE quest_id = ? AND hint_level = ?",
            (quest.db_id, level),
        ).fetchone()

    return row[0] if row else now


def is_no_red_eligible(quest: QuestMeta) -> bool:
    """¿El logro "Sin red" sigue al alcance para este quest?"""
    return not used_hints(quest)
