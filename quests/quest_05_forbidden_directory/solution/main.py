"""
Quest 05 — El Directorio Prohibido

Archivo de Solución
A continuación se muestra el código completo con la solución para el archivo starter/main.py
Puedes usarlo como referencia para completar tu archivo starter/main.py,
pero te recomendamos intentar resolverlo por tu cuenta primero.
"""

from common.functions.get_files_info import get_valid_target_path
from common.utils.ui import show_quest_header, test, pass_test, fail_test

show_quest_header(
    "Quest 05 — El Directorio Prohibido",
    "El agente aprende los límites de su territorio.",
)

WORKING_DIRECTORY = (
    "quests/quest_05_forbidden_directory/workspace"
)

valid_paths = [
    ".",
    "src",
    "notes.txt",
]

invalid_paths = [
    "../",
    "../../secrets.txt",
]

for path in valid_paths:
    test(f"Validando ruta permitida: {path}")

    try:
        result = get_valid_target_path(
            WORKING_DIRECTORY,
            path,
        )

        pass_test(
            f"Ruta válida -> {result}"
        )

    except Exception as e:
        fail_test(
            f"Error inesperado: {e}"
        )

for path in invalid_paths:
    test(f"Validando ruta prohibida: {path}")

    try:
        result = get_valid_target_path(
            WORKING_DIRECTORY,
            path,
        )

        fail_test(
            f"Error esperado, pero se obtuvo ruta válida -> {result}"
        )

    except Exception as e:
        pass_test(
            f"Ruta bloqueada correctamente -> {e}"
        )