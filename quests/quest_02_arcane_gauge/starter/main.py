"""
Quest 02 — El Medidor Arcano

Objetivo:
Aprender a inspeccionar la metadata de uso de Gemini
para entender cuántos tokens consume una invocación.

En este Quest continuarás trabajando sobre el agente
que construiste en el Quest 01.

Ejecutar desde la raíz del proyecto:

    arkanum start 2

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
)

show_quest_header(
    "Quest 02 — El Medidor Arcano",
    "Es hora de conocer el costo de tus respuestas",
)

# TODO 2.0 — Preparación:
# Copia tu solución del Quest 01 en este archivo.
# No copies los imports ni la función show_quest_header, solo el código que va después.
# Lo que pegues conservará sus etiquetas TODO 1.1 … TODO 1.6
# (esos pasos ya los resolviste; son el cimiento sobre el que construyes).
#
# Puedes usar:
# - quests/quest_01_first_invocation/solution/solution.py, o
# - tu propia versión completada.


# ╔══════════════════════════════════════════════════════╗
# ║   NUEVO CONTENIDO DEL QUEST 02                       ║
# ║   A partir de aquí, los TODOs son nuevos (2.x).      ║
# ╚══════════════════════════════════════════════════════╝

# TODO 2.1:
# Después de generar la respuesta, obtén la
# metadata de uso desde:
#
# response.usage_metadata
#
# Guárdala en una variable llamada `usage`.


# TODO 2.2:
# Verifica que `usage` no sea None.
# Si es None, lanza:
# RuntimeError(
#     "No se recibió metadata de uso desde Gemini."
# )


# TODO 2.3:
# Imprime los tokens consumidos usando:
# usage.prompt_token_count
# y:
# usage.candidates_token_count
#
# El formato esperado es:
# Prompt tokens: X
# Response tokens: Y


# TODO 2.4:
# Asegúrate de imprimir los tokens ANTES
# de mostrar la respuesta final del agente.