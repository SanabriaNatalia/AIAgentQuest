"""Pre-checks de Quest 08 — El Ciclo de la Manifestación.

Refactor a `main()` + `generate_content(messages, verbose=False)`, loop sobre
`MAX_ITERS` y persistencia de observaciones con `role="tool"`.
"""
from __future__ import annotations

import ast

from common.cli.helpers import starter_path
from common.cli.pre_checks._ast_helpers import (
    has_call,
    has_for_range,
    has_function_def,
    has_import,
    parse_source,
    regex_in_source,
)
from common.cli.pre_checks.runner import PreCheckResult
from common.dashboard.services.quest_catalog import QuestMeta


def _function_has_body(tree: ast.AST, fn_name: str) -> bool:
    """¿`def fn_name` tiene un cuerpo no trivial (≠ solo `pass`)?"""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn_name:
            body = node.body
            if not body:
                return False
            if len(body) == 1 and isinstance(body[0], ast.Pass):
                return False
            return True
    return False


def checks(quest: QuestMeta) -> list[PreCheckResult]:
    starter = starter_path(quest)
    if not starter.exists():
        return [PreCheckResult("starter/main.py existe", False, f"No se encontró {starter}")]

    tree = parse_source(starter)
    if tree is None:
        return [PreCheckResult("Parsea como Python válido", False, "El starter tiene un SyntaxError.")]

    return [
        PreCheckResult("starter/main.py existe", True),
        PreCheckResult("Parsea como Python válido", True),
        PreCheckResult(
            "Importa MAX_ITERS desde common.config",
            has_import(tree, "common.config", "MAX_ITERS"),
        ),
        PreCheckResult(
            "Define main() con cuerpo",
            has_function_def(tree, "main") and _function_has_body(tree, "main"),
            "Tu lógica principal debe vivir dentro de `def main()`.",
        ),
        PreCheckResult(
            "Define generate_content(messages, verbose=False) con cuerpo",
            has_function_def(tree, "generate_content")
            and _function_has_body(tree, "generate_content"),
            "Q08 separa la llamada al modelo en `generate_content(...)`.",
        ),
        PreCheckResult(
            "Loop for _ in range(MAX_ITERS)",
            has_for_range(tree, "MAX_ITERS"),
            "El agent loop necesita `for _ in range(MAX_ITERS)`.",
        ),
        PreCheckResult(
            "Maneja límite de iteraciones",
            regex_in_source(starter, r"Maximum iterations"),
            "Recuerda imprimir `Maximum iterations ({MAX_ITERS}) reached.`",
        ),
        PreCheckResult(
            "Agrega observaciones de tools con role=\"tool\"",
            regex_in_source(starter, r"role\s*=\s*['\"]tool['\"]"),
            "Después de ejecutar tools, hay que apendear un Content con role=\"tool\".",
        ),
        PreCheckResult(
            "Conserva la llamada a generate_content desde main()",
            has_call(tree, "generate_content"),
        ),
    ]
