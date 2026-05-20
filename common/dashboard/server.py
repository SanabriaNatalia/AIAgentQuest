"""Aplicación FastAPI del dashboard arcano.

En Fase 1 solo expone /health. Las rutas reales se agregan en fases siguientes.
"""
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="Arkanum Dashboard",
        description="Sala de trofeos del aprendiz",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
    )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
