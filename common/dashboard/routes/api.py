"""Endpoints JSON / fragmentos HTML consumidos por el cliente (polling)."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from common.dashboard.services.setup_check import build_setup_context
from common.dashboard.templating import templates

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
