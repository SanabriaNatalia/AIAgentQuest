"""Endpoints JSON / fragmentos HTML consumidos por el cliente (polling)."""
import json
import re
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response

from common.dashboard.services.hints import (
    HintRequestError,
    get_hint,
    list_hints_for,
    request_hint,
)
from common.dashboard.services.markdown import pygments_css
from common.dashboard.services.quest_catalog import quest_by_slug
from common.dashboard.services.setup_check import build_setup_context
from common.dashboard.templating import templates
from common.progress.db import (
    get_connection,
    get_quest_progress,
    init_db,
    register_first_attempt,
)

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


def _read_events(only_unseen: bool, limit: int, mark_seen: bool) -> list[dict]:
    init_db()
    where = "WHERE seen = 0" if only_unseen else ""
    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT id, kind, payload, created_at FROM events "
            f"{where} ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        if mark_seen and rows:
            ids = [r[0] for r in rows]
            placeholders = ",".join(["?"] * len(ids))
            conn.execute(
                f"UPDATE events SET seen = 1 WHERE id IN ({placeholders})",
                ids,
            )

    items: list[dict] = []
    for ev_id, kind, payload, created_at in rows:
        try:
            parsed = json.loads(payload)
        except (TypeError, ValueError):
            parsed = {"raw": payload}
        items.append(
            {"id": ev_id, "kind": kind, "payload": parsed, "created_at": created_at}
        )
    return items


@router.get("/api/events/recent")
def recent_events(limit: int = Query(20, ge=1, le=200)) -> JSONResponse:
    """Consume eventos: devuelve los no vistos y los marca como `seen=1`.

    Usado por `webbrowser.open` auto-flow. La transición a seen=1 se hace
    en el mismo commit que la SELECT para evitar repetir notificaciones.
    """
    return JSONResponse({"events": _read_events(only_unseen=True, limit=limit, mark_seen=True)})


@router.get("/api/events/peek")
def peek_events(limit: int = Query(5, ge=1, le=50)) -> JSONResponse:
    """Mira los eventos no vistos sin marcarlos. Usado por el toast del perfil.

    El cliente decide cuándo "dismiss" via POST /api/events/{id}/dismiss.
    """
    return JSONResponse({"events": _read_events(only_unseen=True, limit=limit, mark_seen=False)})


@router.post("/api/events/{event_id}/dismiss")
def dismiss_event(event_id: int) -> JSONResponse:
    init_db()
    with get_connection() as conn:
        cur = conn.execute("UPDATE events SET seen = 1 WHERE id = ?", (event_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Evento no encontrado.")
    return JSONResponse({"ok": True, "event_id": event_id})


def _serialize_hint(meta) -> dict:
    return {
        "level": meta.level,
        "title": meta.title,
        "description": meta.description,
        "file_exists": meta.file_exists,
        "eligible": meta.eligible,
        "requested": meta.requested,
        "requested_at": meta.requested_at,
    }


@router.get("/api/quests/{slug}/hints")
def list_quest_hints(slug: str) -> JSONResponse:
    """Estado actual de las 3 pistas del quest. Sólo metadatos; el contenido
    se obtiene cuando la pista ha sido solicitada."""
    quest = quest_by_slug(slug)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest desconocida.")

    hints = list_hints_for(quest)
    return JSONResponse({
        "slug": slug,
        "hints": [_serialize_hint(h) for h in hints],
    })


@router.post("/api/quests/{slug}/hints/{level}")
def request_quest_hint(slug: str, level: int) -> JSONResponse:
    """Marca una pista como solicitada y devuelve su contenido renderizado.

    Valida orden estricto del lado servidor: la II requiere la I, la III
    requiere la II. Idempotente: pedir la misma pista dos veces no duplica.
    """
    quest = quest_by_slug(slug)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest desconocida.")

    try:
        requested_at = request_hint(quest, level)
    except HintRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    rendered = get_hint(quest, level)
    return JSONResponse({
        "slug": slug,
        "level": level,
        "requested_at": requested_at,
        "html": rendered.html if rendered else "",
    })


_SYSTEM_PROMPT_PATH = Path("common/prompts/system_prompt.py")
_SYSTEM_PROMPT_TRIPLE_RE = re.compile(
    r"""system_prompt\s*=\s*(?:r?["']{3})(.*?)(?:["']{3})""",
    re.DOTALL,
)
_SYSTEM_PROMPT_PLACEHOLDER_HINT = "Escribe tu prompt del sistema aquí"


@router.get("/api/system-prompt")
def system_prompt_endpoint() -> JSONResponse:
    """Devuelve el system_prompt activo, leyendo el archivo del repo.

    Se lee el archivo en cada request para que el aprendiz pueda editarlo
    sin reiniciar el dashboard. Si el archivo no existe o el regex no
    matchea, devolvemos `content=""` con `error` explicativo.
    """
    if not _SYSTEM_PROMPT_PATH.exists():
        return JSONResponse({
            "content": "",
            "is_placeholder": False,
            "error": f"No existe {_SYSTEM_PROMPT_PATH}",
        })

    raw = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    m = _SYSTEM_PROMPT_TRIPLE_RE.search(raw)
    content = m.group(1) if m else ""

    return JSONResponse({
        "content": content,
        "is_placeholder": _SYSTEM_PROMPT_PLACEHOLDER_HINT in content,
        "path": str(_SYSTEM_PROMPT_PATH),
    })


@router.get("/api/trace/current")
def current_trace(
    trace_id: str | None = Query(None),
    limit: int = Query(200, ge=1, le=1000),
) -> JSONResponse:
    """Pasos del trace más reciente (o uno específico). Usado por /live-agent."""
    from common.dashboard.services.trace import (
        latest_trace_summary,
        recent_steps,
        safe_parse_payload,
    )

    summary = latest_trace_summary()
    target = trace_id or (summary.trace_id if summary else None)
    steps = recent_steps(limit=limit, trace_id=target) if target else []

    return JSONResponse({
        "trace_id": target,
        "summary": (
            {
                "trace_id": summary.trace_id,
                "quest_slug": summary.quest.slug if summary.quest else None,
                "quest_title": summary.quest.title if summary.quest else None,
                "started_at": summary.started_at,
                "last_step_at": summary.last_step_at,
                "steps": summary.steps,
            }
            if summary
            else None
        ),
        "steps": [
            {
                "id": s.id,
                "trace_id": s.trace_id,
                "quest_slug": s.quest.slug if s.quest else None,
                "step_type": s.step_type,
                "name": s.name,
                "payload": safe_parse_payload(s.payload),
                "created_at": s.created_at,
            }
            for s in reversed(steps)  # cronológico para el viewer
        ],
    })


@router.post("/api/quests/{slug}/start")
def start_quest(slug: str) -> JSONResponse:
    """Marca el quest como iniciado: arranca el cronómetro de tiempo total.

    Idempotente — pulsar dos veces no resetea `started_at`. Si la quest ya
    estaba completada, devuelve 409 (no tiene sentido reiniciar).
    """
    quest = quest_by_slug(slug)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest desconocida.")

    init_db()
    with get_connection() as conn:
        already_done = conn.execute(
            "SELECT 1 FROM quest_completion WHERE quest_id = ?", (quest.db_id,)
        ).fetchone()
    if already_done is not None:
        raise HTTPException(
            status_code=409, detail="Quest ya completado; el cronómetro está sellado.",
        )

    register_first_attempt(quest.db_id)
    started_at, _ = get_quest_progress(quest.db_id)
    return JSONResponse({"slug": slug, "started_at": started_at})


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
