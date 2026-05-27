"""
Quest 08 — El Ciclo de la Manifestación

Archivo de Solución
"""

import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
# TODO 8.3:
from common.config import MAX_ITERS
from common.functions.call_function import available_functions, call_function
from common.prompts.system_prompt import system_prompt
from common.utils.ui import (
    show_quest_header,
    narrator,
    show_prompt,
    success,
)

show_quest_header(
    "Quest 08 — El Ciclo de la Manifestación",
    "El agente se manifiesta en un ciclo de acción, observación y reflexión.",
)

# TODO 8.0 — Preparación: código heredado del Quest 07.

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# ╔══════════════════════════════════════════════════════╗
# ║   NUEVO CONTENIDO DEL QUEST 08                       ║
# ╚══════════════════════════════════════════════════════╝

# TODO 8.1:
def main():
    if api_key is None:
        raise RuntimeError(
            "No se encontró GEMINI_API_KEY en el archivo .env"
        )

    parser = argparse.ArgumentParser(
        description="AI Agent Quest — Quest 08"
    )
    parser.add_argument("user_prompt", type=str, help="Prompt del usuario")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Muestra información detallada del agente",
    )

    args = parser.parse_args()

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

    messages = [
        types.Content(
            role="user",
            parts=[
                types.Part(text=args.user_prompt),
            ],
        )
    ]

    narrator("Recibiendo la voluntad del aprendiz...")
    show_prompt(args.user_prompt)

    # TODO 8.4:
    for _ in range(MAX_ITERS):
        try:
            final_response = generate_content(
                messages,
                args.verbose,
            )

            if final_response:
                success("Respuesta final recibida.")
                print("Final response:")
                print(final_response)
                return

        except Exception as e:
            print(f"Error in generate_content: {e}")

    # TODO 8.8:
    print(f"Maximum iterations ({MAX_ITERS}) reached.")

# TODO 8.2:
def generate_content(messages, verbose):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
            temperature=0,
        ),
    )

    usage = response.usage_metadata

    if usage is None:
        raise RuntimeError("No se recibió metadata de uso desde Gemini.")

    if verbose:
        print(f"Prompt tokens: {usage.prompt_token_count}")
        print(f"Response tokens: {usage.candidates_token_count}")

    # TODO 8.5:
    if response.candidates:
        for candidate in response.candidates:
            if candidate.content:
                messages.append(candidate.content)

    # TODO 8.6:
    if not response.function_calls:
        return response.text

    function_results = []

    for function_call in response.function_calls:
        function_call_result = call_function(
            function_call,
            verbose=verbose,
        )

        if not function_call_result.parts:
            raise RuntimeError(
                f"Empty function response for {function_call.name}"
            )

        part = function_call_result.parts[0]

        if part.function_response is None:
            raise RuntimeError(
                f"Function response is missing for {function_call.name}"
            )

        if part.function_response.response is None:
            raise RuntimeError(
                f"Function response content is missing for {function_call.name}"
            )

        function_results.append(part)

        if verbose:
            print(f"-> {part.function_response.response}")

    # TODO 8.7:
    messages.append(
        types.Content(
            role="tool",
            parts=function_results,
        )
    )

    return None

if __name__ == "__main__":
    main()