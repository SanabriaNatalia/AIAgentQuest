from google.genai import types

# ╔══════════════════════════════════════════════════════╗
# ║   QUEST 06 — Registro de herramientas (TODO 6.3)     ║
# ╚══════════════════════════════════════════════════════╝

# TODO 6.3 (call_function.py, paso 1):
# Importa aquí los esquemas de todas las funciones que podrá usar el agente.
from common.functions.get_files_info import schema_get_files_info

# TODO 6.3 (call_function.py, paso 2):
# Registra las herramientas disponibles para el agente.
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)

# ╔══════════════════════════════════════════════════════╗
# ║   QUEST 07 — Ejecución de herramientas (TODO 7.1)    ║
# ╚══════════════════════════════════════════════════════╝

# TODO 7.1 (call_function.py, paso 1):
# Importa aquí las 4 funciones reales que el agente podrá ejecutar.
#
# Necesitarás:
# - get_files_info
# - get_file_content
# - write_file
# - run_python_file
from common.functions.get_files_info import get_files_info

# TODO 7.1 (call_function.py, paso 2):
# Completa el diccionario function_map que relaciona el nombre de cada función
# con la función real de Python.
function_map = {
    "get_files_info": get_files_info,
}

def call_function(function_call, verbose=False):
    """
    Ejecuta una herramienta solicitada por el modelo.
    Recibe un FunctionCall de Gemini y devuelve un
    types.Content con el resultado de la función.
    """

    # TODO 7.1 (call_function.py, paso 3):
    # Imprime la función solicitada.
    #
    # Si verbose=True, imprime:
    #
    # Calling function: {function_call.name}({function_call.args})
    #
    # Si verbose=False, imprime:
    #
    #  - Calling function: {function_call.name}

    # TODO 7.1 (call_function.py, paso 4):
    # Guarda el nombre de la función en una variable llamada function_name.
    #
    # Pista:
    #
    # function_name = function_call.name or ""

    # TODO 7.1 (call_function.py, paso 5):
    # Verifica si function_name existe en function_map.
    #
    # Si NO existe, retorna un types.Content con role="tool"
    # y un types.Part.from_function_response(...)
    #
    # La response debe ser:
    #
    # {"error": f"Unknown function: {function_name}"}

    # TODO 7.1 (call_function.py, paso 6):
    # Copia los argumentos de function_call.
    #
    # Pista:
    #
    # args = dict(function_call.args) if function_call.args else {}

    # TODO 7.1 (call_function.py, paso 7):
    # Inyecta el working_directory dentro de args.
    #
    # El CLI (`arkanum run/check`) te pasa el workspace correcto vía
    # la variable de entorno `ARKANUM_WORKSPACE`. Léela con fallback al
    # workspace de Q07 por si corres el módulo directamente con `python -m`.
    #
    # Usa (recordá `import os` arriba si hace falta):
    #
    # args["working_directory"] = os.environ.get(
    #     "ARKANUM_WORKSPACE",
    #     "quests/quest_07_agent_incarnation/workspace",
    # )
    #
    # Recuerda:
    # El modelo NO debe controlar el working_directory.


    # TODO 7.1 (call_function.py, paso 8):
    # Ejecuta la función real y guarda su resultado en una variable llamada function_result.
    #
    # Pista:
    #
    # function_result = function_map[function_name](**args)


    # TODO 7.1 (call_function.py, paso 9):
    # Retorna un types.Content con role="tool"
    # y un types.Part.from_function_response(...)
    #
    # La response debe ser:
    #
    # {"result": function_result}