"""Rutas HTML del dashboard. En Fase 2: perfil + placeholders de mapa/rangos."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from common.dashboard.services.progress import (
    get_apprentice,
    get_completed_count,
    get_current_quest,
    get_xp_breakdown,
)
from common.dashboard.services.quest_catalog import ACTS
from common.dashboard.templating import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def profile_page(request: Request):
    apprentice = get_apprentice()
    context: dict = {"request": request, "apprentice": apprentice}

    if apprentice:
        level, xp_in_level, xp_required, xp_pct = get_xp_breakdown(apprentice.xp)
        current_quest = get_current_quest()
        if current_quest:
            act_info = f"Acto {current_quest.act} · {ACTS[current_quest.act].name}"
        else:
            act_info = "Travesía completada"

        context.update(
            level=level,
            xp_in_level=xp_in_level,
            xp_required=xp_required,
            xp_pct=xp_pct,
            completed_count=get_completed_count(),
            act_info=act_info,
        )

    return templates.TemplateResponse(request, "profile.html", context)


@router.get("/map", response_class=HTMLResponse)
def map_page(request: Request):
    return templates.TemplateResponse(
        request,
        "coming_soon.html",
        {"request": request, "page_name": "Mapa del Laboratorio"},
    )


@router.get("/ranks", response_class=HTMLResponse)
def ranks_page(request: Request):
    return templates.TemplateResponse(
        request,
        "coming_soon.html",
        {"request": request, "page_name": "Galería de Rangos"},
    )
