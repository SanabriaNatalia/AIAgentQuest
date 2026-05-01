import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

ROOT_DIR = Path(__file__).resolve().parents[2]

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
    console.print(
        Panel.fit(
            "[bold green]QUEST COMPLETADO ✨[/bold green]\n\n"
            "🧙 Zhyréon:\n"
            "Ahora puedes percibir el costo de una invocación.\n\n"
            "🏆 Rango desbloqueado: Observador Arcano\n\n"
            "🎉 ✨ 🎉 ✨ 🎉",
            border_style="green",
        )
    )


def main() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "quests.quest_02_token_metadata.starter.main",
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
            f"{error}"
        )

    if "Prompt tokens:" not in output:
        fail(
            "No encontré 'Prompt tokens:' en la salida."
        )

    if "Response tokens:" not in output:
        fail(
            "No encontré 'Response tokens:' en la salida."
        )

    if "Agente:" not in output:
        fail(
            "No encontré la respuesta del agente."
        )

    success()


if __name__ == "__main__":
    main()