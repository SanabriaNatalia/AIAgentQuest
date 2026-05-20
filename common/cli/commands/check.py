"""Comando `arkanum check <N>` — ejecuta el check del quest N."""
from __future__ import annotations

import typer
from rich.console import Console

from common.cli.helpers import (
    check_module,
    check_path,
    resolve_quest_by_number,
    run_module,
)

console = Console()


def check(
    number: int = typer.Argument(..., help="Número del quest (1..8)"),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Sólo correr pre-checks locales sin invocar Gemini (F10 los implementa).",
    ),
) -> None:
    """Validar la solución del quest indicado."""
    quest = resolve_quest_by_number(number)
    module = check_module(quest)

    if not check_path(quest).exists():
        console.print(
            f"[red]No existe el check para Quest {quest.order}:[/] {check_path(quest)}"
        )
        raise typer.Exit(1)

    if dry_run:
        console.print(
            "[yellow]⚠ Pre-checks locales aún no implementados[/] "
            "(llegan en Fase 10)."
        )
        console.print(
            f"[dim]Para correr el check real:[/] [cyan]arkanum check {quest.order}[/]"
        )
        return

    console.print(
        f"[dim]Ejecutando check de[/] [cyan]Quest {quest.order} — {quest.title}[/]"
    )
    console.print(
        "[yellow]Aviso:[/] este check consume cuota de Gemini."
    )
    console.print()
    rc = run_module(module)
    if rc != 0:
        raise typer.Exit(rc)
