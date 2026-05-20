"""Pre-checks de Quest 07 — La Encarnación del Agente.

Q07 cablea `call_function` y el flag `--verbose`. Validamos:
- function_map con las 4 funciones reales.
- call_function devuelve types.Content con role="tool".
- Starter importa `call_function`, agrega `--verbose`, llama
  `call_function(...)` y arma `function_results`.
"""
from __future__ import annotations

from common.cli.helpers import REPO_ROOT, starter_path
from common.cli.pre_checks._ast_helpers import (
    has_call,
    has_import,
    parse_source,
    read_source,
    regex_in_source,
)
from common.cli.pre_checks.runner import PreCheckResult
from common.dashboard.services.quest_catalog import QuestMeta

CALL_FN_PATH = REPO_ROOT / "common" / "functions" / "call_function.py"


def checks(quest: QuestMeta) -> list[PreCheckResult]:
    starter = starter_path(quest)
    if not starter.exists():
        return [PreCheckResult("starter/main.py existe", False, f"No se encontró {starter}")]

    starter_tree = parse_source(starter)
    if starter_tree is None:
        return [PreCheckResult("Parsea como Python válido", False, "El starter tiene un SyntaxError.")]

    call_fn_source = read_source(CALL_FN_PATH) or ""

    # Aproximación: contamos cuántos nombres reales aparecen en function_map.
    real_fn_names = ("get_files_info", "get_file_content", "write_file", "run_python_file")
    mapped = sum(1 for fn in real_fn_names if f'"{fn}"' in call_fn_source or f"'{fn}'" in call_fn_source)

    return [
        PreCheckResult("starter/main.py existe", True),
        PreCheckResult("Parsea como Python válido", True),
        PreCheckResult(
            "function_map contiene las 4 funciones",
            mapped >= 4,
            f"Sólo se detectaron {mapped}/4 entries en function_map.",
        ),
        PreCheckResult(
            "call_function devuelve types.Content con role=\"tool\"",
            regex_in_source(CALL_FN_PATH, r"role\s*=\s*['\"]tool['\"]")
            and regex_in_source(CALL_FN_PATH, r"types\.Content"),
            "La función debe construir un `types.Content(role=\"tool\", ...)`.",
        ),
        PreCheckResult(
            "call_function usa Part.from_function_response",
            regex_in_source(CALL_FN_PATH, r"Part\.from_function_response"),
        ),
        PreCheckResult(
            "Importa call_function en el starter",
            has_import(starter_tree, "common.functions.call_function", "call_function"),
        ),
        PreCheckResult(
            "Agrega flag --verbose con argparse",
            regex_in_source(starter, r"add_argument\(\s*['\"]--verbose['\"]"),
        ),
        PreCheckResult(
            "Llama call_function(...) sobre las function_calls",
            has_call(starter_tree, "call_function"),
        ),
        PreCheckResult(
            "Acumula resultados en function_results",
            regex_in_source(starter, r"function_results\s*\.\s*append\("),
            "Recuerda `function_results.append(part)` por cada tool ejecutada.",
        ),
    ]
