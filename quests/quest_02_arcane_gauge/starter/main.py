"""
Quest 02 — El Medidor Arcano

Objetivo:
Aprender a inspeccionar la metadata de uso de Gemini
para entender cuántos tokens consume una invocación.

En este Quest continuarás trabajando sobre el agente
que construiste en el Quest 01.

Ejecutar desde la raíz del proyecto:

    uv run python -m quests.quest_02_arcane_gauge.starter.main

Una vez que hayas terminado, valida tu solución ejecutando:

    uv run python -m quests.quest_02_arcane_gauge.check
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

# TODO 1:
# Copia tu solución del Quest 01 en este archivo. 
# No copies los imports ni la función show_quest_header, solo el código que va después.
#
# Puedes usar:
# - quests/quest_01_first_agent/solution/main.py o
# - tu propia versión completada.


# ============================================
# NUEVO CONTENIDO DEL QUEST 02
# ============================================

# TODO 2:
# Después de generar la respuesta, obtén la
# metadata de uso desde:
#
# response.usage_metadata
#
# Guárdala en una variable llamada `usage`.


# TODO 3:
# Verifica que `usage` no sea None.
# Si es None, lanza:
# RuntimeError(
#     "No se recibió metadata de uso desde Gemini."
# )


# TODO 4:
# Imprime los tokens consumidos usando:
# usage.prompt_token_count
# y:
# usage.candidates_token_count
#
# El formato esperado es:
# Prompt tokens: X
# Response tokens: Y


# TODO 5:
# Asegúrate de imprimir los tokens ANTES
# de mostrar la respuesta final del agente.