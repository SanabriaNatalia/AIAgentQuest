"""
Quest 08 — El Ciclo de la Manifestación

Objetivo:
Construir el primer agent loop iterativo
utilizando tool calls y observaciones.

Ejecutar desde la raíz del proyecto:

    uv run python -m quests.quest_08_manifesting_cycle.starter.main \
    "Lee notes.txt y dime qué contiene"

También puedes usar modo verbose:

    uv run python -m quests.quest_08_manifesting_cycle.starter.main \
    "Lee notes.txt y dime qué contiene" \
    --verbose

Una vez hayas terminado, valida tu solución ejecutando:

    uv run python -m quests.quest_08_manifesting_cycle.check
"""

import argparse
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from common.utils.ui import (
    show_quest_header,
    narrator,
    agent,
    success,
    show_prompt,
)

show_quest_header(
    "Quest 08 — El Ciclo de la Manifestación",
    "El agente se manifiesta en un ciclo de acción, observación y reflexión.",
)

# TODO 1:
# Copia tu solución del Quest 07 en este archivo.
#
# Puedes usar:
#
# quests/quest_07_agent_incarnation/solution/main.py
#
# o tu propia versión completada.
#
# No copies los imports ni la función show_quest_header,
# solo el código que va después.
#
# En este quest refactorizarás tu código, por lo que prepárate para 
# mover partes de tu solución a nuevas funciones.

# ============================================
# NUEVO CONTENIDO DEL QUEST 08
# ============================================


# TODO 2:
# Refactoriza tu archivo para que la lógica principal viva dentro de:
#
# def main():
#
# Dentro de main() deberían quedar:
#
# - validación de API key
# - creación del parser
# - lectura de args
# - creación de messages
# - agent loop

def main():
    pass

# TODO 3:
# Crea una función llamada:
#
# generate_content(messages, verbose)
#
# Esta función será responsable de:
#
# - llamar a Gemini
# - manejar function calls
# - ejecutar tools
# - agregar observaciones al historial
# - devolver respuestas finales

def generate_content(messages, verbose=False):
    pass


# TODO 4:
# Importa:
#
# MAX_ITERS
#
# desde:
#
# common.config
# 
# Preferiblemente al inicio de tu archivo, 
# junto con los otros imports.
#
# Este valor limitará la cantidad máxima
# de iteraciones del agente.


# TODO 5:
# Dentro de main(), crea un loop usando:
#
# for _ in range(MAX_ITERS):
#
# El loop debe:
#
# - ejecutar generate_content(messages, args.verbose)
# - imprimir la respuesta final si existe
# - terminar con return si el agente responde
# - continuar si el agente solo ejecutó tools


# TODO 6:
# Dentro de generate_content(...), cuando recibas response.candidates,
# agrega el content del modelo al historial:
#
# if response.candidates:
#     for candidate in response.candidates:
#         if candidate.content:
#             messages.append(candidate.content)


# TODO 7:
# Dentro de generate_content(...), si NO hay function calls:
#
# return response.text
#
# Esto romperá el loop principal.


# TODO 8:
# Después de ejecutar las tools, agrega sus resultados al historial:
#
# messages.append(
#     types.Content(
#         role="tool",
#         parts=function_results,
#     )
# )


# TODO 9:
# Si el agente alcanza MAX_ITERS sin respuesta final,
# imprime:
#
# Maximum iterations ({MAX_ITERS}) reached.
#
# Esto evitará loops infinitos en caso de que el agente no logre resolver la tarea.

if __name__ == "__main__":
    main()