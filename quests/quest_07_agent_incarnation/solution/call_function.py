from google.genai import types

from common.functions.get_files_info import get_files_info
from common.functions.get_file_content import get_file_content
from common.functions.write_file import write_file
from common.functions.run_python_file import run_python_file


function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def call_function(function_call, verbose=False):
    """
    Ejecuta una tool solicitada por el modelo.

    Recibe un FunctionCall de Gemini y devuelve un
    types.Content con el resultado de la función.
    """

    if verbose:
        print(
            f"Calling function: "
            f"{function_call.name}({function_call.args})"
        )
    else:
        print(f" - Calling function: {function_call.name}")

    function_name = function_call.name or ""

    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={
                        "error": (
                            f"Unknown function: {function_name}"
                        )
                    },
                )
            ],
        )

    args = dict(function_call.args) if function_call.args else {}

    args["working_directory"] = (
        "quests/quest_07_agent_embodiment/workspace"
    )

    function_result = function_map[function_name](**args)

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={
                    "result": function_result
                },
            )
        ],
    )