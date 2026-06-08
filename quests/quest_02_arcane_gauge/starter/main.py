"""
Quest 02 — El Medidor Arcano

Objetivo:
Aprender a inspeccionar la metadata de uso de Gemini
para entender cuántos tokens consume una invocación.

En este Quest continuarás trabajando sobre el agente
que construiste en el Quest 01.

Ejecutar desde la raíz del proyecto:

    arkanum run 2

Una vez que hayas terminado, valida tu solución ejecutando:

    arkanum check 2
"""
import os

from dotenv import load_dotenv
from google import genai

from common.utils.ui import (
    show_quest_header,
    narrator,
    agent,
    success,
    show_prompt,
)

show_quest_header(
    "Quest 02 — El Medidor Arcano",
    "Es hora de conocer el costo de tus respuestas",
)

# TODO 2.0 — Preparación: código heredado del Quest 01.

# TODO 1.1:
load_dotenv()

# TODO 1.2:
api_key = os.environ.get("GEMINI_API_KEY")

# TODO 1.3:
if api_key is None:
    raise RuntimeError(
        "No se encontró GEMINI_API_KEY en el archivo .env"
    )

success("API key encontrada.")

# TODO 1.4:
client = genai.Client(api_key=api_key)

success("Cliente de Gemini inicializado.")

# TODO 1.5:
prompt = "Explícame qué es un agente IA en un párrafo corto."

narrator("Enviando la primera invocación al modelo...")
show_prompt(prompt)

# TODO 1.6:
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)
success("Respuesta recibida.")


# ╔══════════════════════════════════════════════════════╗
# ║   NUEVO CONTENIDO DEL QUEST 02                       ║
# ║   A partir de aquí, los TODOs son nuevos (2.x).      ║
# ╚══════════════════════════════════════════════════════╝

# TODO 2.1:
usage = response.usage_metadata

# TODO 2.2:
if usage is None:
    raise RuntimeError(
        "No se recibió metadata de uso desde Gemini."
    )

# TODO 2.3 / 2.4:
print(f"Prompt tokens: {usage.prompt_token_count}")
print(f"Response tokens: {usage.candidates_token_count}")

agent(response.text)
