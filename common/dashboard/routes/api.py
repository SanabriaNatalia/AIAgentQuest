"""Endpoints JSON / fragmentos HTML consumidos por el cliente (polling)."""
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response

from common.dashboard.services.markdown import pygments_css
from common.dashboard.services.quest_catalog import quest_by_slug
from common.dashboard.services.setup_check import build_setup_context
from common.dashboard.templating import templates
from common.progress.db import get_connection, init_db

router = APIRouter()


@router.get("/api/setup/status", response_class=HTMLResponse)
def setup_status_fragment(request: Request):
    """Fragmento HTML del panel de setup. Cliente lo embebe via poll."""
    ctx = build_setup_context()
    return templates.TemplateResponse(
        request,
        "partials/setup_panel.html",
        {"request": request, **ctx},
    )


@router.get("/api/pygments.css")
def pygments_stylesheet() -> Response:
    """CSS generado dinámicamente por Pygments según el theme configurado."""
    return Response(content=pygments_css(), media_type="text/css")


@router.post("/api/quests/{slug}/mark-read")
def mark_quest_read(slug: str) -> JSONResponse:
    quest = quest_by_slug(slug)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest desconocida.")

    init_db()
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO quest_reading (quest_id, read_at) VALUES (?, ?)",
            (quest.db_id, now),
        )
    return JSONResponse({"slug": slug, "read_at": now})
