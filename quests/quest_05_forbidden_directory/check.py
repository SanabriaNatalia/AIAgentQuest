import os
import subprocess
import sys
from pathlib import Path
from common.cli.check_runner import render_required_outputs_table
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
        2, 
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
    # Forzamos COLUMNS=1000 para que rich.Console no envuelva líneas largas
    # en el subprocess; sin esto, el wrap rompe el `expected in output` de
    # más abajo cuando la terminal del aprendiz es estrecha. Ver H-08.
    env = os.environ.copy()
    env["COLUMNS"] = "1000"
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
        env=env,
    )

    output = result.stdout
    error = result.stderr

    # Reemite la salida del starter en la terminal del aprendiz, para que
    # la respuesta del agente quede visible durante `arkanum check`.
    if output:
        sys.stdout.write(output)
        if not output.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()

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

    table, missing = render_required_outputs_table(
        "Salidas esperadas — Quest 5",
        output,
        REQUIRED_OUTPUTS,
    )
    console.print(table)
    if missing:
        fail(
            f"Faltaron {len(missing)} salida(s) esperada(s) en los tests. "
            "Revisa los try/except del starter y la función validador."
        )

    success()


if __name__ == "__main__":
    main()