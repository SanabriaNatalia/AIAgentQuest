"""Pre-checks de Quest 03 — La Voz del Aprendiz.

Aparece argparse y mensajes estructurados con `types.Content`.
"""
from __future__ import annotations

from common.cli.helpers import starter_path
from common.cli.pre_checks._ast_helpers import (
    call_has_kwarg,
    has_call,
    has_import,
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
            "Importa argparse",
            has_import(tree, "argparse"),
        ),
        PreCheckResult(
            "Importa types desde google.genai",
            has_import(tree, "google.genai", "types"),
            "Q03 introduce `from google.genai import types`.",
        ),
        PreCheckResult(
            "Crea un ArgumentParser",
            has_call(tree, "argparse.ArgumentParser") or has_call(tree, "ArgumentParser"),
        ),
        PreCheckResult(
            "Registra el argumento user_prompt",
            regex_in_source(path, r"add_argument\(\s*['\"]user_prompt['\"]"),
            "Se espera `parser.add_argument(\"user_prompt\", ...)`.",
        ),
        PreCheckResult(
            "Construye un types.Content(role=\"user\", ...)",
            has_call(tree, "types.Content")
            and regex_in_source(path, r"role\s*=\s*['\"]user['\"]"),
        ),
        PreCheckResult(
            "Pasa contents=messages a generate_content",
            call_has_kwarg(tree, "client.models.generate_content", "contents"),
            "La llamada a generate_content debe usar `contents=messages`.",
        ),
    ]
