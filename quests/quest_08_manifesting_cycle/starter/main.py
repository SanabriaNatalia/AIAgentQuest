"""
Quest 08 — El Ciclo de la Manifestación

Objetivo:
Construir el primer agent loop iterativo
utilizando tool calls y observaciones.

Ejecutar desde la raíz del proyecto:

    arkanum run 8 "Los tests de calculator están fallando. Ayúdame a corregir el error."

También puedes usar modo verbose:

    arkanum run 8 "Los tests de calculator están fallando. Ayúdame a corregir el error." --verbose

Una vez hayas terminado, y el agente haya solucionado el bug,
valida tu solución ejecutando:

    arkanum check 8
"""

import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from common.config import MAX_ITERS
from common.functions.call_function import available_functions, call_function
from common.prompts.system_prompt import system_prompt
from common.tracing import emit_thought
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

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def main():
    if api_key is None:
        raise RuntimeError("No se encontró GEMINI_API_KEY en el archivo .env")

    parser = argparse.ArgumentParser(description="AI Agent Quest — Quest 08")
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
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
    ]

    narrator("Recibiendo la voluntad del aprendiz...")
    show_prompt(args.user_prompt)

    for _ in range(MAX_ITERS):
        try:
            final_response = generate_content(messages, args.verbose)
            if final_response:
                success("Respuesta final recibida.")
                print("Final response:")
                print(final_response)
                return
        except Exception as e:
            print(f"Error in generate_content: {e}")

    print(f"Maximum iterations ({MAX_ITERS}) reached.")


def generate_content(messages, verbose=False):
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

    if response.candidates:
        for candidate in response.candidates:
            if candidate.content:
                messages.append(candidate.content)

    # Pensamiento del agente: el texto que el modelo genera JUNTO a sus tool
    # calls (su razonamiento). El loop normalmente lo descarta; aquí lo
    # emitimos para que el visualizador lo muestre como `agent_thought`.
    # Leemos el texto parte por parte en vez de `response.text`: esa propiedad
    # avisa ("non-text parts in the response: ['function_call']") cuando la
    # respuesta mezcla texto + tool call. (best-effort: solo si el trace activo).
    thought = ""
    for candidate in (response.candidates or []):
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if getattr(part, "text", None):
                    thought += part.text
    thought = thought.strip()
    if thought and response.function_calls:
        emit_thought(thought)

    if not response.function_calls:
        return response.text

    function_results = []
    for function_call in response.function_calls:
        function_call_result = call_function(function_call, verbose=verbose)
        if not function_call_result.parts:
            raise RuntimeError(f"Empty function response for {function_call.name}")
        part = function_call_result.parts[0]
        if part.function_response is None:
            raise RuntimeError(f"Function response is missing for {function_call.name}")
        if part.function_response.response is None:
            raise RuntimeError(f"Function response content is missing for {function_call.name}")
        function_results.append(part)
        if verbose:
            print(f"-> {part.function_response.response}")

    messages.append(types.Content(role="tool", parts=function_results))
    return None



# TODO 8.9:
# Afina tu system prompt para el agent loop.
#
# El prompt minimalista del Quest 06 bastaba para tareas de un solo paso,
# pero aquí el agente ejecuta tareas de varios pasos. Vuelve a:
#
# common/prompts/system_prompt.py
#
# y mejora el `system_prompt` para guiar mejor el ciclo: pídele que razone
# paso a paso, que trabaje con rutas relativas (no debe especificar el
# working_directory) y que responda al usuario en español al terminar.
#
# Tienes un ejemplo en el README de este Quest (sección "Afina tu system
# prompt").
#
# Nota: `arkanum check 8` no valida el prompt directamente, pero verás la
# diferencia en el comportamiento del agente al correr `arkanum run 8 "..."`.


if __name__ == "__main__":
    main()
