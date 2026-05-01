"""
Quest 02 — El Medidor Arcano

Archivo de Solución
A continuación se muestra el código completo con la solución para este quest.
Puedes usarlo como referencia para completar tu archivo starter/main.py,
pero te recomendamos intentar resolverlo por tu cuenta primero.

Ejecutar este archivo desde la raíz del proyecto usando:
    uv run python -m quests.quest_02_arcane_gauge.solution.solution
"""

import os

from dotenv import load_dotenv
from google import genai

from common.utils.ui import (
    show_quest_header,
    narrator,
    agent,
    success,
    show_prompt
)

show_quest_header(
    "Quest 02 — El Medidor Arcano",
    "Es hora de conocer el costo de tus respuestas",
)

# TODO 1:

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if api_key is None:
    raise RuntimeError(
        "No se encontró GEMINI_API_KEY en el archivo .env"
    )

success("API key encontrada.")

client = genai.Client(api_key=api_key)

success("Cliente de Gemini inicializado.")

prompt = "Explícame qué es un agente IA en un párrafo corto."

narrator("Enviando la primera invocación al modelo...")
show_prompt(prompt)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)
success("Respuesta recibida.")

# TODO 2:
usage = response.usage_metadata

# TODO 3:
if usage is None:
    raise RuntimeError(
        "No se recibió metadata de uso desde Gemini."
    )

# TODO 4:
print(f"Prompt tokens: {usage.prompt_token_count}")
print(f"Response tokens: {usage.candidates_token_count}")

# TODO 5:

agent(response.text)








