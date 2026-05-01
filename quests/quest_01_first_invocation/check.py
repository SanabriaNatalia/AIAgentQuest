import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

ROOT_DIR = Path(__file__).resolve().parents[2]
STARTER_FILE = ROOT_DIR / "quests" / "quest_01_first_agent" / "starter" / "main.py"

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
            "Excelente trabajo, aprendiz.\n\n"
            "Has realizado la primera invocación correctamente.\n\n"
            "🏆 Rango desbloqueado: Aprendiz\n\n"
            "🎉 ✨ 🎉 ✨ 🎉",
            border_style="green",
        )
    )


def main() -> None:
    if not STARTER_FILE.exists():
        fail(f"No se encontró el archivo:\n{STARTER_FILE}")

    result = subprocess.run(
        [
            sys.executable, 
            "-m", 
            "quests.quest_01_first_agent.starter.main"
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        timeout=200,
    )

    output = result.stdout.strip()
    error = result.stderr.strip()

    if result.returncode != 0:
        fail(
            "El programa terminó con errores.\n\n"
            f"Error:\n{error or output}"
        )

    if len(output) < 50:
        fail(
            "El programa corrió, pero la salida parece demasiado corta.\n"
            "Asegúrate de imprimir la respuesta de Gemini con response.text."
        )

    if "Agente:" not in output:
        fail(
            "No encontré la sección de respuesta de Gemini.\n"
            "Asegúrate de usar agent(response.text) o imprimir la respuesta claramente."
        )

    success()


if __name__ == "__main__":
    main()