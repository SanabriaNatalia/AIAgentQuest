"""Pre-checks de Quest 02 — El Medidor Arcano.

Suma a Q01 la lectura de `response.usage_metadata` y la impresión de los
tokens consumidos.
"""
from __future__ import annotations

from common.cli.helpers import starter_path
from common.cli.pre_checks._ast_helpers import (
    has_attribute_access,
    has_call,
    parse_source,
    regex_in_source,
)
from common.cli.pre_checks.runner import PreCheckResult
from common.dashboard.services.quest_catalog import QuestMeta


def checks(quest: QuestMeta) -> list[PreCheckResult]:
    path = starter_path(quest)
    if not path.exists():
        return [PreCheckResult("starter/main.py existe", False, f"No se encontró {path}")]

    tree = parse_source(path)
    if tree is None:
        return [PreCheckResult("Parsea como Python válido", False, "El starter tiene un SyntaxError.")]

    return [
        PreCheckResult("starter/main.py existe", True),
        PreCheckResult("Parsea como Python válido", True),
        PreCheckResult(
            "Conserva la invocación de Q01 (generate_content)",
            has_call(tree, "client.models.generate_content"),
            "Recuerda copiar tu solución de Q01 antes de añadir el medidor.",
        ),
        PreCheckResult(
            "Lee response.usage_metadata",
            has_attribute_access(tree, "response.usage_metadata"),
            "Sin este acceso no podrás obtener los tokens consumidos.",
        ),
        PreCheckResult(
            'Imprime "Prompt tokens:"',
            regex_in_source(path, r"Prompt tokens:"),
            "Q02 espera el formato literal `Prompt tokens: X`.",
        ),
        PreCheckResult(
            'Imprime "Response tokens:"',
            regex_in_source(path, r"Response tokens:"),
            "Q02 espera el formato literal `Response tokens: Y`.",
        ),
        PreCheckResult(
            "Accede a prompt_token_count",
            regex_in_source(path, r"prompt_token_count"),
        ),
        PreCheckResult(
            "Accede a candidates_token_count",
            regex_in_source(path, r"candidates_token_count"),
        ),
    ]
