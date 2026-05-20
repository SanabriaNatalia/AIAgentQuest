"""Comando `arkanum next` — muestra la próxima quest después de la actual."""
from __future__ import annotations

import typer
from rich.console import Console

from common.dashboard.services.progress import get_apprentice, get_current_quest
from common.dashboard.services.quest_catalog import QUESTS

console = Console()


def next_quest() -> None:
    """Mostrar la próxima quest tras la actual."""
    apprentice = get_apprentice()
    if apprentice is None:
        console.print(
            "[yellow]Aún no hay aprendiz registrado.[/] "
            "Ejecuta: [cyan]arkanum init[/]"
        )
        raise typer.Exit(1)

    current = get_current_quest()
    if current is None:
        console.print("[gold1]Has completado todos los quests disponibles.[/]")
        return

    upcoming = [q for q in QUESTS if q.order > current.order]
    if not upcoming:
        console.print(
            f"[gold1]La quest actual ({current.title}) es la última disponible.[/]"
        )
        return

    nxt = upcoming[0]
    console.print()
    console.print(f"[dim]Quest actual:[/] [bold]Quest {current.order}[/] · {current.title}")
    console.print(
        f"[dim]Próxima:[/]      [bold]Quest {nxt.order}[/] · {nxt.title}"
    )
    console.print(f"[dim]Rango sellado:[/] {nxt.rank_unlocked}")
    console.print()
