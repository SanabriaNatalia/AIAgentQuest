"""Notificaciones best-effort entre `record_quest_completion` y el dashboard.

Diseño:
- `emit_event(kind, payload)` intenta `POST /events/{kind}` al dashboard.
  Si el server no responde (timeout, no arrancado, lo que sea), persiste
  el evento directamente en la tabla `events` para que el dashboard lo
  recoja al refrescar.
- `open_celebration(quest_id)` abre el browser en `/celebrate?quest=...`
  con un throttle de 5s (vía `.last_celebrate.timestamp`) para evitar
  múltiples pestañas si se completan quests seguidas.
- Ambos respetan `ARKANUM_NO_DASHBOARD=1`. `open_celebration` además
  respeta `ARKANUM_NO_CELEBRATION=1` (útil en CI o cuando solo quieres
  el evento sin que se te abra el browser).
"""
from __future__ import annotations

import json
import os
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import httpx

from common.progress.db import get_connection, init_db

PORT_FILE = Path(".quest_dashboard.port")
LAST_CELEBRATE_FILE = Path(".last_celebrate.timestamp")

_HTTP_TIMEOUT = 0.3
_CELEBRATION_THROTTLE_SECONDS = 5.0


def _is_disabled() -> bool:
    return os.environ.get("ARKANUM_NO_DASHBOARD") == "1"


def _read_port() -> int | None:
    if not PORT_FILE.exists():
        return None
    try:
        return int(PORT_FILE.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None


def _persist_event_locally(kind: str, payload: dict) -> None:
    """Fallback: si el HTTP falla, deja el evento en la tabla `events`."""
    init_db()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO events (kind, payload, seen, created_at) VALUES (?, ?, 0, ?)",
            (kind, json.dumps(payload, ensure_ascii=False), datetime.now().isoformat(timespec="seconds")),
        )


def emit_event(kind: str, payload: dict) -> bool:
    """Notifica un evento al dashboard. Devuelve True si el POST tuvo éxito.

    Si el server está apagado o tarda más de `_HTTP_TIMEOUT`, persiste el
    evento en la tabla `events` para que el dashboard lo recoja al volver.
    Si `ARKANUM_NO_DASHBOARD=1`, no hace nada (ni persiste).
    """
    if _is_disabled():
        return False

    port = _read_port()
    if port is not None:
        url = f"http://127.0.0.1:{port}/events/{kind}"
        try:
            response = httpx.post(url, json=payload, timeout=_HTTP_TIMEOUT)
            if response.status_code < 400:
                return True
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.HTTPError, OSError):
            pass

    try:
        _persist_event_locally(kind, payload)
    except Exception:
        pass
    return False


def _read_last_celebrate_ts() -> float:
    if not LAST_CELEBRATE_FILE.exists():
        return 0.0
    try:
        return float(LAST_CELEBRATE_FILE.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return 0.0


def _write_last_celebrate_ts(value: float) -> None:
    try:
        LAST_CELEBRATE_FILE.write_text(f"{value:.3f}", encoding="utf-8")
    except OSError:
        pass


def open_celebration(quest_id: str) -> bool:
    """Abre el browser en `/celebrate?quest=...` con throttle.

    Devuelve True si efectivamente lanzó el browser. False si el opt-out
    aplica, si el throttle bloqueó la apertura, o si no hay puerto válido.
    """
    if _is_disabled() or os.environ.get("ARKANUM_NO_CELEBRATION") == "1":
        return False

    now = time.time()
    if now - _read_last_celebrate_ts() < _CELEBRATION_THROTTLE_SECONDS:
        return False

    port = _read_port()
    if port is None:
        return False

    url = f"http://127.0.0.1:{port}/celebrate?quest={quote(quest_id, safe='')}"
    try:
        opened = webbrowser.open(url, new=2)
    except Exception:
        return False

    if opened:
        _write_last_celebrate_ts(now)
    return opened
