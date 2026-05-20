"""Comando `arkanum init` — wizard de registro del aprendiz.

Reemplaza al legacy `common/progress/init_user.py`. Diferencias:
- Usa Rich Prompt (cp1252-safe via reconfigure en main.py).
- Verifica `.env` y `GEMINI_API_KEY`, opcionalmente pinguea Gemini.
- Si el aprendiz ya está registrado, ofrece actualizar el nombre.
- Pregunta si abrir el dashboard al final.
"""
from __future__ import annotations

import webbrowser
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from common.dashboard import lifecycle
from common.progress.db import get_connection, init_db
from common.progress.setup_diagnostics import _read_gemini_key, _validate_api_key

console = Console()

STARTING_RANK = "Aprendiz del Arkanum"


def init(
    skip_ping: bool = typer.Option(
        False,
        "--skip-ping",
        help="No validar la API key contra Gemini (más rápido).",
    ),
    no_dashboard: bool = typer.Option(
        False,
        "--no-dashboard",
        help="No preguntar por arrancar el dashboard.",
    ),
) -> None:
    """Registrar al aprendiz y configurar el laboratorio."""
    console.print()
    console.print(
        Panel.fit(
            "[bold gold1]⚜ Bienvenido al Arkanum ⚜[/]\n"
            "[dim]Antes de invocar al primer agente, "
            "debes dar tu nombre al maestro.[/]",
            border_style="gold1",
        )
    )
    console.print()

    init_db()

    existing = _get_existing_apprentice()
    default_name = existing.get("username") if existing else None

    if existing:
        console.print(
            f"[yellow]Ya existe un aprendiz registrado:[/] [bold]{default_name}[/]"
        )
        if not Confirm.ask("¿Actualizar el nombre?", default=False, console=console):
            console.print("Manteniendo nombre actual.")
        else:
            default_name = None

    if default_name is None:
        username = Prompt.ask("Nombre del aprendiz", console=console).strip()
        if not username:
            console.print("[red]El nombre no puede estar vacío.[/]")
            raise typer.Exit(1)
        _upsert_apprentice(username)
        console.print(f"[green]✓[/] Aprendiz registrado: [bold]{username}[/]")
        console.print(f"[green]✓[/] Rango inicial: [italic]{STARTING_RANK}[/]")

    # === API key ===
    console.print()
    console.print("[bold]Validando configuración de Gemini...[/]")
    _check_and_offer_api_key(skip_ping=skip_ping)

    # === Dashboard ===
    if not no_dashboard:
        console.print()
        if Confirm.ask("¿Abrir el dashboard arcano?", default=True, console=console):
            _start_and_open_dashboard()

    console.print()
    console.print(
        Panel.fit(
            "[bold gold1]Laboratorio listo[/]\n\n"
            "Comandos útiles:\n"
            "  [cyan]arkanum current[/]   — quest actual\n"
            "  [cyan]arkanum start 1[/]   — empezar Quest 1\n"
            "  [cyan]arkanum progress[/]  — ver tu avance",
            border_style="purple",
        )
    )


def _get_existing_apprentice() -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT username, current_rank FROM apprentice WHERE id = 1"
        ).fetchone()
    if row is None:
        return None
    return {"username": row[0], "current_rank": row[1]}


def _upsert_apprentice(username: str) -> None:
    with get_connection() as conn:
        existing = conn.execute("SELECT id FROM apprentice WHERE id = 1").fetchone()
        if existing:
            conn.execute(
                "UPDATE apprentice SET username = ? WHERE id = 1",
                (username,),
            )
        else:
            conn.execute(
                "INSERT INTO apprentice (id, username, current_rank, xp, level) "
                "VALUES (1, ?, ?, 0, 1)",
                (username, STARTING_RANK),
            )


def _check_and_offer_api_key(*, skip_ping: bool) -> None:
    if not Path(".env").exists():
        console.print(
            "[red]✗[/] No existe [bold].env[/] en la raíz del proyecto."
        )
        console.print(
            "[dim]Crea el archivo y agrega:[/] "
            "[cyan]GEMINI_API_KEY='tu_clave_aqui'[/]"
        )
        console.print(
            "[dim]Genera una clave en:[/] https://aistudio.google.com/"
        )
        return

    key = _read_gemini_key()
    if not key:
        console.print(
            "[red]✗[/] [bold].env[/] existe pero [bold]GEMINI_API_KEY[/] está vacía."
        )
        return

    console.print(f"[green]✓[/] API key presente (longitud {len(key)}).")

    if skip_ping:
        console.print("[yellow]⚠[/] Ping a Gemini omitido (--skip-ping).")
        return

    console.print("[dim]Pingueando Gemini...[/]")
    result = _validate_api_key(key)
    if result.status == "ok":
        console.print(f"[green]✓[/] {result.label} — {result.detail or ''}")
    elif result.status == "warn":
        console.print(f"[yellow]⚠[/] {result.label} — {result.detail or ''}")
    else:
        console.print(f"[red]✗[/] {result.label} — {result.detail or ''}")


def _start_and_open_dashboard() -> None:
    try:
        if lifecycle.is_running():
            st = lifecycle.status()
            console.print(
                f"[yellow]Dashboard ya activo[/] (PID {st['pid']}, puerto {st['port']})."
            )
        else:
            console.print("Iniciando dashboard...")
            pid = lifecycle.start(detached=True)
            st = lifecycle.status()
            console.print(
                f"[green]✓[/] Dashboard activo (PID {pid}, puerto {st['port']})."
            )
        url = f"http://127.0.0.1:{lifecycle.status()['port']}"
        webbrowser.open(url)
        console.print(f"Abriendo {url}")
    except RuntimeError as exc:
        console.print(f"[red]Error al iniciar dashboard:[/] {exc}")
