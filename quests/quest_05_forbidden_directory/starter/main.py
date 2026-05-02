from common.functions.get_files_info import get_files_info
from common.utils.ui import show_quest_header, success, warning

show_quest_header(
    "Quest 05 — El Directorio Prohibido",
    "El agente aprende los límites de su territorio.",
)

working_directory = "quests/quest_05_forbidden_directory/workspace"

print("\nCaso 1 — Ruta permitida")
print(get_files_info(working_directory, "."))

print("\nCaso 2 — Subdirectorio permitido")
print(get_files_info(working_directory, "src"))

print("\nCaso 3 — Ruta prohibida")
print(get_files_info(working_directory, "../"))