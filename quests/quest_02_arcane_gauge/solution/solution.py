"""
Quest 02 — El Medidor Arcano

Archivo de Solución
A continuación se muestra el código completo con la solución para este quest.
Puedes usarlo como referencia para completar tu archivo starter/main.py,
pero te recomendamos intentar resolverlo por tu cuenta primero.

Ejecutar este archivo desde la raíz del proyecto usando:
    uv run python -m quests.quest_02_token_metadata.solution.solution
"""

# TODO 1:
# Copia tu solución del Quest 01 en este archivo.
#
# Puedes usar:
# - quests/quest_01_first_agent/solution/main.py o
# - tu propia versión completada.
"""
Quest 01 — La Primera Invocación

Archivo de Solución
A continuación se muestra el código completo con la solución para este quest.
Puedes usarlo como referencia para completar tu archivo starter/main.py,
pero te recomendamos intentar resolverlo por tu cuenta primero.
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
# Después de generar la respuesta, obtén la
# metadata de uso desde:
#
# response.usage_metadata
#
# Guárdala en una variable llamada `usage`.

usage = response.usage_metadata

# TODO 3:
# Verifica que `usage` no sea None.
# Si es None, lanza:
# RuntimeError(
#     "No se recibió metadata de uso desde Gemini."
# )

if usage is None:
    raise RuntimeError(
        "No se recibió metadata de uso desde Gemini."
    )

# TODO 4:
# Imprime los tokens consumidos usando:
# usage.prompt_token_count
# y:
# usage.candidates_token_count
#
# El formato esperado es:
# Prompt tokens: X
# Response tokens: Y
print(f"Prompt tokens: {usage.prompt_token_count}")
print(f"Response tokens: {usage.candidates_token_count}")

# TODO 5:
# Asegúrate de imprimir los tokens ANTES
# de mostrar la respuesta final del agente.
agent(response.text)








