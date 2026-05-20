"""Comando `arkanum check <N>` — pre-checks locales + check real.

- `--dry-run`: corre sólo los pre-checks (sin gastar cuota Gemini).
- Modo normal: corre pre-checks primero. Si fallan, pide confirmación antes
  de invocar el check real. Si pasan, sigue derecho.
"""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from common.cli.helpers import (
    check_module,
    check_path,
    resolve_quest_by_number,
    run_module,
)
from common.cli.pre_checks.runner import (
    PreCheckResult,
    all_passed,
    run_pre_checks,
)
from common.progress.db import record_quest_attempt, register_first_attempt

console = Console()


def _render_table(quest_title: str, results: list[PreCheckResult]) -> None:
    table = Table(
        title=f"Pre-checks locales — {quest_title}",
        title_style="bold magenta",
        show_lines=False,
    )
    table.add_column("", width=2, no_wrap=True)
    table.add_column("Check", style="bold")
    table.add_column("Detalle", style="dim")

    for r in results:
        icon = "[green]✔[/green]" if r.passed else "[red]✘[/red]"
        detail = "" if r.passed else (r.detail or "—")
        table.add_row(icon, r.name, detail)

    console.print(table)


def check(
    number: int = typer.Argument(..., help="Número del quest (1..8)"),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Sólo correr pre-checks locales sin invocar Gemini.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Asumir sí cuando se pide confirmación tras pre-checks fallidos.",
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

    register_first_attempt(quest.db_id)

    results = run_pre_checks(quest)
    _render_table(f"Quest {quest.order} — {quest.title}", results)
    passed = all_passed(results)

    if dry_run:
        if passed:
            console.print(
                f"\n[green]Pre-checks OK.[/] Cuando estés listo: "
                f"[cyan]arkanum check {quest.order}[/]"
            )
        else:
            console.print(
                "\n[yellow]Algunos pre-checks fallaron.[/] "
                "Revisa los detalles antes de invocar Gemini."
            )
            raise typer.Exit(1)
        return

    if not passed:
        if not yes:
            proceed = typer.confirm(
                "Los pre-checks locales fallaron. ¿Continuar con el check real "
                "(consume cuota de Gemini)?",
                default=False,
            )
            if not proceed:
                console.print("[dim]Cancelado por el aprendiz.[/]")
                raise typer.Exit(1)

    console.print(
        f"\n[dim]Ejecutando check de[/] [cyan]Quest {quest.order} — {quest.title}[/]"
    )
    console.print("[yellow]Aviso:[/] este check consume cuota de Gemini.")
    console.print()
    rc = run_module(module)
    record_quest_attempt(
        quest.db_id,
        passed=rc == 0,
        failure_reason=None if rc == 0 else f"check exit code {rc}",
    )
    if rc != 0:
        raise typer.Exit(rc)
