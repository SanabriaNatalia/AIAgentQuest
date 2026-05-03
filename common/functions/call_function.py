from google.genai import types

# ============================================
# QUEST 06
# ============================================

# TODO 1 — Quest 06:
# Importa aquí los esquemas de todas las funciones que podrá usar el agente.
from common.functions.get_files_info import schema_get_files_info

# TODO 2 — Quest 06:
# Registra las herramientas disponibles para el agente.
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]

)

# ============================================
# QUEST 07
# ============================================