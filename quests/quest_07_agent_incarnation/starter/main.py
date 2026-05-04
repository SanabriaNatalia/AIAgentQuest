"""
Quest 07 — La Encarnación del Agente

Objetivo:
Ejecutar las herramientas solicitadas por el modelo
y convertir sus resultados en respuestas estructuradas.

Ejecutar desde la raíz del proyecto:

    uv run python -m quests.quest_07_agent_embodiment.starter.main \
    "¿Qué archivos hay en la raíz?"

También puedes usar modo verbose:

    uv run python -m quests.quest_07_agent_embodiment.starter.main \
    "¿Qué archivos hay en la raíz?" \
    --verbose

Una vez hayas terminado, valida tu solución ejecutando:

    uv run python -m quests.quest_07_agent_embodiment.check
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
    "Quest 07 — La Encarnación del Agente",
    "El agente manifiesta su voluntad en el mundo.",
)

# TODO 1:
# Copia tu solución del Quest 06 en este archivo.
#
# Puedes usar:
#
# quests/quest_06_tool_chest/solution/solution.py
#
# o tu propia versión completada.
#
# No copies los imports ni la función show_quest_header,
# solo el código que va después.


# ============================================
# NUEVO CONTENIDO DEL QUEST 07
# ============================================

# TODO 2:
# Abre:
#
# common/functions/call_function.py
#
# y completa TODOS los pasos del Quest 07.
#
# Allí construirás:
#
# - function_map
# - call_function()
#
# Esa función será responsable de:
# - ejecutar tools reales
# - inyectar working_directory
# - devolver respuestas estructuradas


# TODO 3:
# Agrega el flag:
#
# --verbose
#
# usando argparse.
#
# Pista:
#
# parser.add_argument(
#     "--verbose",
#     action="store_true",
#     help="Muestra información detallada del agente",
# )
#
# Cuando verbose esté activo,
# el programa deberá mostrar:
#
# - user prompt
# - token usage
# - resultados de tools
#
# Pista:
#
# if args.verbose:
#     print(...)

# TODO 4:
# Importa:
#
# call_function
#
# desde:
#
# common.functions.call_function
# 
# Preferiblemente, al inicio del archivo, junto con los otros imports.

# TODO 5:
# Reemplaza el print de function_calls
# por llamadas reales a:
#
# call_function(...)
#
# Debes:
#
# - iterar sobre response.function_calls
# - ejecutar cada tool usando call_function, es importante guardar su resultado en una variable (ej: result) para los siguientes pasos
# - valida result.parts (si no existe, lanza un error: Function call result has no parts)
# Obtén el primer part de la respuesta de la función (nuestras funciones solo retornan un part, así que no es necesario iterar sobre ellos)
# - validar:
#   - .function_response (si no existe, lanza un error: Function response is missing)
#   - .response dentro de .function_response (si no existe, lanza un error: Function response content is missing)
# - guardar resultados en function_results usando function_results.append(part)

# TODO 6:
# Si verbose=True,
# imprime el resultado de cada tool usando:
#
# print(
#     f"-> {result.parts[0].function_response.response}"
# )