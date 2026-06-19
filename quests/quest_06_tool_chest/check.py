import os
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from common.cli.check_runner import (
    render_any_of_table,
    render_required_outputs_table,
)
from common.progress.db import record_quest_completion
from common.utils.ui import warning

ROOT_DIR = Path(__file__).resolve().parents[2]

console = Console()

REQUIRED_OUTPUTS = [
    ("Calling function:", "El agente invocó una herramienta (línea 'Calling function:')"),
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
            3,
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
    # Si el aprendiz pasó un prompt vía `arkanum check 6 "..."`, llega aquí
    # como ARKANUM_CHECK_PROMPT. Si no, fallback al prompt canónico.
    prompt = (
        os.environ.get("ARKANUM_CHECK_PROMPT")
        or "¿Qué archivos hay en la raíz?"
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "quests.quest_06_tool_chest.starter.main",
            prompt,
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        timeout=30,
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

    table, missing = render_required_outputs_table(
        "Salidas esperadas — Quest 6",
        output,
        REQUIRED_OUTPUTS,
    )
    console.print(table)
    if missing:
        fail(
            f"Faltaron {len(missing)} salida(s). El starter debe imprimir "
            "'Calling function: ...' cuando el modelo planea una tool."
        )

    tools_table, found_any = render_any_of_table(
        "Tools válidas detectadas",
        output,
        VALID_FUNCTIONS,
        item_label="Tool",
    )
    console.print(tools_table)
    if not found_any:
        fail(
            "Ninguna de las tools válidas apareció en los function calls. "
            "Revisa que tu agente esté planeando alguna de las 4 tools registradas."
        )

    success()


if __name__ == "__main__":
    main()