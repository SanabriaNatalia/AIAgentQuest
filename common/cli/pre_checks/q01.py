"""Pre-checks de Quest 01 — La Primera Invocación.

Validamos el camino mínimo de una invocación a Gemini:
- carga de `.env`
- cliente `genai.Client`
- llamada a `generate_content`
- prompt no vacío
"""
from __future__ import annotations

import ast

from common.cli.helpers import starter_path
from common.cli.pre_checks._ast_helpers import (
    has_call,
    has_import,
    parse_source,
)
from common.cli.pre_checks.runner import PreCheckResult
from common.dashboard.services.quest_catalog import QuestMeta


def _prompt_assignment_is_nonempty(tree: ast.Module) -> bool:
    """True si alguna asignación top-level a `prompt` tiene un string no vacío
    o un valor no-constante (fstring, variable, expresión).

    Mira solo el `tree.body` (top-level del módulo) para no confundirse con
    cadenas que mencionen `prompt = ""` dentro de mensajes de error, docstrings
    o expresiones anidadas.
    """
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "prompt" for t in node.targets):
            continue
        value = node.value
        if isinstance(value, ast.Constant):
            if isinstance(value.value, str) and value.value.strip():
                return True
        else:
            # fstring, llamada, atributo, variable, etc. — asumimos válido.
            return True
    return False


def checks(quest: QuestMeta) -> list[PreCheckResult]:
    path = starter_path(quest)
    if not path.exists():
        return [PreCheckResult("starter/main.py existe", False, f"No se encontró {path}")]

    tree = parse_source(path)
    if tree is None:
        return [PreCheckResult("Parsea como Python válido", False, "El starter tiene un SyntaxError.")]

    results = [
        PreCheckResult("starter/main.py existe", True),
        PreCheckResult("Parsea como Python válido", True),
        PreCheckResult(
            "Importa load_dotenv",
            has_import(tree, "dotenv", "load_dotenv"),
            "Necesario para cargar GEMINI_API_KEY desde .env.",
        ),
        PreCheckResult(
            "Llama load_dotenv()",
            has_call(tree, "load_dotenv"),
            "Sin esta llamada, la API key nunca se carga al entorno.",
        ),
        PreCheckResult(
            "Importa genai",
            has_import(tree, "google", "genai") or has_import(tree, "google.genai"),
        ),
        PreCheckResult(
            "Construye un cliente genai.Client(...)",
            has_call(tree, "genai.Client"),
            "El cliente se crea con `genai.Client(api_key=...)`.",
        ),
        PreCheckResult(
            "Llama a client.models.generate_content(...)",
            has_call(tree, "client.models.generate_content"),
            "La invocación al modelo todavía no aparece en el código.",
        ),
        PreCheckResult(
            "Define un prompt no vacío",
            _prompt_assignment_is_nonempty(tree),
            "El placeholder `prompt = \"\"` debe reemplazarse por tu prompt.",
        ),
    ]
    return results
