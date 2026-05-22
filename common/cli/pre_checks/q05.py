"""Pre-checks de Quest 05 — El Directorio Prohibido.

Q05 toca dos archivos: la función `get_valid_target_path` y el starter del
quest. Validamos pistas mínimas en ambos.
"""
from __future__ import annotations

from common.cli.helpers import REPO_ROOT, starter_path
from common.cli.pre_checks._ast_helpers import (
    has_call,
    parse_source,
    read_source,
    regex_in_source,
)
from common.cli.pre_checks.runner import PreCheckResult
from common.dashboard.services.quest_catalog import QuestMeta

VALIDATOR_PATH = REPO_ROOT / "common" / "functions" / "get_valid_target_path.py"


def checks(quest: QuestMeta) -> list[PreCheckResult]:
    starter = starter_path(quest)
    if not starter.exists():
        return [PreCheckResult("starter/main.py existe", False, f"No se encontró {starter}")]

    starter_tree = parse_source(starter)
    if starter_tree is None:
        return [PreCheckResult("Parsea como Python válido", False, "El starter tiene un SyntaxError.")]

    validator_source = read_source(VALIDATOR_PATH) or ""
    validator_tree = parse_source(VALIDATOR_PATH)
    validator_ok = validator_tree is not None

    return [
        PreCheckResult("starter/main.py existe", True),
        PreCheckResult("Parsea como Python válido", True),
        PreCheckResult(
            "get_valid_target_path.py parsea sin SyntaxError",
            validator_ok,
            "Revisa el archivo common/functions/get_valid_target_path.py.",
        ),
        PreCheckResult(
            "Usa os.path.abspath en el validador",
            validator_ok and (
                regex_in_source(VALIDATOR_PATH, r"os\.path\.abspath")
                or regex_in_source(VALIDATOR_PATH, r"\babspath\(")
            ),
            "Sin abspath no podrás comparar rutas absolutas.",
        ),
        PreCheckResult(
            "Verifica contención (commonpath / startswith)",
            validator_ok and (
                regex_in_source(VALIDATOR_PATH, r"os\.path\.commonpath")
                or regex_in_source(VALIDATOR_PATH, r"\bcommonpath\(")
                or regex_in_source(VALIDATOR_PATH, r"\.startswith\(")
            ),
            "Debes verificar que la ruta resuelta siga dentro del working dir.",
        ),
        PreCheckResult(
            "Los placeholders del validador fueron reemplazados",
            validator_ok and 'working_dir_abs = ""' not in validator_source,
            "Aún hay `working_dir_abs = \"\"` sin implementar.",
        ),
        PreCheckResult(
            "El starter invoca get_valid_target_path(...)",
            has_call(starter_tree, "get_valid_target_path"),
        ),
        PreCheckResult(
            "El starter usa pass_test y fail_test",
            regex_in_source(starter, r"\bpass_test\(")
            and regex_in_source(starter, r"\bfail_test\("),
            "Necesitas reportar éxito/fallo en cada ruta validada.",
        ),
    ]
