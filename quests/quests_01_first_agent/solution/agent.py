"""
Quest 01 — La Primera Invocación

Objetivo:
Enviar un mensaje a Gemini y mostrar la respuesta en la terminal.

Ejecutar desde la raíz del proyecto:

    uv run python quests/quest_01_first_agent/starter/main.py
"""

import os

from dotenv import load_dotenv
from google import genai
from common.utils.ui import (
    show_quest_header,
    narrator,
    agent,
    success,
    user_prompt
)

show_quest_header(
    "Quest 01 — La Primera Invocación",
    "El laboratorio escucha tu primer llamado.",
)

# TODO 1:
load_dotenv()

# TODO 2:
api_key = os.environ.get("GEMINI_API_KEY")

# TODO 3:
if api_key is None:
    raise RuntimeError(
        "No se encontró GEMINI_API_KEY en el archivo .env"
    )

success("API key encontrada.")

# TODO 4:
client = genai.Client(api_key=api_key)

success("Cliente de Gemini inicializado.")

# TODO 5:
prompt = "Explícame qué es un agente IA en un párrafo corto."

narrator("Enviando la primera invocación al modelo...")
user_prompt(prompt)

# TODO 6:
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

success("Respuesta recibida.")

agent(response.text)