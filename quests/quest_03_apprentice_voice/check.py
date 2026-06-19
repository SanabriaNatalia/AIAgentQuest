import os
import subprocess
import sys
from pathlib import Path
from common.cli.check_runner import render_required_outputs_table
from common.progress.db import record_quest_completion
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
    record_quest_completion(
        "La Voz del Aprendiz",
        1, 
        "Proclamador Arcano"
    )
    console.print(
        Panel.fit(
            "[bold green]QUEST COMPLETADO ✨[/bold green]\n\n"
            "🧙 Zhyréon:\n"
            "El agente ha escuchado la voz del aprendiz.\n\n"
            "🏆 Rango desbloqueado: Proclamador Arcano\n\n"
            "🎉 ✨ 🎉 ✨ 🎉",
            border_style="green",
        )
    )


def main() -> None:
    # Si el aprendiz pasó un prompt vía `arkanum check 3 "..."`, llega aquí
    # como ARKANUM_CHECK_PROMPT. Si no, fallback al prompt canónico. Q03 trata
    # justamente de "la voz del aprendiz", así que respetar su prompt es lo
    # coherente (mismo patrón que Q06/Q07).
    prompt = (
        os.environ.get("ARKANUM_CHECK_PROMPT")
        or "¿Qué es un agente IA? Responde en un párrafo corto."
    )

    # H-08: COLUMNS=1000 evita que rich.Console envuelva líneas largas
    # del subprocess y rompa la búsqueda `prompt in output` de abajo.
    env = os.environ.copy()
    env["COLUMNS"] = "1000"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "quests.quest_03_apprentice_voice.starter.main",
            prompt,
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        timeout=30,
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

    table, missing = render_required_outputs_table(
        "Salidas esperadas — Quest 3",
        output,
        [prompt, "Prompt tokens:", "Response tokens:", "Gemini"],
    )
    console.print(table)
    if missing:
        fail(
            f"Faltaron {len(missing)} salida(s) esperada(s) en la consola. "
            "Revisa que recibas el prompt con argparse y muestres tokens + respuesta."
        )

    success()


if __name__ == "__main__":
    main()