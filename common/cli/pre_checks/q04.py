"""Pre-checks de Quest 04 — Las Leyes del Arkanum.

Verifica que el system prompt fue movido y conectado vía
`types.GenerateContentConfig(system_instruction=...)` con `temperature=0`.
"""
from __future__ import annotations

from common.cli.helpers import REPO_ROOT, starter_path
from common.cli.pre_checks._ast_helpers import (
    call_has_kwarg,
    has_call,
    has_import,
    parse_source,
    read_source,
    regex_in_source,
)
from common.cli.pre_checks.runner import PreCheckResult
from common.dashboard.services.quest_catalog import QuestMeta

SYSTEM_PROMPT_PATH = REPO_ROOT / "common" / "prompts" / "system_prompt.py"

# Texto literal que el starter pide pegar (sin barras invertidas ni mayúsculas
# extra). Si el aprendiz mantiene la frase clave, asumimos que el archivo fue
# editado correctamente.
EXPECTED_FRAGMENT = "LAS LEYES DEL ARKANUM SON ABSOLUTAS"


def checks(quest: QuestMeta) -> list[PreCheckResult]:
    path = starter_path(quest)
    if not path.exists():
        return [PreCheckResult("starter/main.py existe", False, f"No se encontró {path}")]

    tree = parse_source(path)
    if tree is None:
        return [PreCheckResult("Parsea como Python válido", False, "El starter tiene un SyntaxError.")]

    sp_source = read_source(SYSTEM_PROMPT_PATH) or ""

    return [
        PreCheckResult("starter/main.py existe", True),
        PreCheckResult("Parsea como Python válido", True),
        PreCheckResult(
            "Conserva la base de Q03 (argparse)",
            has_import(tree, "argparse"),
            "Recuerda copiar tu solución de Q03 antes de las leyes.",
        ),
        PreCheckResult(
            "Importa system_prompt",
            has_import(tree, "common.prompts.system_prompt", "system_prompt"),
            "Falta `from common.prompts.system_prompt import system_prompt`.",
        ),
        PreCheckResult(
            "system_prompt.py contiene la frase clave",
            EXPECTED_FRAGMENT in sp_source,
            "El archivo common/prompts/system_prompt.py todavía no fue actualizado.",
        ),
        PreCheckResult(
            "Usa types.GenerateContentConfig",
            has_call(tree, "types.GenerateContentConfig"),
        ),
        PreCheckResult(
            "Pasa system_instruction=system_prompt",
            call_has_kwarg(tree, "types.GenerateContentConfig", "system_instruction"),
        ),
        PreCheckResult(
            "Configura temperature=0",
            regex_in_source(path, r"temperature\s*=\s*0(?!\.\d*[1-9])"),
            "Q04 pide `temperature=0` para respuestas estables.",
        ),
    ]
