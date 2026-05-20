"""Comando `arkanum start <N>` — ejecuta el starter del quest N."""
from __future__ import annotations

import typer
from rich.console import Console

from common.cli.helpers import (
    resolve_quest_by_number,
    run_module,
    starter_module,
    starter_path,
)

console = Console()


def start(
    ctx: typer.Context,
    number: int = typer.Argument(..., help="Número del quest (1..8)"),
) -> None:
    """Ejecutar el starter del quest indicado.

    Cualquier argumento extra después del número se reenvía al starter.
    Ejemplo: `arkanum start 3 "¿Qué es un agente IA?"`.
    """
    quest = resolve_quest_by_number(number)
    module = starter_module(quest)

    if not starter_path(quest).exists():
        console.print(
            f"[red]No existe el starter para Quest {quest.order}:[/] "
            f"{starter_path(quest)}"
        )
        raise typer.Exit(1)

    extra = list(ctx.args)
    console.print(
        f"[dim]Ejecutando[/] [cyan]{module}[/] "
        f"[dim]· Quest {quest.order} — {quest.title}[/]"
    )
    console.print()
    rc = run_module(module, extra_args=extra)
    if rc != 0:
        raise typer.Exit(rc)
