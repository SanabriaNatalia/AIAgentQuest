"""Comando `arkanum cost` — tokens consumidos y estimación de costo."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from common.dashboard.services.cost import (
    PRICE_INPUT_PER_1M,
    PRICE_OUTPUT_PER_1M,
    attempts_history,
    cost_per_quest,
    has_any_cost,
    total_cost,
)

console = Console()


def _fmt_usd(value: float) -> str:
    if value < 0.01:
        return f"${value:.4f}"
    return f"${value:.2f}"


def cost(
    per_attempt: bool = typer.Option(
        False,
        "--per-attempt",
        help="Mostrar histórico crudo (una fila por invocación).",
    ),
    limit: int = typer.Option(
        25,
        "--limit",
        help="Máximo de filas para --per-attempt.",
    ),
) -> None:
    """Mostrar tokens consumidos en checks y costo estimado en USD."""
    if not has_any_cost():
        console.print(
            "[dim]Aún no se ha registrado ningún costo.[/] "
            "Ejecuta [cyan]arkanum check N[/] (Q02 en adelante) para empezar a sumar."
        )
        return

    if per_attempt:
        _render_attempts(limit)
    else:
        _render_aggregate()


def _render_aggregate() -> None:
    table = Table(
        title="Tokens consumidos por quest",
        title_style="bold magenta",
    )
    table.add_column("Quest", style="bold")
    table.add_column("Invoc.", justify="right", style="dim")
    table.add_column("Prompt", justify="right")
    table.add_column("Response", justify="right")
    table.add_column("Total", justify="right", style="bold")
    table.add_column("USD est.", justify="right", style="cyan")

    rows = cost_per_quest()
    for row in rows:
        table.add_row(
            f"Q{row.quest.order:02d} — {row.quest.title}",
            str(row.invocations),
            f"{row.prompt_tokens:,}",
            f"{row.response_tokens:,}",
            f"{row.total_tokens:,}",
            _fmt_usd(row.estimated_usd),
        )

    totals = total_cost()
    table.add_section()
    table.add_row(
        "[bold]Total[/]",
        str(totals["invocations"]),
        f"{totals['prompt_tokens']:,}",
        f"{totals['response_tokens']:,}",
        f"{totals['total_tokens']:,}",
        _fmt_usd(totals["estimated_usd"]),
    )
    console.print(table)
    console.print(
        f"[dim]Tarifa Gemini 2.5 Flash usada:[/] "
        f"prompt ${PRICE_INPUT_PER_1M}/1M · response ${PRICE_OUTPUT_PER_1M}/1M"
    )


def _render_attempts(limit: int) -> None:
    table = Table(
        title=f"Histórico de invocaciones (últimas {limit})",
        title_style="bold magenta",
    )
    table.add_column("Fecha", style="dim")
    table.add_column("Quest")
    table.add_column("Prompt", justify="right")
    table.add_column("Response", justify="right")
    table.add_column("USD est.", justify="right", style="cyan")

    for entry in attempts_history(limit=limit):
        quest_label = (
            f"Q{entry.quest.order:02d} — {entry.quest.title}" if entry.quest else "?"
        )
        table.add_row(
            entry.attempted_at,
            quest_label,
            f"{entry.prompt_tokens:,}",
            f"{entry.response_tokens:,}",
            _fmt_usd(entry.estimated_usd),
        )
    console.print(table)
