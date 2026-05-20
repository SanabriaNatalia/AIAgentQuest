"""Rutas HTML del dashboard. En Fase 2: perfil + placeholders de mapa/rangos."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from common.dashboard.services.progress import (
    get_apprentice,
    get_completed_count,
    get_current_quest,
    get_quest_status_map,
    get_xp_breakdown,
)
from common.dashboard.services.quest_catalog import ACTS, QUESTS
from common.dashboard.templating import templates

ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII"}

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
    status_map = get_quest_status_map()
    acts_data = []
    for num in (1, 2, 3, 4):
        act = ACTS[num]
        quests = [q for q in QUESTS if q.act == num]
        acts_data.append({"act": act, "quests": quests, "roman": ROMAN[num]})
    return templates.TemplateResponse(
        request,
        "map.html",
        {
            "request": request,
            "acts_data": acts_data,
            "status_map": status_map,
            "roman": ROMAN,
        },
    )


@router.get("/ranks", response_class=HTMLResponse)
def ranks_page(request: Request):
    status_map = get_quest_status_map()
    return templates.TemplateResponse(
        request,
        "ranks.html",
        {
            "request": request,
            "quests": QUESTS,
            "status_map": status_map,
            "roman": ROMAN,
        },
    )
