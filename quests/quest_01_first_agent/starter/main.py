"""
Quest 01 — La Primera Invocación

Objetivo:
Enviar un mensaje a Gemini y mostrar la respuesta en la terminal.

Completa los TODOS en orden.
No borres el código existente, solo añádele lo que se pide en cada paso.

Puedes ejecutar el siguiente comando desde la raíz del proyecto 
para validar que funcione:

    uv run python -m quests.quest_01_first_agent.starter.main

Una vez que funcione, ejecuta el comando de check para validar tu solución:

    uv run python -m quests.quest_01_first_agent.check
"""

import os

from dotenv import load_dotenv
from google import genai

from common.utils.ui import (
    show_quest_header,
    narrator,
    agent,
    success,
)

show_quest_header(
    "Quest 01 — La Primera Invocación",
    "El laboratorio escucha tu primer llamado.",
)

# TODO 1:
# Carga las variables de entorno desde el archivo .env.
# Pista: usa load_dotenv().

# TODO 2:
# Lee la variable GEMINI_API_KEY desde el entorno.
# Pista: usa os.environ.get("GEMINI_API_KEY").


# TODO 3:
# Si api_key no existe, lanza un RuntimeError.
# Pista:
# if api_key is None:
#     raise RuntimeError("...")
# Asegúrate de incluir un mensaje claro indicando que no se 
# encontró la API key en el archivo .env.



success("API key encontrada.")

# TODO 4:
# Crea un cliente de Gemini usando la API key.
# Pista: genai.Client(api_key=api_key)



success("Cliente de Gemini inicializado.")

# TODO 5:
# Define un prompt fijo. 
# Solicita al modelo que explique qué es un agente IA en un párrafo corto.
prompt = ""

narrator("Enviando la primera invocación al modelo...")

# TODO 6:
# Usa client.models.generate_content() para enviar el prompt al modelo.
# Debe recibir:
# - model="gemini-2.5-flash"
# - contents=prompt
# Guarda la respuesta en la variable response.
response = None



success("Respuesta recibida.")

# Para acceder al texto de la respuesta, se usa response.text.
# El método agent() es solo para mostrar la respuesta en la terminal con formato.
agent(response.text)