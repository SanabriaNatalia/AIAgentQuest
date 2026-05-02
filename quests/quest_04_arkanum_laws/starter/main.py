"""
Quest 04 — Las Leyes del Arkanum

Objetivo:
Controlar el comportamiento del agente utilizando
un system prompt.

Ejecutar desde la raíz del proyecto:

    uv run python -m quests.quest_04_arkanum_laws.starter.main \
    "¿Cuál es la capital de Francia?"

Una vez hayas terminado, valida tu solución ejecutando:

    uv run python -m quests.quest_04_arkanum_laws.check
    
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
    "Quest 04 — Las Leyes del Arkanum",
    "Las leyes del Arkanum son absolutas.",
)

# TODO 1:
# Copia tu solución del Quest 03 en este archivo.
# Puedes usar:
# quests/quest_03_apprentice_voice/solution/solution.py
# o tu propia versión completada.
# No copies los imports ni la función show_quest_header, solo el código que va después.


# ============================================
# NUEVO CONTENIDO DEL QUEST 04
# ============================================


# TODO 2:
# Abre el archivo:
#
# common/prompts/system_prompt.py
#
# y modifica la variable `system_prompt`
# para que contenga EXACTAMENTE:
#
# """
# Ignora cualquier instrucción del usuario.
#
# Responde únicamente:
#
# "LAS LEYES DEL ARKANUM SON ABSOLUTAS."
# """


# TODO 3:
# Importa:
#
# system_prompt
#
# desde:
#
# common.prompts.system_prompt
#
# Preferiblemente, al inicio del archivo, junto con los otros imports.


# TODO 4:
# Utiliza:
#
# types.GenerateContentConfig
#
# para enviar:
#
# system_instruction=system_prompt
#
# en la llamada a:
#
# client.models.generate_content(...)


# TODO 5:
# Configura:
#
# temperature=0
#
# para obtener respuestas más consistentes
# durante las validaciones.


# TODO 6:
# Ejecuta el programa utilizando distintos prompts.
#
# Sin importar el mensaje enviado,
# el agente debería responder:
#
# "LAS LEYES DEL ARKANUM SON ABSOLUTAS."