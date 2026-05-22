"""Comando `arkanum doctor` — diagnóstico de setup del laboratorio."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from common.progress.setup_diagnostics import count_statuses, run_setup_diagnostics

_ICONS = {
    "ok": "[green]✓[/]",
    "warn": "[yellow]⚠[/]",
    "fail": "[red]✗[/]",
}


def doctor(
    skip_ping: bool = typer.Option(
        False,
        "--skip-ping",
        "-s",
        help="Omitir ping real a Gemini (usa solo cache)",
    ),
) -> None:
    """Diagnóstico de setup del laboratorio Arkanum."""
    console = Console()
    console.print("\n[bold]Diagnóstico del Arkanum[/]\n")

    checks = run_setup_diagnostics(skip_api_ping=skip_ping)

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column(width=2)
    table.add_column()
    table.add_column(style="dim")

    for check in checks:
        table.add_row(_ICONS[check.status], check.label, check.detail or "")

    console.print(table)

    counts = count_statuses(checks)
    console.print()
    console.print(
        f"[green]{counts['ok']} ok[/]  ·  "
        f"[yellow]{counts['warn']} avisos[/]  ·  "
        f"[red]{counts['fail']} errores[/]"
    )

    if counts["fail"] > 0:
        raise typer.Exit(1)
