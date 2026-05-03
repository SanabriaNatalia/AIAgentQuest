import subprocess
import sys
from pathlib import Path
from common.progress.db import record_quest_completion
from rich.console import Console
from rich.panel import Panel

ROOT_DIR = Path(__file__).resolve().parents[2]

REQUIRED_OUTPUTS = [
    "Validando ruta permitida: .",
    "Validando ruta permitida: src",
    "Validando ruta permitida: notes.txt",
    "Ruta válida ->",
    "Validando ruta prohibida: ../",
    "Ruta bloqueada correctamente -> '../' is outside the permitted working directory",
    "Validando ruta prohibida: ../../secrets.txt",
    "Ruta bloqueada correctamente -> '../../secrets.txt' is outside the permitted working directory",
]

console = Console()


def fail(message: str) -> None:
    console.print(
        Panel.fit(
            f"[bold red]QUEST INCOMPLETO[/bold red]\n\n{message}",
            border_style="red",
        )
    )
    raise SystemExit(1)


def success() -> None:
    record_quest_completion(
        "El Directorio Prohibido", 
        "Guardián del Umbral"
    )
    console.print(
        Panel.fit(
            "[bold green]QUEST COMPLETADO ✨[/bold green]\n\n"
            "🧙 Zhyréon:\n"
            "Has trazado la frontera del agente.\n\n"
            "🏆 Rango desbloqueado: Guardián del Umbral\n\n"
            "🎉 ✨ 🎉 ✨ 🎉",
            border_style="green",
        )
    )


def main() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "quests.quest_05_forbidden_directory.starter.main",
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        timeout=20,
    )

    output = result.stdout
    error = result.stderr

    if result.returncode != 0:
        fail(
            "El programa terminó con errores.\n\n"
            f"{error or output}"
        )

    if "FAIL" in output:
        fail(
            "Encontré un FAIL en la salida del starter.\n\n"
            f"Salida:\n{output}"
        )

    for expected in REQUIRED_OUTPUTS:
        if expected not in output:
            fail(
                "No encontré una salida esperada.\n\n"
                f"Faltó:\n{expected}\n\n"
                f"Salida completa:\n{output}"
            )

    success()


if __name__ == "__main__":
    main()