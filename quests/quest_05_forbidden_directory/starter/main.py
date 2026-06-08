"""
Quest 05 — El Directorio Prohibido

Objetivo:
Construir la frontera de seguridad del agente validando
que las rutas permanezcan dentro del working directory.

En este Quest trabajarás en dos lugares:

1. Completar la función:

    common/functions/get_valid_target_path.py

2. Completar el manejo de errores en este archivo:

    quests/quest_05_forbidden_directory/starter/main.py

Ejecutar desde la raíz del proyecto:

    arkanum run 5

Una vez hayas terminado, valida tu solución ejecutando:

    arkanum check 5
"""

from common.functions.get_valid_target_path import get_valid_target_path
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

    # TODO 5.7:
    try:
        result = get_valid_target_path(
            WORKING_DIRECTORY,
            path,
        )

        pass_test(f"Ruta válida -> {result}")

    except Exception as e:
        fail_test(f"Error inesperado: {e}")

for path in invalid_paths:

    test(f"Validando ruta prohibida: {path}")

    # TODO 5.8:
    try:
        result = get_valid_target_path(
            WORKING_DIRECTORY,
            path,
        )

        fail_test("La ruta prohibida NO fue bloqueada")

    except Exception as e:
        pass_test(f"Ruta bloqueada correctamente -> {e}")
