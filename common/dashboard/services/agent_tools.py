"""Catálogo declarado de las herramientas del agente (Q06-Q08).

El visualizador `/live-agent` (vista de grafo "Constelación del Agente")
dibuja un nodo por herramienta alrededor del agente, **aunque el aprendiz
no las haya llamado todavía**. Para eso necesita conocer las tools de
antemano.

No leemos los `FunctionDeclaration` de `common/functions/*.py` porque solo
`schema_get_files_info` está implementado en el repo del aprendiz: los otros
tres (`schema_get_file_content`, `schema_write_file`, `schema_run_python_file`)
son `None` hasta que el aprendiz completa los TODO de Q06. Como las cuatro
herramientas del currículo son fijas y conocidas, las declaramos aquí de
forma estable e independiente del progreso del aprendiz.

Si en el futuro se añaden tools al curso, basta con extender `AGENT_TOOLS`.
"""
from __future__ import annotations

from typing import TypedDict


class AgentTool(TypedDict):
    name: str
    label: str
    icon: str
    description: str


# Orden = orden de presentación radial en el grafo. Las descripciones están
# alineadas con los docstrings / FunctionDeclaration de `common/functions/`.
AGENT_TOOLS: list[AgentTool] = [
    {
        "name": "get_files_info",
        "label": "Listar archivos",
        "icon": "📂",
        "description": (
            "Lista los archivos de un directorio (tamaño y si es carpeta), "
            "relativo al working directory."
        ),
    },
    {
        "name": "get_file_content",
        "label": "Leer archivo",
        "icon": "📄",
        "description": (
            "Lee el contenido de un archivo de texto (truncado a un máximo "
            "de caracteres) dentro del working directory."
        ),
    },
    {
        "name": "write_file",
        "label": "Escribir archivo",
        "icon": "✍️",
        "description": (
            "Crea o sobrescribe un archivo con el contenido indicado dentro "
            "del working directory."
        ),
    },
    {
        "name": "run_python_file",
        "label": "Ejecutar Python",
        "icon": "🐍",
        "description": (
            "Ejecuta un archivo .py en el sandbox y devuelve su stdout/stderr "
            "y el código de salida."
        ),
    },
]


# Tools por quest. Hoy Q07 y Q08 comparten las cuatro; indexar por quest deja
# el grafo preparado para que un quest futuro declare un set distinto sin tocar
# el frontend (el selector pide /api/agent/tools?quest=N).
_TOOLS_BY_QUEST: dict[int, tuple[str, ...]] = {
    7: ("get_files_info", "get_file_content", "write_file", "run_python_file"),
    8: ("get_files_info", "get_file_content", "write_file", "run_python_file"),
}


def list_agent_tools(quest_order: int | None = None) -> list[AgentTool]:
    """Herramientas a dibujar en el grafo, para el quest dado (copia defensiva).

    Sin `quest_order` (o uno sin set propio) devuelve el catálogo completo —
    compatibilidad con cualquier consumidor sin selector. Con un quest conocido,
    filtra a sus tools preservando el orden declarado en `_TOOLS_BY_QUEST`.
    """
    by_name = {tool["name"]: tool for tool in AGENT_TOOLS}
    names = _TOOLS_BY_QUEST.get(quest_order) if quest_order is not None else None
    if names is None:
        return [dict(tool) for tool in AGENT_TOOLS]  # type: ignore[misc]
    return [dict(by_name[n]) for n in names if n in by_name]  # type: ignore[misc]
