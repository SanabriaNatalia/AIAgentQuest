"""
Quest 07 — La Encarnación del Agente

Objetivo:
Ejecutar las herramientas solicitadas por el modelo
y convertir sus resultados en respuestas estructuradas.

⚠️ En este Quest todavía NO devolvemos los resultados de las tools al
modelo (eso lo harás en Q08, el agent loop). Aquí solo capturas los
resultados y los imprimes; el agente nunca llega a "responder la
pregunta" final. Por ejemplo, si preguntas "¿qué archivos hay?",
verás `Calling function: get_files_info(...)` y su resultado, pero NO
una respuesta en lenguaje natural como "hay 3 archivos: ...". Eso es
intencional. Q08 cierra el loop.

Ejecutar desde la raíz del proyecto:

    arkanum run 7 "¿Qué archivos hay en la raíz?"

También puedes usar modo verbose:

    arkanum run 7 "¿Qué archivos hay en la raíz?" --verbose

Una vez hayas terminado, valida tu solución ejecutando:

    arkanum check 7
"""

import argparse
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
# TODO 7.3:
from common.functions.call_function import available_functions, call_function
from common.prompts.system_prompt import system_prompt
from common.utils.ui import (
    show_quest_header,
    narrator,
    agent,
    success,
    show_prompt,
)

show_quest_header(
    "Quest 07 — La Encarnación del Agente",
    "El agente manifiesta su voluntad en el mundo.",
)

# TODO 7.0 — Preparación: código heredado del Quest 06.

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if api_key is None:
    raise RuntimeError(
        "No se encontró GEMINI_API_KEY en el archivo .env"
    )

success("API key encontrada.")

client = genai.Client(api_key=api_key)

success("Cliente de Gemini inicializado.")

parser = argparse.ArgumentParser(description="AI Agent Quest — Quest 07")
parser.add_argument("user_prompt", type=str, help="Prompt del usuario")
# TODO 7.2:
parser.add_argument(
    "--verbose",
    action="store_true",
    help="Muestra información detallada del agente",
)

args = parser.parse_args()

prompt = args.user_prompt

narrator("Recibiendo la solicitud del aprendiz...")
show_prompt(prompt)

messages = [
    types.Content(
        role="user",
        parts=[
            types.Part(text=prompt),
        ],
    )
]

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
    raise RuntimeError(
        "No se recibió metadata de uso desde Gemini."
    )

success("Respuesta recibida.")


# ╔══════════════════════════════════════════════════════╗
# ║   NUEVO CONTENIDO DEL QUEST 07                       ║
# ║   A partir de aquí, los TODOs son nuevos (7.x).      ║
# ╚══════════════════════════════════════════════════════╝

# TODO 7.2 (continuación):
if args.verbose:
    print(f"User prompt: {args.user_prompt}")
    print(f"Prompt tokens: {usage.prompt_token_count}")
    print(f"Response tokens: {usage.candidates_token_count}")

# TODO 7.4:
function_results = []

for function_call in response.function_calls or []:
    result = call_function(
        function_call,
        verbose=args.verbose,
    )

    if not result.parts:
        raise RuntimeError("Function call result has no parts")

    part = result.parts[0]

    if part.function_response is None:
        raise RuntimeError("Function response is missing")

    if part.function_response.response is None:
        raise RuntimeError("Function response content is missing")

    function_results.append(part)

    # TODO 7.5:
    if args.verbose:
        print(f"-> {part.function_response.response}")

if not function_results:
    agent(response.text)
