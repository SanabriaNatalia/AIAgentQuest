"""Punto de entrada del CLI `arkanum`. Los comandos se agregan en fases posteriores."""
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

import typer

from common.cli.commands.check import check
from common.cli.commands.cost import cost
from common.cli.commands.current import current
from common.cli.commands.dashboard import dashboard_app
from common.cli.commands.doctor import doctor
from common.cli.commands.init import init
from common.cli.commands.next_quest import next_quest
from common.cli.commands.progress import progress
from common.cli.commands.run import run
from common.cli.commands.start import start

app = typer.Typer(
    name="arkanum",
    help="Arkanum — CLI del laboratorio de agentes",
    no_args_is_help=True,
)

app.add_typer(dashboard_app, name="dashboard")
app.command(name="doctor")(doctor)
app.command(name="init")(init)
app.command(name="current")(current)
app.command(name="next")(next_quest)
app.command(name="progress")(progress)
app.command(
    name="start",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)(start)
app.command(
    name="run",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)(run)
app.command(name="check")(check)
app.command(name="cost")(cost)


@app.callback()
def _root() -> None:
    """Arkanum — CLI del laboratorio de agentes."""


if __name__ == "__main__":
    app()
