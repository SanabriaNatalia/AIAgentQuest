"""
Quest 04 — Las Leyes del Arkanum

Objetivo:
Controlar el comportamiento del agente utilizando
un system prompt.

Ejecutar desde la raíz del proyecto:

    arkanum run 4 "¿Cuál es la capital de Francia?"

Una vez hayas terminado, valida tu solución ejecutando:

    arkanum check 4
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

# TODO 4.0 — Preparación:
# Copia tu solución del Quest 03 en este archivo.
# No copies los imports ni la función show_quest_header, solo el código que va después.
# Lo que pegues conservará sus etiquetas TODO 1.x, 2.x y 3.x — esos pasos ya los resolviste.
#
# Puedes usar:
# - quests/quest_03_apprentice_voice/solution/solution.py, o
# - tu propia versión completada.


# ╔══════════════════════════════════════════════════════╗
# ║   NUEVO CONTENIDO DEL QUEST 04                       ║
# ║   A partir de aquí, los TODOs son nuevos (4.x).      ║
# ╚══════════════════════════════════════════════════════╝

# TODO 4.1:
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


# TODO 4.2:
# Importa:
#
# system_prompt
#
# desde:
#
# common.prompts.system_prompt
#
# Preferiblemente, al inicio del archivo, junto con los otros imports.


# TODO 4.3:
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


# TODO 4.4:
# Configura:
#
# temperature=0
#
# para obtener respuestas más consistentes
# durante las validaciones.


# TODO 4.5:
# Ejecuta el programa utilizando distintos prompts.
#
# Sin importar el mensaje enviado,
# el agente debería responder:
#
# "LAS LEYES DEL ARKANUM SON ABSOLUTAS."