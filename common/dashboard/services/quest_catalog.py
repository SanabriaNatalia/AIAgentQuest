"""Metadata estática de los 8 quests y los 4 actos del laboratorio.

`db_id` corresponde al string que cada `check.py` pasa a
`record_quest_completion`, y por lo tanto es la clave usada para consultar
la tabla `quest_completion`. `slug` se usa para URLs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from common.progress.levels import get_xp_reward


@dataclass(frozen=True)
class QuestMeta:
    slug: str
    db_id: str
    title: str
    act: int
    order: int
    difficulty: int
    rank_unlocked: str
    banner: str
    quote_zhyreon: str
    # True si `arkanum check N` ejecuta un starter que llama a Gemini.
    # Permite condicionar el aviso "consume cuota de Gemini" (ver check.py).
    uses_gemini: bool = True
    # True si la quest emite traces que `/live-agent` puede visualizar.
    # Solo Q07/Q08 hoy (agent loop con tools); el CLI ofrece lanzar
    # `arkanum run N` automáticamente tras un check exitoso.
    live_agent: bool = False
    # Prompt sugerido si el aprendiz no pasó uno al check explícitamente.
    live_agent_default_prompt: str | None = None

    @property
    def xp(self) -> int:
        return get_xp_reward(self.difficulty)


@dataclass(frozen=True)
class ActMeta:
    number: int
    name: str
    quote_zhyreon: str
    status: Literal["available", "in_development"]
    quest_slugs: tuple[str, ...]


QUESTS: tuple[QuestMeta, ...] = (
    QuestMeta(
        slug="quest_01_first_invocation",
        db_id="La Primera Invocación",
        title="La Primera Invocación",
        act=1,
        order=1,
        difficulty=1,
        rank_unlocked="Invocador Principiante",
        banner="quest-1-banner.png",
        quote_zhyreon=(
            "Antes de otorgar memoria, herramientas o conocimiento, "
            "primero debes aprender a invocar una voz."
        ),
    ),
    QuestMeta(
        slug="quest_02_arcane_gauge",
        db_id="El Medidor Arcano",
        title="El Medidor Arcano",
        act=1,
        order=2,
        difficulty=1,
        rank_unlocked="Tasador de Respuestas",
        banner="quest-2-banner.png",
        quote_zhyreon=(
            "Toda invocación consume energía. Los aprendices imprudentes "
            "agotan sus recursos antes de comprender el costo de sus palabras."
        ),
    ),
    QuestMeta(
        slug="quest_03_apprentice_voice",
        db_id="La Voz del Aprendiz",
        title="La Voz del Aprendiz",
        act=1,
        order=3,
        difficulty=1,
        rank_unlocked="Proclamador Arcano",
        banner="quest-3-banner.png",
        quote_zhyreon=(
            "Un agente que solo repite instrucciones fijas no escucha realmente. "
            "La verdadera conversación comienza cuando el aprendiz puede hablar."
        ),
    ),
    QuestMeta(
        slug="quest_04_arkanum_laws",
        db_id="Las Leyes del Arkanum",
        title="Las Leyes del Arkanum",
        act=1,
        order=4,
        difficulty=1,
        rank_unlocked="Ejecutor de Leyes",
        banner="quest-4-banner.png",
        quote_zhyreon="Todo agente obedece primero las leyes que le dieron forma.",
    ),
    QuestMeta(
        slug="quest_05_forbidden_directory",
        db_id="El Directorio Prohibido",
        title="El Directorio Prohibido",
        act=2,
        order=5,
        difficulty=2,
        rank_unlocked="Guardián del Umbral",
        banner="quest-5-banner.png",
        quote_zhyreon=(
            "Antes de entregar herramientas a un agente, traza los límites "
            "del mundo donde puede actuar."
        ),
        uses_gemini=False,
    ),
    QuestMeta(
        slug="quest_06_tool_chest",
        db_id="El Cofre de Instrumentos",
        title="El Cofre de Instrumentos",
        act=2,
        order=6,
        difficulty=3,
        rank_unlocked="Artífice de Herramientas",
        banner="quest-6-banner.png",
        quote_zhyreon="Un agente deja de ser solo una voz cuando aprende a utilizar herramientas.",
    ),
    QuestMeta(
        slug="quest_07_agent_incarnation",
        db_id="La Encarnación del Agente",
        title="La Encarnación del Agente",
        act=2,
        order=7,
        difficulty=3,
        rank_unlocked="Conjurador de Encarnaciones",
        banner="quest-7-banner.png",
        quote_zhyreon="La voluntad deja de ser idea cuando encuentra manos.",
        live_agent=True,
        live_agent_default_prompt="¿Qué archivos hay en la raíz?",
    ),
    QuestMeta(
        slug="quest_08_manifesting_cycle",
        db_id="El Ciclo de la Manifestación",
        title="El Ciclo de la Manifestación",
        act=2,
        order=8,
        difficulty=3,
        rank_unlocked="Conjurador Encarnado",
        banner="quest-8-banner.png",
        quote_zhyreon=(
            "Una acción aislada puede ser accidente. "
            "La voluntad persistente transforma el mundo."
        ),
        # El check de Q08 valida estado del filesystem (calculator.py +
        # python tests.py), NO invoca al agente. El agente lo corre el
        # aprendiz antes con `arkanum run 8`.
        uses_gemini=False,
        live_agent=True,
        live_agent_default_prompt=(
            "Los tests de calculator están fallando. "
            "Ayúdame a corregir el error."
        ),
    ),
)


ACTS: dict[int, ActMeta] = {
    1: ActMeta(
        number=1,
        name="Fundamentos del Agente",
        quote_zhyreon=(
            "Antes de construir inteligencia, debes comprender conversación, "
            "contexto y voluntad."
        ),
        status="available",
        quest_slugs=tuple(q.slug for q in QUESTS if q.act == 1),
    ),
    2: ActMeta(
        number=2,
        name="Capacidad de Acción",
        quote_zhyreon=(
            "Una voz inteligente puede responder preguntas. "
            "Un agente encarnado puede transformar el mundo."
        ),
        status="available",
        quest_slugs=tuple(q.slug for q in QUESTS if q.act == 2),
    ),
    3: ActMeta(
        number=3,
        name="Inteligencia Extendida",
        quote_zhyreon=(
            "La memoria individual es limitada. "
            "Los grandes arquitectos construyen bibliotecas."
        ),
        status="in_development",
        quest_slugs=(),
    ),
    4: ActMeta(
        number=4,
        name="Arquitectura de Agentes",
        quote_zhyreon="Cuando múltiples inteligencias cooperan, nace una arquitectura.",
        status="in_development",
        quest_slugs=(),
    ),
}


def quest_by_slug(slug: str) -> QuestMeta | None:
    for quest in QUESTS:
        if quest.slug == slug:
            return quest
    return None


def quest_by_db_id(db_id: str) -> QuestMeta | None:
    for quest in QUESTS:
        if quest.db_id == db_id:
            return quest
    return None


def quests_in_act(act: int) -> tuple[QuestMeta, ...]:
    return tuple(q for q in QUESTS if q.act == act)
