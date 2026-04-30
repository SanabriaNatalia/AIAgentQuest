"""
Quest 01 — La Primera Invocación

Objetivo:
Enviar un mensaje a Gemini y mostrar la respuesta en la terminal.

Ejecutar desde la raíz del proyecto:

    uv run python quests/quest_01_first_agent/starter/main.py
"""

import os
from xmlrpc import client
from dotenv import load_dotenv
from google import genai
from rich.console import Console
from rich.panel import Panel
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
# Carga las variables de entorno desde el archivo .env.
# Pista: usa load_dotenv().



# TODO 2:
# Lee la variable GEMINI_API_KEY desde el entorno.
# Pista: usa os.environ.get("GEMINI_API_KEY").



# TODO 3:
# Si no existe api_key, lanza un RuntimeError con un mensaje claro.
# Pista:
# if api_key is None:
#     raise RuntimeError("...")
# El mensaje de error debe indicar que la clave no se encontró 
# y que se debe configurar en el archivo .env.



success("API key encontrada.")

# TODO 4:
# Crea un cliente de Gemini usando la API key.
# Pista: genai.Client(api_key=api_key)



# TODO 5:
# Define un prompt fijo.
# Puedes cambiarlo después, pero por ahora mantén uno simple.
# Es conveniente que añadas "máximo un párrafo" como condición 
# (para minimizar el consumo de tokens)
prompt = ""


narrator("Enviando la primera invocación al modelo...")
user_prompt(prompt)


# TODO 6:
# Usa client.models.generate_content() para enviar el prompt al modelo.
# Debe recibir:
# - model="gemini-2.5-flash"
# - contents=prompt
# No olvides guardar el resultado en la variable llamada response.
response = None


agent(response.text)