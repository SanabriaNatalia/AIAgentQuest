"""Endpoint /health usado por el lifecycle para validar que el server vive."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
