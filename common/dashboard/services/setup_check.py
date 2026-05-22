"""Builder de contexto del panel de setup, consumido por /, /setup y /api/setup/status."""
from __future__ import annotations

from common.progress.setup_diagnostics import (
    count_statuses,
    run_setup_diagnostics,
)
from common.progress.setup_remedies import remedy_for


def build_setup_context(skip_api_ping: bool = True) -> dict:
    """Por defecto saltea el ping real y usa cache.

    El ping real se hace una vez al día desde `arkanum doctor` o desde
    el wizard de init_user (Fase 8); el polling del dashboard no debe
    quemar la cuota de Gemini.

    Devuelve también `issues`: lista (en el mismo orden que `checks`) con
    los checks en estado `warn`/`fail` junto a su receta de reparación.
    El template renderiza esta lista solo cuando hay algo que arreglar.
    """
    checks = run_setup_diagnostics(skip_api_ping=skip_api_ping)
    issues = []
    for check in checks:
        if check.status == "ok":
            continue
        remedy = remedy_for(check.id)
        issues.append(
            {
                "check": check.to_dict(),
                "remedy": remedy.to_dict() if remedy else None,
            }
        )
    return {
        "checks": checks,
        "counts": count_statuses(checks),
        "issues": issues,
    }
