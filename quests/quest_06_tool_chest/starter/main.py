"""
Quest 06 — El Cofre de Instrumentos

Objetivo:
Registrar herramientas disponibles para que el modelo pueda
solicitar function calls.

Ejecutar desde la raíz del proyecto:

    uv run python -m quests.quest_06_tool_chest.starter.main \
    "¿Qué archivos hay en la raíz?"

Una vez hayas terminado, valida tu solución ejecutando:

    uv run python -m quests.quest_06_tool_chest.check
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

# TODO 1:

# Copia tu solución del Quest 04 en este archivo.
# Puedes usar:
#
# quests/quest_04_arkanum_laws/solution/solution.py
#
# o tu propia versión completada.
#
# No copies los imports ni la función show_quest_header,
# solo el código que va después.

# ============================================
# NUEVO CONTENIDO DEL QUEST 06
# ============================================

# TODO 2:
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

# TODO 3:

# Completa los schemas faltantes en:
#
# common/functions/get_file_content.py
# common/functions/write_file.py
# common/functions/run_python_file.py
#
# Usa como referencia el schema ya existente en:
#
# common/functions/get_files_info.py

# TODO 4:

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

# TODO 5:
# Importa:
#
# available_functions
#
# desde:
#
# common.functions.call_function
#
# Preferiblemente, al inicio del archivo, junto con los otros imports.

# TODO 6:
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

# TODO 7:
# Después de recibir la respuesta, revisa:
#
# response.function_calls
#
# Si existen function calls, itera sobre ellas e imprime:
#
# Calling function: {function_call.name}({function_call.args})
#
# Si no existen function calls, imprime la respuesta del agente normalmente.

# TODO 8:
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
# uv run python -m quests.quest_06_tool_chest.check