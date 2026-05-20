"""Punto de entrada del CLI `arkanum`. Los comandos se agregan en fases posteriores."""
import typer

app = typer.Typer(
    name="arkanum",
    help="Arkanum — CLI del laboratorio de agentes",
    no_args_is_help=True,
)


@app.callback()
def _root() -> None:
    """Arkanum — CLI del laboratorio de agentes."""


if __name__ == "__main__":
    app()
