"""Builder de contexto del panel de setup, consumido por /, /setup y /api/setup/status."""
from __future__ import annotations

from common.progress.setup_diagnostics import (
    count_statuses,
    run_setup_diagnostics,
)


def build_setup_context(skip_api_ping: bool = True) -> dict:
    """Por defecto saltea el ping real y usa cache.

    El ping real se hace una vez al día desde `arkanum doctor` o desde
    el wizard de init_user (Fase 8); el polling del dashboard no debe
    quemar la cuota de Gemini.
    """
    checks = run_setup_diagnostics(skip_api_ping=skip_api_ping)
    return {
        "checks": checks,
        "counts": count_statuses(checks),
    }
