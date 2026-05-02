"""
Quest 04 — Las Leyes del Arkanum

Archivo de Solución
A continuación se muestra el código completo con la solución para este quest.
Puedes usarlo como referencia para completar tu archivo starter/main.py,
pero te recomendamos intentar resolverlo por tu cuenta primero.

Ejecutar este archivo desde la raíz del proyecto usando:

    uv run python -m quests.quest_04_arkanum_laws.solution.solution
"""

import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

# TODO 3:
from common.prompts.system_prompt import system_prompt
from common.utils.ui import (
    show_quest_header,
    narrator,
    agent,
    success,
    show_prompt,
)

show_quest_header(
    "Quest 04 — Las Leyes del Arkanum",
    "Las leyes del Arkanum son absolutas.",
)

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if api_key is None:
    raise RuntimeError("No se encontró GEMINI_API_KEY en el archivo .env")

success("API key encontrada.")

client = genai.Client(api_key=api_key)

success("Cliente de Gemini inicializado.")

parser = argparse.ArgumentParser(description="AI Agent Quest — Quest 04")
parser.add_argument("user_prompt", type=str, help="Prompt del usuario")

args = parser.parse_args()

prompt = args.user_prompt

narrator("Recibiendo la voz del aprendiz...")
show_prompt(prompt)

messages = [
    types.Content(
        role="user",
        parts=[
            types.Part(text=prompt),
        ],
    )
]

# TODO 5 y TODO 6:
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=messages,
    config=types.GenerateContentConfig(
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

agent(response.text)