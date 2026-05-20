"""Rutas HTML del dashboard."""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from common.dashboard.services.hints import (
    get_hint,
    list_hints_for,
)
from common.dashboard.services.markdown import (
    render_markdown_file,
    resolve_codex_path,
    resolve_quest_readme,
)
from common.dashboard.services.progress import (
    get_apprentice,
    get_completed_count,
    get_current_quest,
    get_quest_status_map,
    get_xp_breakdown,
    is_quest_readme_read,
)
from common.dashboard.services.quest_catalog import ACTS, QUESTS, quest_by_slug
from common.dashboard.services.setup_check import build_setup_context
from common.dashboard.templating import templates

ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII"}

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def profile_page(request: Request):
    apprentice = get_apprentice()
    context: dict = {"request": request, "apprentice": apprentice}
    context.update(build_setup_context())

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


@router.get("/setup", response_class=HTMLResponse)
def setup_page(request: Request):
    return templates.TemplateResponse(
        request,
        "setup.html",
        {"request": request, **build_setup_context()},
    )


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


@router.get("/quest/{slug}", response_class=HTMLResponse)
def quest_page(request: Request, slug: str):
    quest = quest_by_slug(slug)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest no encontrada en el grimorio.")

    status_map = get_quest_status_map()
    status = status_map.get(slug, "locked")

    if status == "locked":
        return templates.TemplateResponse(
            request,
            "quest_view.html",
            {
                "request": request,
                "quest": quest,
                "status": status,
                "rendered": None,
                "act": ACTS[quest.act],
                "roman": ROMAN,
            },
        )

    readme_path = resolve_quest_readme(slug)
    if readme_path is None:
        raise HTTPException(
            status_code=404,
            detail="README del quest no existe en el repositorio.",
        )

    rendered = render_markdown_file(readme_path)
    hints = list_hints_for(quest)
    hint_contents: dict[int, str] = {}
    for meta in hints:
        if meta.requested:
            rendered_hint = get_hint(quest, meta.level)
            if rendered_hint is not None:
                hint_contents[meta.level] = rendered_hint.html

    return templates.TemplateResponse(
        request,
        "quest_view.html",
        {
            "request": request,
            "quest": quest,
            "status": status,
            "rendered": rendered,
            "act": ACTS[quest.act],
            "roman": ROMAN,
            "already_read": is_quest_readme_read(quest.db_id),
            "hints": hints,
            "hint_contents": hint_contents,
        },
    )


@router.get("/celebrate", response_class=HTMLResponse)
def celebrate_page(request: Request, quest: str | None = None):
    from common.dashboard.services.quest_catalog import quest_by_db_id
    from common.dashboard.services.celebration import build_celebration_context

    quest_meta = quest_by_slug(quest) if quest else None
    if quest_meta is None and quest:
        quest_meta = quest_by_db_id(quest)

    context = build_celebration_context(quest_meta)
    context["request"] = request
    return templates.TemplateResponse(request, "celebrate.html", context)


@router.get("/codex", response_class=HTMLResponse)
@router.get("/codex/{path:path}", response_class=HTMLResponse)
def codex_page(request: Request, path: str = ""):
    resolved = resolve_codex_path(path)
    if resolved is None:
        raise HTTPException(
            status_code=404,
            detail="Pergamino no encontrado en el Códex.",
        )

    rendered = render_markdown_file(resolved)
    crumbs = _build_codex_crumbs(path)
    return templates.TemplateResponse(
        request,
        "codex_view.html",
        {
            "request": request,
            "rendered": rendered,
            "crumbs": crumbs,
            "path": path,
        },
    )


def _build_codex_crumbs(path: str) -> list[dict[str, str]]:
    crumbs: list[dict[str, str]] = [{"label": "Códex", "href": "/codex"}]
    if not path:
        return crumbs
    accumulated: list[str] = []
    for part in path.strip("/").split("/"):
        accumulated.append(part)
        crumbs.append(
            {
                "label": part.replace("_", " "),
                "href": "/codex/" + "/".join(accumulated),
            }
        )
    return crumbs
