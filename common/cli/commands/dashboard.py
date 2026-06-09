"""Subcomandos `arkanum dashboard [start|stop|status|logs|open]`."""
from __future__ import annotations

import time
import webbrowser

import typer
from rich.console import Console

from common.dashboard import lifecycle

console = Console()

dashboard_app = typer.Typer(
    name="dashboard",
    help="Controlar el servidor del dashboard arcano",
    no_args_is_help=True,
)


@dashboard_app.command("start")
def start_cmd(
    dev: bool = typer.Option(
        False,
        "--dev",
        help="Modo desarrollo: foreground con auto-reload (no se detacha)",
    ),
) -> None:
    """Arrancar el dashboard (detached por default) y abrirlo en el navegador.

    El modo `--dev` corre en foreground y no abre el navegador.
    """
    if dev:
        console.print("[bold magenta]Modo desarrollo[/]: foreground con auto-reload.")
        console.print("Ctrl+C para detener.\n")
        lifecycle.start(detached=False, dev=True)
        return

    if lifecycle.is_running():
        st = lifecycle.status()
        url = f"http://127.0.0.1:{st['port']}"
        console.print(
            f"[yellow]El dashboard ya está activo[/] "
            f"(PID {st['pid']}, puerto {st['port']})"
        )
        console.print(url)
        webbrowser.open(url)
        return

    console.print("Iniciando dashboard arcano...")
    try:
        pid = lifecycle.start(detached=True)
    except RuntimeError as exc:
        console.print(f"[red]Error al iniciar:[/] {exc}")
        raise typer.Exit(1)

    st = lifecycle.status()
    url = f"http://127.0.0.1:{st['port']}"
    console.print(
        f"[green]Dashboard activo[/] (PID {pid}, puerto {st['port']})"
    )
    console.print(url)
    webbrowser.open(url)


@dashboard_app.command("stop")
def stop_cmd() -> None:
    """Detener el dashboard."""
    if not lifecycle.is_running():
        console.print("[yellow]El dashboard no está activo.[/]")
        return

    if lifecycle.stop():
        console.print("[green]Dashboard detenido.[/]")
    else:
        console.print("[red]No se pudo detener el dashboard.[/]")
        raise typer.Exit(1)


@dashboard_app.command("status")
def status_cmd() -> None:
    """Mostrar el estado del dashboard."""
    st = lifecycle.status()
    if not st["running"]:
        console.print("[yellow]Dashboard inactivo.[/]")
        return

    uptime_s = st["uptime"] or 0
    hours, rest = divmod(uptime_s, 3600)
    minutes, seconds = divmod(rest, 60)
    console.print(
        f"[green]Activo[/] · PID {st['pid']} · puerto {st['port']} · "
        f"uptime {hours}h {minutes}m {seconds}s"
    )
    console.print(f"http://127.0.0.1:{st['port']}")


@dashboard_app.command("logs")
def logs_cmd(
    follow: bool = typer.Option(False, "--follow", "-f", help="Tail -f"),
    lines: int = typer.Option(50, "--lines", "-n", help="Líneas a mostrar"),
) -> None:
    """Mostrar logs del dashboard."""
    log_file = lifecycle.LOG_FILE
    if not log_file.exists():
        console.print("[yellow]No hay logs todavía.[/]")
        return

    content = log_file.read_text(encoding="utf-8", errors="replace")
    tail = content.splitlines()[-lines:]
    for line in tail:
        console.print(line, markup=False, highlight=False)

    if not follow:
        return

    with log_file.open("r", encoding="utf-8", errors="replace") as fh:
        fh.seek(0, 2)
        try:
            while True:
                line = fh.readline()
                if line:
                    console.print(line.rstrip("\n"), markup=False, highlight=False)
                else:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            pass


@dashboard_app.command("open")
def open_cmd() -> None:
    """Abrir el dashboard en el browser. Lo arranca si está inactivo."""
    if not lifecycle.is_running():
        console.print("Dashboard inactivo. Iniciando...")
        try:
            lifecycle.start(detached=True)
        except RuntimeError as exc:
            console.print(f"[red]Error al iniciar:[/] {exc}")
            raise typer.Exit(1)

    st = lifecycle.status()
    url = f"http://127.0.0.1:{st['port']}"
    webbrowser.open(url)
    console.print(f"Abriendo {url}")
