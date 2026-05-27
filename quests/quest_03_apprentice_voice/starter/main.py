"""
Quest 03 — La Voz del Aprendiz

Objetivo:
Permitir que el usuario envíe prompts desde la terminal
y convertir esos prompts en mensajes estructurados.

En este Quest continuarás trabajando sobre el agente
construido en el Quest 02.

Ejecutar desde la raíz del proyecto:

    uv run python -m quests.quest_03_user_input.starter.main "¿Qué es un agente IA?"

Una vez que hayas terminado, valida tu solución ejecutando:

    uv run python -m quests.quest_03_apprentice_voice.check
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
    "Quest 03 — La Voz del Aprendiz",
    "Atrás quedó el código rígido. Es hora de escuchar tu voz.",
)


# TODO 3.0 — Preparación:
# Copia tu solución del Quest 02 en este archivo.
# No copies los imports ni la función show_quest_header, solo el código que va después.
# Lo que pegues conservará sus etiquetas TODO 1.x y 2.x — esos pasos ya los resolviste.
#
# Puedes usar:
# - quests/quest_02_arcane_gauge/solution/solution.py, o
# - tu propia versión completada.


# ╔══════════════════════════════════════════════════════╗
# ║   NUEVO CONTENIDO DEL QUEST 03                       ║
# ║   A partir de aquí, los TODOs son nuevos (3.x).      ║
# ╚══════════════════════════════════════════════════════╝

# TODO 3.1:
# Importa argparse al inicio del archivo (junto a los demás imports).
# Lo utilizaremos para recibir prompts desde consola.


# TODO 3.2:
# Importa `types` al inicio del archivo (junto a los demás imports):
#
# from google.genai import types
#
# Los modelos conversacionales trabajan con mensajes
# estructurados en lugar de strings simples.


# TODO 3.3:
# Reemplaza el prompt hardcoded utilizando argparse.
#
# El programa debe aceptar un argumento llamado:
#
# user_prompt
#
# Ejemplo:
#
# uv run python -m quests.quest_03_apprentice_voice.starter.main \
# "¿Qué es un agente IA?"


# TODO 3.4:
# Reemplaza:
#
# prompt = ...
#
# por:
#
# prompt = args.user_prompt
#
# para utilizar el prompt enviado desde terminal.


# TODO 3.5:
# Crea una lista llamada `messages`.
#
# Debe contener un único mensaje con:
#
# role="user"
#
# y:
#
# types.Part(text=prompt)
#
# Pista:
#
# messages = [
#     types.Content(
#         role="user",
#         parts=[
#             types.Part(text=prompt)
#         ]
#     )
# ]


# TODO 3.6:
# Reemplaza:
#
# contents=prompt
#
# por:
#
# contents=messages
#
# en la llamada a generate_content().


# TODO 3.7:
# Mantén funcionando el medidor de tokens
# del Quest 02.
#
# El programa debe seguir mostrando:
#
# Prompt tokens: X
# Response tokens: Y


# TODO 3.8:
# Ejecuta el programa usando distintos prompts
# desde terminal.
#
# Ejemplo:
#
# uv run python -m quests.quest_03_apprentice_voice.starter.main \
# "Explícame qué es RAG en un párrafo"