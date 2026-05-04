from google.genai import types

# ============================================
# QUEST 06
# ============================================

# TODO 1 — Quest 06:
# Importa aquí los esquemas de todas las funciones que podrá usar el agente.
from common.functions.get_files_info import schema_get_files_info

# TODO 2 — Quest 06:
# Registra las herramientas disponibles para el agente.
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)

# ============================================
# QUEST 07
# ============================================

# TODO 1 — Quest 07:
# Importa aquí las 4 funciones reales que el agente podrá ejecutar.
#
# Necesitarás:
# - get_files_info
# - get_file_content
# - write_file
# - run_python_file
from common.functions.get_files_info import get_files_info

# TODO 2 — Quest 07:
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

    # TODO 3 — Quest 07:
    # Imprime la función solicitada.
    #
    # Si verbose=True, imprime:
    #
    # Calling function: {function_call.name}({function_call.args})
    #
    # Si verbose=False, imprime:
    #
    #  - Calling function: {function_call.name}

    # TODO 4 — Quest 07:
    # Guarda el nombre de la función en una variable llamada function_name.
    #
    # Pista:
    #
    # function_name = function_call.name or ""

    # TODO 5 — Quest 07:
    # Verifica si function_name existe en function_map.
    #
    # Si NO existe, retorna un types.Content con role="tool"
    # y un types.Part.from_function_response(...)
    #
    # La response debe ser:
    #
    # {"error": f"Unknown function: {function_name}"}

    # TODO 6 — Quest 07:
    # Copia los argumentos de function_call.
    #
    # Pista:
    #
    # args = dict(function_call.args) if function_call.args else {}

    # TODO 7 — Quest 07:
    # Inyecta el working_directory dentro de args.
    #
    # Usa:
    #
    # args["working_directory"] = "quests/quest_07_agent_embodiment/workspace"
    #
    # Recuerda:
    # El modelo NO debe controlar el working_directory.


    # TODO 8 — Quest 07:
    # Ejecuta la función real y guarda su resultado en una variable llamada function_result.
    #
    # Pista:
    #
    # function_result = function_map[function_name](**args)


    # TODO 9 — Quest 07:
    # Retorna un types.Content con role="tool"
    # y un types.Part.from_function_response(...)
    #
    # La response debe ser:
    #
    # {"result": function_result}