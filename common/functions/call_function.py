import os

from google.genai import types

from common.functions.get_files_info import schema_get_files_info, get_files_info
from common.functions.get_file_content import schema_get_file_content, get_file_content
from common.functions.write_file import schema_write_file, write_file
from common.functions.run_python_file import schema_run_python_file, run_python_file

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)

function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def call_function(function_call, verbose=False):
    if verbose:
        print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(f" - Calling function: {function_call.name}")

    function_name = function_call.name or ""

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


    return types.Content(
        role="tool",
        parts=[types.Part.from_function_response(
            name=function_name,
            response={"result": function_result},
        )],
    )
