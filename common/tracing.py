"""Emisor de trace estructurado para el Live Agent (F16 / adenda 2026-05-29).

Cuando una solución/starter de Q07-Q08 quiere emitir un evento al
visualizador `/live-agent` además de imprimir a stdout, llama:

    from common.tracing import emit
    emit("agent_thought", payload={"text": razonamiento})

El módulo es opt-in y silencioso: si `ARKANUM_TRACE_ID` no está en el
entorno (la quest se corrió fuera de `arkanum run`), no hace nada. Si
el dashboard no responde, swallow el error sin tocar el flujo del agente.

El regex de `common/cli/commands/run.py` sigue activo como fallback
para starters que no usen este módulo — los dos caminos conviven sin
duplicar steps porque emiten `step_type` diferentes.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

_DEFAULT_URL = "http://127.0.0.1:8765/events/trace"
_ENV_TRACE_ID = "ARKANUM_TRACE_ID"
_ENV_QUEST_DB_ID = "ARKANUM_QUEST_DB_ID"
_ENV_TRACE_URL = "ARKANUM_TRACE_URL"


def trace_enabled() -> bool:
    """True si la quest fue lanzada vía `arkanum run` (hay trace_id activo)."""
    return bool(os.environ.get(_ENV_TRACE_ID))


def emit(step_type: str, name: str | None = None, payload: Any = None) -> None:
    """Envía un step al endpoint /events/trace del dashboard.

    Best-effort: si `ARKANUM_TRACE_ID` no está set, no hace nada. Si el
    dashboard no responde en 500ms, swallow el error sin lanzar excepción.
    Telemetría, no critical path — nunca interrumpe el flujo del agente.

    `payload` se serializa con `json.dumps`. Si no es serializable, se
    convierte a string vía `default=str`.
    """
    trace_id = os.environ.get(_ENV_TRACE_ID)
    if not trace_id:
        return

    body: dict[str, Any] = {
        "trace_id": trace_id,
        "step_type": step_type,
        "name": name,
        "payload": _stringify_payload(payload),
    }
    quest_db_id = os.environ.get(_ENV_QUEST_DB_ID)
    if quest_db_id:
        body["quest_db_id"] = quest_db_id

    url = os.environ.get(_ENV_TRACE_URL, _DEFAULT_URL)
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=0.5) as _resp:
            pass
    except (urllib.error.URLError, TimeoutError, OSError):
        pass


def _stringify_payload(payload: Any) -> str | None:
    if payload is None:
        return None
    if isinstance(payload, str):
        return payload
    try:
        return json.dumps(payload, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return str(payload)
