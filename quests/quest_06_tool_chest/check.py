import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from common.progress.db import record_quest_completion
from common.utils.ui import warning

ROOT_DIR = Path(__file__).resolve().parents[2]

console = Console()

REQUIRED_OUTPUTS = [
    "Calling function:",
]

VALID_FUNCTIONS = [
    "get_files_info",
    "get_file_content",
    "write_file",
    "run_python_file",
]


def fail(message: str) -> None:
    console.print(
        Panel.fit(
            f"[bold red]QUEST INCOMPLETO[/bold red]\n\n{message}",
            border_style="red",
        )
    )

    raise SystemExit(1)


def success() -> None:
    try:
        record_quest_completion(
            "El Cofre de Instrumentos",
            "Artífice de Herramientas",
        )

    except Exception as e:
        warning(f"{e}")

    console.print(
        Panel.fit(
            "[bold green]QUEST COMPLETADO ✨[/bold green]\n\n"
            "🧙 Zhyréon:\n"
            "El agente ha abierto el Cofre de Instrumentos, pronto estará listo para usarlas.\n\n"
            "🏆 Rango desbloqueado: Artífice de Herramientas\n\n"
            "🎉 ✨ 🎉 ✨ 🎉",
            border_style="green",
        )
    )


def main() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "quests.quest_06_tool_chest.starter.main",
            "¿Qué archivos hay en la raíz?",
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )

    output = result.stdout
    error = result.stderr

    if result.returncode != 0:
        fail(
            "El programa terminó con errores.\n\n"
            f"{error or output}"
        )

    for expected in REQUIRED_OUTPUTS:
        if expected not in output:
            fail(
                "No encontré una salida esperada.\n\n"
                f"Faltó:\n{expected}\n\n"
                f"Salida completa:\n{output}"
            )

    found_valid_function = any(
        function_name in output
        for function_name in VALID_FUNCTIONS
    )

    if not found_valid_function:
        fail(
            "No encontré ninguna tool válida en los function calls.\n\n"
            f"Tools esperadas:\n{VALID_FUNCTIONS}\n\n"
            f"Salida completa:\n{output}"
        )

    success()


if __name__ == "__main__":
    main()