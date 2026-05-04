import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from common.progress.db import record_quest_completion
from common.utils.ui import warning

ROOT_DIR = Path(__file__).resolve().parents[2]

console = Console()

EXPECTED_OUTPUTS = [
    "Calling function:",
    "result",
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
            "La Encarnación del Agente",
            "Conjurador de Encarnaciones",
        )

    except Exception as e:
        warning(f"{e}")

    console.print(
        Panel.fit(
            "[bold green]QUEST COMPLETADO ✨[/bold green]\n\n"
            "🧙 Zhyréon:\n"
            "El agente ha actuado sobre el mundo por primera vez.\n\n"
            "🏆 Rango desbloqueado: Conjurador de Encarnaciones\n\n"
            "🎉 ✨ 🎉 ✨ 🎉",
            border_style="green",
        )
    )


def main() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "quests.quest_07_agent_incarnation.starter.main",
            "¿Qué archivos hay en la raíz?",
            "--verbose",
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

    for expected in EXPECTED_OUTPUTS:
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
            "No encontré ninguna tool válida ejecutándose.\n\n"
            f"Tools esperadas:\n{VALID_FUNCTIONS}\n\n"
            f"Salida completa:\n{output}"
        )

    success()


if __name__ == "__main__":
    main()