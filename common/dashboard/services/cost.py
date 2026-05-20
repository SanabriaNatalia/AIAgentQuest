"""Tracking de costo de invocaciones a Gemini (F14).

Cada `arkanum check` que pasa por un quest a partir de Q02 imprime
`Prompt tokens: X` / `Response tokens: Y`. El CLI las captura por línea
y persiste vía `record_cost(quest_id, prompt_tokens, response_tokens)`.

Pricing: Gemini 2.5 Flash, valores públicos a 2026-05.
- Input:  $0.075 / 1M tokens
- Output: $0.30  / 1M tokens

Si Google cambia los precios, edita las constantes y `arkanum cost`
se actualiza automáticamente.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from common.dashboard.services.quest_catalog import QUESTS, QuestMeta, quest_by_db_id
from common.progress.db import get_connection, init_db

_PROMPT_TOKENS_RE = re.compile(r"Prompt tokens:\s*(\d+)", re.IGNORECASE)
_RESPONSE_TOKENS_RE = re.compile(r"Response tokens:\s*(\d+)", re.IGNORECASE)


def parse_tokens(stdout: str) -> tuple[int, int]:
    """Suma todos los `Prompt tokens:` / `Response tokens:` que encuentre.

    Devuelve `(0, 0)` si el stdout no menciona ninguna de las dos líneas
    (caso Q01, que no expone usage_metadata). Se ignoran las menciones en
    comentarios — si por algún motivo el aprendiz hace `print("Prompt tokens:")`
    sin un número, el regex no matchea (`\\d+` requiere dígitos).
    """
    prompt_sum = sum(int(m.group(1)) for m in _PROMPT_TOKENS_RE.finditer(stdout))
    response_sum = sum(int(m.group(1)) for m in _RESPONSE_TOKENS_RE.finditer(stdout))
    return prompt_sum, response_sum

PRICE_INPUT_PER_1M = 0.075   # USD por 1M tokens de prompt
PRICE_OUTPUT_PER_1M = 0.30   # USD por 1M tokens de respuesta


@dataclass(frozen=True)
class QuestCostRow:
    quest: QuestMeta
    prompt_tokens: int
    response_tokens: int
    invocations: int

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.response_tokens

    @property
    def estimated_usd(self) -> float:
        return _usd(self.prompt_tokens, self.response_tokens)


@dataclass(frozen=True)
class CostAttempt:
    """Una fila cruda de quest_costs (cada invocación parseada del stdout)."""
    id: int
    quest: QuestMeta | None
    attempted_at: str
    prompt_tokens: int
    response_tokens: int

    @property
    def estimated_usd(self) -> float:
        return _usd(self.prompt_tokens, self.response_tokens)


def _usd(prompt_tokens: int, response_tokens: int) -> float:
    return (
        prompt_tokens * PRICE_INPUT_PER_1M / 1_000_000
        + response_tokens * PRICE_OUTPUT_PER_1M / 1_000_000
    )


def record_cost(
    quest_db_id: str,
    prompt_tokens: int,
    response_tokens: int,
    attempted_at: str | None = None,
) -> None:
    """Persiste el costo de una invocación. No-op si ambos tokens son 0."""
    if prompt_tokens <= 0 and response_tokens <= 0:
        return
    init_db()
    when = attempted_at or datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO quest_costs (quest_id, attempted_at, prompt_tokens, response_tokens) "
            "VALUES (?, ?, ?, ?)",
            (quest_db_id, when, prompt_tokens, response_tokens),
        )


def cost_per_quest() -> list[QuestCostRow]:
    """Agregado por quest. Sólo incluye quests que tienen al menos una invocación."""
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT quest_id, SUM(prompt_tokens), SUM(response_tokens), COUNT(*) "
            "FROM quest_costs GROUP BY quest_id"
        ).fetchall()

    out: list[QuestCostRow] = []
    for db_id, prompt_sum, resp_sum, count in rows:
        meta = quest_by_db_id(db_id)
        if meta is None:
            # quest_id huérfano (renombrado o legacy) — saltar para no romper UI.
            continue
        out.append(
            QuestCostRow(
                quest=meta,
                prompt_tokens=int(prompt_sum or 0),
                response_tokens=int(resp_sum or 0),
                invocations=int(count or 0),
            )
        )
    # Orden estable por número de quest.
    out.sort(key=lambda r: r.quest.order)
    return out


def total_cost() -> dict:
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(prompt_tokens), 0), COALESCE(SUM(response_tokens), 0), COUNT(*) "
            "FROM quest_costs"
        ).fetchone()
    prompt_sum, resp_sum, count = int(row[0]), int(row[1]), int(row[2])
    return {
        "prompt_tokens": prompt_sum,
        "response_tokens": resp_sum,
        "total_tokens": prompt_sum + resp_sum,
        "invocations": count,
        "estimated_usd": _usd(prompt_sum, resp_sum),
    }


def attempts_history(limit: int = 50) -> list[CostAttempt]:
    """Histórico crudo de invocaciones, más reciente primero."""
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, quest_id, attempted_at, prompt_tokens, response_tokens "
            "FROM quest_costs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        CostAttempt(
            id=int(r[0]),
            quest=quest_by_db_id(r[1]),
            attempted_at=r[2],
            prompt_tokens=int(r[3]),
            response_tokens=int(r[4]),
        )
        for r in rows
    ]


def has_any_cost() -> bool:
    init_db()
    with get_connection() as conn:
        row = conn.execute("SELECT 1 FROM quest_costs LIMIT 1").fetchone()
    return row is not None
