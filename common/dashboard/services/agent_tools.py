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


def list_agent_tools() -> list[AgentTool]:
    """Devuelve el catálogo de herramientas del agente (copia defensiva)."""
    return [dict(tool) for tool in AGENT_TOOLS]  # type: ignore[misc]
