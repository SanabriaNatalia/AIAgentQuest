"""Comando `arkanum current` — muestra el quest actual del aprendiz."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from common.dashboard.services.progress import get_apprentice, get_current_quest
from common.dashboard.services.quest_catalog import ACTS

console = Console()


def current() -> None:
    """Mostrar la quest actual del aprendiz."""
    apprentice = get_apprentice()
    if apprentice is None:
        console.print(
            "[yellow]Aún no hay aprendiz registrado.[/] "
            "Ejecuta primero: [cyan]arkanum init[/]"
        )
        raise typer.Exit(1)

    quest = get_current_quest()
    if quest is None:
        console.print(
            Panel.fit(
                "[bold gold1]Travesía completada[/]\n\n"
                "Has invocado todo lo que el laboratorio ofrece hoy.\n"
                "[dim]El acto III aguarda en las profundidades.[/]",
                border_style="gold1",
            )
        )
        return

    act = ACTS[quest.act]
    console.print()
    console.print(
        Panel.fit(
            f"[bold gold1]Quest {quest.order} — {quest.title}[/]\n"
            f"[dim]Acto {quest.act} · {act.name}[/]\n\n"
            f"[italic]“{quest.quote_zhyreon}”[/]\n"
            f"[dim]— Zhyréon[/]\n\n"
            f"Rango por obtener: [bold]{quest.rank_unlocked}[/]\n"
            f"XP en juego: [magenta]+{quest.xp}[/]",
            border_style="purple",
        )
    )
    console.print()
    console.print("Para empezar:")
    console.print(f"  [cyan]arkanum start {quest.order}[/]")
