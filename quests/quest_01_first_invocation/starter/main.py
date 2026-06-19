"""
Quest 01 — La Primera Invocación

Objetivo:
Enviar un mensaje a Gemini y mostrar la respuesta en la terminal.

Completa los TODOS en orden.
No borres el código existente, solo añádele lo que se pide en cada paso.

Puedes ejecutar el siguiente comando desde la raíz del proyecto
para validar que funcione:

    arkanum run 1

Una vez que funcione, ejecuta el comando de check para validar tu solución:

    arkanum check 1
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
    "Quest 01 — La Primera Invocación",
    "El laboratorio escucha tu primer llamado.",
)

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

# Para acceder al texto de la respuesta, se usa response.text.
# El método agent() es solo para mostrar la respuesta en la terminal con formato.
agent(response.text)
