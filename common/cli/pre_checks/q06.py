"""Pre-checks de Quest 06 — El Cofre de Instrumentos.

Q06 requiere:
- 4 schemas (get_files_info ya viene, faltan los otros 3).
- `available_functions = types.Tool(...)` con las 4 declaraciones.
- En el starter: `tools=[available_functions]` y manejo de `response.function_calls`.
- system_prompt.py actualizado con el agente de herramientas.
"""
from __future__ import annotations

from common.cli.helpers import REPO_ROOT, starter_path
from common.cli.pre_checks._ast_helpers import (
    call_has_kwarg,
    has_attribute_access,
    has_call,
    has_import,
    parse_source,
    read_source,
    regex_in_source,
)
from common.cli.pre_checks.runner import PreCheckResult
from common.dashboard.services.quest_catalog import QuestMeta

CALL_FN_PATH = REPO_ROOT / "common" / "functions" / "call_function.py"
SYSTEM_PROMPT_PATH = REPO_ROOT / "common" / "prompts" / "system_prompt.py"
SCHEMAS_NEEDED = {
    "schema_get_file_content": REPO_ROOT / "common" / "functions" / "get_file_content.py",
    "schema_write_file": REPO_ROOT / "common" / "functions" / "write_file.py",
    "schema_run_python_file": REPO_ROOT / "common" / "functions" / "run_python_file.py",
}


def checks(quest: QuestMeta) -> list[PreCheckResult]:
    starter = starter_path(quest)
    if not starter.exists():
        return [PreCheckResult("starter/main.py existe", False, f"No se encontró {starter}")]

    starter_tree = parse_source(starter)
    if starter_tree is None:
        return [PreCheckResult("Parsea como Python válido", False, "El starter tiene un SyntaxError.")]

    call_fn_source = read_source(CALL_FN_PATH) or ""
    sp_source = read_source(SYSTEM_PROMPT_PATH) or ""

    results: list[PreCheckResult] = [
        PreCheckResult("starter/main.py existe", True),
        PreCheckResult("Parsea como Python válido", True),
    ]

    for schema_var, schema_path in SCHEMAS_NEEDED.items():
        present = regex_in_source(schema_path, rf"{schema_var}\s*=\s*types\.FunctionDeclaration")
        results.append(
            PreCheckResult(
                f"{schema_var} definido como FunctionDeclaration",
                present,
                f"Falta declarar {schema_var} en {schema_path.relative_to(REPO_ROOT)}.",
            )
        )

    declarations_count = call_fn_source.count("schema_")
    results.append(
        PreCheckResult(
            "call_function.py registra los 4 schemas",
            # Al menos 4 referencias a `schema_` (import + lista), conservador:
            # damos por bueno si aparece ≥ 5 (4 declarations + 4 imports = 8).
            declarations_count >= 5,
            "El `available_functions = types.Tool(...)` debe contener los 4 schemas.",
        )
    )

    results.extend([
        PreCheckResult(
            "Importa available_functions",
            has_import(starter_tree, "common.functions.call_function", "available_functions"),
            "Falta `from common.functions.call_function import available_functions`.",
        ),
        PreCheckResult(
            "Pasa tools= a GenerateContentConfig",
            call_has_kwarg(starter_tree, "types.GenerateContentConfig", "tools"),
            "Recuerda agregar `tools=[available_functions]` dentro del config.",
        ),
        PreCheckResult(
            "Itera sobre response.function_calls",
            has_attribute_access(starter_tree, "response.function_calls"),
            "El starter debe revisar `response.function_calls`.",
        ),
        PreCheckResult(
            'Imprime "Calling function:" en el flujo de tools',
            regex_in_source(starter, r"Calling function:"),
        ),
        PreCheckResult(
            "system_prompt.py menciona herramientas / tools",
            "herramientas" in sp_source.lower() or "tools" in sp_source.lower(),
            "El system prompt todavía es el placeholder inicial.",
        ),
    ])

    return results
