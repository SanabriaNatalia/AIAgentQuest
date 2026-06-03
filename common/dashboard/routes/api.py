"""Endpoints JSON / fragmentos HTML consumidos por el cliente (polling)."""
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel

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


class SystemPromptUpdate(BaseModel):
    content: str


@router.post("/api/system-prompt")
def update_system_prompt(payload: SystemPromptUpdate) -> JSONResponse:
    """Reescribe el bloque entre triple-quotes en system_prompt.py.

    Mitigaciones (mejora #18):
    - Crea un backup .system_prompt.py.bak antes de tocar el original.
    - Rechaza contenido con '\"\"\"' literal (rompería la sintaxis).
    - Solo reemplaza el primer match de la asignación system_prompt = '''...'''.
    - El cambio se aplica al próximo arkanum start (no afecta procesos en curso).
    """
    if not _SYSTEM_PROMPT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No existe {_SYSTEM_PROMPT_PATH}",
        )
    if '"""' in payload.content:
        raise HTTPException(
            status_code=400,
            detail="El contenido no puede incluir comillas triples (rompería la sintaxis).",
        )

    raw = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    if not _SYSTEM_PROMPT_TRIPLE_RE.search(raw):
        raise HTTPException(
            status_code=400,
            detail="No se encontró el bloque `system_prompt = \"\"\"...\"\"\"` en el archivo.",
        )

    backup_path = _SYSTEM_PROMPT_PATH.with_suffix(".py.bak")
    backup_path.write_text(raw, encoding="utf-8")

    new_content = payload.content
    new_raw = _SYSTEM_PROMPT_TRIPLE_RE.sub(
        lambda _m: f'system_prompt = """{new_content}"""',
        raw,
        count=1,
    )
    _SYSTEM_PROMPT_PATH.write_text(new_raw, encoding="utf-8")

    return JSONResponse({
        "ok": True,
        "path": str(_SYSTEM_PROMPT_PATH),
        "backup": str(backup_path),
        "is_placeholder": _SYSTEM_PROMPT_PLACEHOLDER_HINT in new_content,
    })


@router.get("/api/traces/recent")
def recent_traces(limit: int = Query(10, ge=1, le=50)) -> JSONResponse:
    """Lista de los N últimos traces (sin steps) para el historial."""
    from common.dashboard.services.trace import (
        recent_trace_summaries,
        trace_first_user_prompt,
    )

    summaries = recent_trace_summaries(limit=limit)
    items = []
    for s in summaries:
        items.append({
            "trace_id": s.trace_id,
            "quest_slug": s.quest.slug if s.quest else None,
            "quest_title": s.quest.title if s.quest else None,
            "quest_order": s.quest.order if s.quest else None,
            "started_at": s.started_at,
            "last_step_at": s.last_step_at,
            "steps": s.steps,
            "user_prompt": trace_first_user_prompt(s.trace_id),
        })
    return JSONResponse({"traces": items})


@router.delete("/api/traces/{trace_id}")
def delete_trace(trace_id: str) -> JSONResponse:
    """Borra todos los steps de un trace específico de `agent_traces`.

    Devuelve 404 si no existía. La operación es idempotente: borrar
    dos veces el mismo trace devuelve 404 la segunda vez.
    """
    from common.progress.db import get_connection, init_db

    init_db()
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM agent_traces WHERE trace_id = ?",
            (trace_id,),
        )
        deleted = cur.rowcount
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} no encontrado.")
    return JSONResponse({"ok": True, "deleted_steps": deleted, "trace_id": trace_id})


@router.get("/api/quests/live-agent")
def live_agent_quests() -> JSONResponse:
    """Catálogo de quests que el launcher de /live-agent puede ejecutar.

    Solo incluye quests marcadas con `live_agent=True` en QuestMeta
    (hoy Q07 y Q08). Frontend lo usa para poblar el `<select>` del
    launcher sin hardcodear las opciones.
    """
    from common.dashboard.services.quest_catalog import QUESTS

    items = [
        {
            "order": q.order,
            "slug": q.slug,
            "title": q.title,
            "default_prompt": q.live_agent_default_prompt,
        }
        for q in QUESTS
        if q.live_agent
    ]
    return JSONResponse({"quests": items})


class TraceRunRequest(BaseModel):
    quest_order: int
    prompt: str


_REPO_ROOT = Path(__file__).resolve().parents[3]


@router.post("/api/trace/run")
def trace_run(payload: TraceRunRequest) -> JSONResponse:
    """Spawnea `python -m common.cli.main run N "prompt"` en background.

    El proceso queda desligado: devolvemos inmediatamente y el polling
    normal de /live-agent se encarga de mostrar los steps a medida que
    el wrapper los emite.

    Mitigaciones (mejora #7):
    - Validamos el quest_order contra el catálogo (400 si no existe).
    - Validamos que el prompt no esté vacío (400).
    - Sandbox al cwd del repo y env UTF-8.
    - stdout/stderr a DEVNULL: el subprocess se ve solo en `/live-agent`,
      no llena el log del dashboard.
    """
    from common.dashboard.services.quest_catalog import QUESTS

    matches = [q for q in QUESTS if q.order == payload.quest_order]
    if not matches:
        raise HTTPException(
            status_code=400,
            detail=f"Quest #{payload.quest_order} no existe.",
        )
    quest = matches[0]
    if not quest.live_agent:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Quest #{quest.order} no soporta el visualizador en vivo. "
                "Solo Q07 y Q08 emiten traces que /live-agent pueda mostrar."
            ),
        )
    prompt = (payload.prompt or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="El prompt no puede estar vacío.")
    cmd = [
        sys.executable,
        "-m",
        "common.cli.main",
        "run",
        str(quest.order),
        prompt,
    ]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    popen_kwargs: dict = {
        "cwd": str(_REPO_ROOT),
        "env": env,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "stdin": subprocess.DEVNULL,
    }
    if sys.platform == "win32":
        popen_kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )
    else:
        popen_kwargs["start_new_session"] = True

    try:
        subprocess.Popen(cmd, **popen_kwargs)
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo lanzar el subprocess: {exc}",
        ) from exc

    return JSONResponse({
        "status": "started",
        "quest_order": quest.order,
        "quest_slug": quest.slug,
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
        trace_summary_for,
    )

    if trace_id:
        summary = trace_summary_for(trace_id)
        target = summary.trace_id if summary else trace_id
    else:
        summary = latest_trace_summary()
        target = summary.trace_id if summary else None
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
                "seconds_since_last_step": summary.seconds_since_last_step,
                "has_session_end": summary.has_session_end,
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
