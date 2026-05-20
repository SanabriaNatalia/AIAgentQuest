"""Singleton de Jinja2Templates para que las rutas no dependan del app factory."""
from pathlib import Path

from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _format_duration(seconds) -> str:
    """Renderiza un número de segundos como `XmYs` / `Xs` / `Xh Ym`.

    Acepta None y devuelve "—" para que las plantillas no tengan que
    chequear antes de pasarlo al filter.
    """
    if seconds is None:
        return "—"
    try:
        total = int(seconds)
    except (TypeError, ValueError):
        return "—"
    if total < 60:
        return f"{total}s"
    minutes, secs = divmod(total, 60)
    if minutes < 60:
        return f"{minutes}m {secs}s" if secs else f"{minutes}m"
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins}m" if mins else f"{hours}h"


templates.env.filters["format_duration"] = _format_duration
