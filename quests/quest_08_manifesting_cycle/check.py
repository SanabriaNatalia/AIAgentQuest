import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from common.progress.db import record_quest_completion
from common.utils.ui import warning

ROOT_DIR = Path(__file__).resolve().parents[2]
WORKSPACE_DIR = ROOT_DIR / "quests" / "quest_08_manifesting_cycle" / "workspace"
CALCULATOR_FILE = WORKSPACE_DIR / "calculator.py"
TESTS_FILE = WORKSPACE_DIR / "tests.py"

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
    try:
        record_quest_completion(
            "El Ciclo de la Manifestación",
            "Conjurador Encarnado",
        )
    except Exception as e:
        warning(f"{e}")

    console.print(
        Panel.fit(
            "[bold green]QUEST COMPLETADO ✨[/bold green]\n\n"
            "🧙 Zhyréon:\n"
            "El agente completó su primer ciclo de manifestación.\n\n"
            "🏆 Rango desbloqueado: Conjurador Encarnado\n\n"
            "🎉 ✨ 🎉 ✨ 🎉",
            border_style="green",
        )
    )

    console.print()

    console.print(
        Panel.fit(
            "[bold magenta]ACTO II COMPLETADO[/bold magenta]\n\n"
            "⚡ La Manifestación del Agente ⚡\n\n"
            "El agente ya no solo habla.\n"
            "Ahora observa, actúa, corrige e itera.\n\n"
            "✨ Nuevo acto desbloqueado:\n"
            "ACTO III — Inteligencia Extendida",
            border_style="magenta",
        )
    )


def main() -> None:
    if not CALCULATOR_FILE.exists():
        fail(f"No encontré el archivo esperado:\n{CALCULATOR_FILE}")

    if not TESTS_FILE.exists():
        fail(f"No encontré el archivo esperado:\n{TESTS_FILE}")

    calculator_code = CALCULATOR_FILE.read_text(encoding="utf-8")

    if "def add" not in calculator_code:
        fail("No encontré la función add() en calculator.py.")

    if "return a + b" not in calculator_code:
        fail(
            "La función add() todavía no parece estar corregida.\n\n"
            "Esperaba encontrar:\n"
            "return a + b"
        )

    result = subprocess.run(
        [sys.executable, "tests.py"],
        cwd=WORKSPACE_DIR,
        capture_output=True,
        text=True,
        timeout=20,
    )

    output = result.stdout
    error = result.stderr

    if result.returncode != 0:
        fail(
            "Los tests de calculator todavía fallan.\n\n"
            f"{error or output}"
        )

    if "All tests passed!" not in output:
        fail(
            "Los tests corrieron, pero no encontré el mensaje esperado:\n"
            "All tests passed!\n\n"
            f"Salida:\n{output}"
        )

    success()


if __name__ == "__main__":
    main()