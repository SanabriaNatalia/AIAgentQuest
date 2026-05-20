"""Aplicación FastAPI del dashboard arcano."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from common.dashboard.routes import health, pages

_DASHBOARD_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _DASHBOARD_DIR / "static"
_REPO_ROOT = _DASHBOARD_DIR.parent.parent
_ASSETS_DIR = _REPO_ROOT / "assets"


def create_app() -> FastAPI:
    app = FastAPI(
        title="Arkanum Dashboard",
        description="Sala de trofeos del aprendiz",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
    )

    if _STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    if _ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(_ASSETS_DIR)), name="assets")

    app.include_router(health.router)
    app.include_router(pages.router)

    return app


app = create_app()
