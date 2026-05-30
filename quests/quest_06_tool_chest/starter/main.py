"""
Quest 06 — El Cofre de Instrumentos

Objetivo:
Registrar herramientas disponibles para que el modelo pueda
solicitar function calls.

Ejecutar desde la raíz del proyecto:

    arkanum start 6 "¿Qué archivos hay en la raíz?"

Una vez hayas terminado, valida tu solución ejecutando:

    arkanum check 6
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
    "Quest 06 — El Cofre de Instrumentos",
    "El agente descubre sus primeras herramientas.",
)

# TODO 6.0 — Preparación:
# Copia tu solución del Quest 04 en este archivo.
# No copies los imports ni la función show_quest_header, solo el código que va después.
# Lo que pegues conservará sus etiquetas TODO 1.x … 4.x — esos pasos ya los resolviste.
#
# Puedes usar:
# - quests/quest_04_arkanum_laws/solution/solution.py, o
# - tu propia versión completada.


# ╔══════════════════════════════════════════════════════╗
# ║   NUEVO CONTENIDO DEL QUEST 06                       ║
# ║   A partir de aquí, los TODOs son nuevos (6.x).      ║
# ╚══════════════════════════════════════════════════════╝

# TODO 6.1:
# Abre el archivo:
#
# common/prompts/system_prompt.py
#
# y modifica la variable `system_prompt`
# para que contenga un prompt de agente de herramientas.
#
# Usa este texto:
#
# """
# Eres un agente de IA especializado en programación.
#
# Cuando el usuario haga una pregunta o solicitud,
# debes crear un plan de uso de herramientas.
#
# Puedes realizar las siguientes operaciones:
#
# - Listar archivos y directorios
# - Leer contenido de archivos
# - Escribir archivos
# - Ejecutar archivos Python
# """

# TODO 6.2:
# Completa los schemas faltantes en:
#
# common/functions/get_file_content.py
# common/functions/write_file.py
# common/functions/run_python_file.py
#
# (en cada uno verás el marcador `TODO 6.2`).
#
# Usa como referencia el schema ya existente en:
#
# common/functions/get_files_info.py
#
# También puedes revisar esta entrada del códice:
# docs/agents/tool_schemas.md

# TODO 6.3:
# Abre:
#
# common/functions/call_function.py
#
# y registra todas las herramientas disponibles en:
#
# available_functions = types.Tool(
#     function_declarations=[
#         ...
#     ]
# )

# TODO 6.4:
# Importa:
#
# available_functions
#
# desde:
#
# common.functions.call_function
#
# Preferiblemente, al inicio del archivo, junto con los otros imports.

# TODO 6.5:
# En la llamada a:
#
# client.models.generate_content(...)
#
# agrega las herramientas dentro de GenerateContentConfig:
#
# config=types.GenerateContentConfig(
#     tools=[available_functions], <-- Agrega esta línea
#     system_instruction=system_prompt,
#     temperature=0,
# )

# TODO 6.6:
# Después de recibir la respuesta, revisa:
#
# response.function_calls
#
# Si existen function calls, itera sobre ellas e imprime:
#
# Calling function: {function_call.name}({function_call.args})
#
# Si no existen function calls, imprime la respuesta del agente normalmente.

# TODO 6.7:
# Ejecuta el programa con prompts que deberían activar tools.
#
# Ejemplo:
#
# uv run python -m quests.quest_06_tool_chest.starter.main \
# "¿Qué archivos hay en la raíz?"
#
# Resultado esperado aproximado:
#
# Calling function: get_files_info({'directory': '.'})
#
# Cuando hayas validado que las tools se están llamando correctamente,
# ejecuta el check para completar la quest:
#
# arkanum check 6