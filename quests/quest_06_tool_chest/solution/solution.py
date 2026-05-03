"""
Quest 06 — El Cofre de Instrumentos

Archivo de Solución
A continuación se muestra el código completo con la solución para este quest.
Puedes usarlo como referencia para completar tu archivo starter/main.py,
pero te recomendamos intentar resolverlo por tu cuenta primero.

Ejecutar este archivo desde la raíz del proyecto usando:

    uv run python -m quests.quest_06_tool_chest.solution.solution
"""

import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
# TODO 5
from common.functions.call_function import available_functions

from common.prompts.system_prompt import system_prompt
from common.utils.ui import (
    show_quest_header,
    narrator,
    agent,
    success,
    show_prompt,
)

show_quest_header(
    "Quest 06 — El Cofre de Instrumentos",
    "El agente descubre sus primeras herramientas.",
)

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if api_key is None:
    raise RuntimeError("No se encontró GEMINI_API_KEY en el archivo .env")

success("API key encontrada.")

client = genai.Client(api_key=api_key)

success("Cliente de Gemini inicializado.")

parser = argparse.ArgumentParser(description="AI Agent Quest — Quest 06")
parser.add_argument("user_prompt", type=str, help="Prompt del usuario")

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

# TODO 6:
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

success("Respuesta recibida.")

print(f"Prompt tokens: {usage.prompt_token_count}")
print(f"Response tokens: {usage.candidates_token_count}")

# TODO 7:
function_calls = response.function_calls

if function_calls:
    for function_call in function_calls:
        print(f"Calling function: {function_call.name}({function_call.args})")
else:
    agent(response.text)