"""Comando `arkanum progress` — vista rápida del avance del aprendiz.

Reemplaza el legacy `common.progress.show_progress` con render Rich
(cp1252-safe gracias al reconfigure de UTF-8 en main.py).
"""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from common.dashboard.services.progress import (
    get_apprentice,
    get_completed_count,
    get_quest_status_map,
    get_xp_breakdown,
)
from common.dashboard.services.quest_catalog import QUESTS

console = Console()


def progress() -> None:
    """Mostrar el progreso del aprendiz."""
    apprentice = get_apprentice()
    if apprentice is None:
        console.print(
            "[yellow]Aún no hay aprendiz registrado.[/] "
            "Ejecuta: [cyan]arkanum init[/]"
        )
        raise typer.Exit(1)

    level, xp_in_level, xp_required, xp_pct = get_xp_breakdown(apprentice.xp)
    completed_count = get_completed_count()
    status_map = get_quest_status_map()

    console.print()
    console.print(f"[bold gold1]⚜ Aprendiz:[/] {apprentice.username}")
    console.print(f"[dim]Rango actual:[/] [italic]{apprentice.current_rank}[/]")
    console.print(f"[dim]Nivel:[/] [bold]{level}[/]   "
                  f"[dim]XP:[/] {xp_in_level}/{xp_required} ({xp_pct}%)   "
                  f"[dim]Total:[/] {apprentice.xp}")
    console.print(f"[dim]Quests completados:[/] [bold]{completed_count}[/] / {len(QUESTS)}")
    console.print()

    table = Table(show_header=True, header_style="bold gold1", box=None, padding=(0, 1))
    table.add_column("#", justify="right", style="dim")
    table.add_column("Quest")
    table.add_column("Estado")
    table.add_column("Rango", style="italic")

    icons = {"completed": "[green]✓ completado[/]",
             "current":   "[magenta]★ en curso[/]",
             "locked":    "[dim]🔒 sellado[/]"}

    for q in QUESTS:
        st = status_map.get(q.slug, "locked")
        table.add_row(
            str(q.order),
            q.title,
            icons[st],
            q.rank_unlocked if st != "locked" else "[dim]—[/]",
        )

    console.print(table)
    console.print()
