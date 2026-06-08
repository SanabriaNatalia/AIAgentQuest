"""Lifecycle del servidor del dashboard.

Maneja arranque detached, parada limpia, validación con psutil y persistencia
del PID/puerto en archivos del repo. El servidor sobrevive al cierre de la
terminal y se valida tanto por PID como por nombre de proceso para evitar
colisiones con PIDs reciclados.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import psutil

PID_FILE = Path(".quest_progress.pid")
PORT_FILE = Path(".quest_dashboard.port")
LOG_FILE = Path(".quest_dashboard.log")

_PORT_CANDIDATES = (8765, 8766, 8767, 8768)
_MODULE_MARKER = "common.dashboard"


def is_running() -> bool:
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return False
    return _is_our_process(pid)


def _is_our_process(pid: int) -> bool:
    if not psutil.pid_exists(pid):
        return False
    try:
        proc = psutil.Process(pid)
        cmdline = " ".join(proc.cmdline())
        return _MODULE_MARKER in cmdline
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def status() -> dict:
    if not is_running():
        return {"running": False, "pid": None, "port": None, "uptime": None}

    pid = int(PID_FILE.read_text(encoding="utf-8").strip())
    port: int | None = None
    if PORT_FILE.exists():
        try:
            port = int(PORT_FILE.read_text(encoding="utf-8").strip())
        except (ValueError, OSError):
            port = None

    try:
        proc = psutil.Process(pid)
        uptime = int(time.time() - proc.create_time())
    except psutil.NoSuchProcess:
        return {"running": False, "pid": None, "port": None, "uptime": None}

    return {"running": True, "pid": pid, "port": port, "uptime": uptime}


def start(
    detached: bool = True,
    dev: bool = False,
    wait_for_health: bool = True,
    health_timeout: float | None = None,
) -> int:
    if dev:
        if is_running():
            stop()
        port = _find_free_port()
        _run_foreground_dev(port)
        return 0

    if is_running():
        return int(PID_FILE.read_text(encoding="utf-8").strip())

    port = _find_free_port()
    pid = _spawn_detached(port)
    PID_FILE.write_text(str(pid), encoding="utf-8")
    PORT_FILE.write_text(str(port), encoding="utf-8")

    if wait_for_health:
        if health_timeout is None:
            health_timeout = float(
                os.environ.get("ARKANUM_DASHBOARD_HEALTH_TIMEOUT", "20")
            )
        if not _wait_for_health(port, timeout=health_timeout):
            raise RuntimeError(
                f"El servidor no respondió al health check en {health_timeout:.0f}s. "
                "Probablemente siga arrancando en segundo plano (arranque en frío, "
                "habitual la primera vez). Espera unos segundos y ábrelo con "
                "`arkanum dashboard open`. Si no aparece, revisa el error real con "
                f"`arkanum dashboard logs` (o {LOG_FILE}). Para máquinas lentas puedes "
                "ampliar la espera con la variable ARKANUM_DASHBOARD_HEALTH_TIMEOUT."
            )

    return pid


def stop() -> bool:
    if not PID_FILE.exists():
        _clean_state()
        return False

    try:
        pid = int(PID_FILE.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        _clean_state()
        return False

    killed = False
    if _is_our_process(pid):
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
            killed = True
        except psutil.NoSuchProcess:
            pass

    _clean_state()
    return killed


def ensure_started() -> None:
    if os.environ.get("ARKANUM_NO_DASHBOARD") == "1":
        return
    if is_running():
        return
    try:
        start(detached=True, wait_for_health=False)
    except Exception:
        pass


def _clean_state() -> None:
    PID_FILE.unlink(missing_ok=True)
    PORT_FILE.unlink(missing_ok=True)


def _find_free_port() -> int:
    for port in _PORT_CANDIDATES:
        if _port_available(port):
            return port
    raise RuntimeError(
        f"No hay puertos libres en el rango {_PORT_CANDIDATES[0]}-{_PORT_CANDIDATES[-1]}"
    )


def _port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def _spawn_detached(port: int) -> int:
    log_handle = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
    cmd = [sys.executable, "-m", "common.dashboard", "--port", str(port)]

    popen_kwargs: dict = {
        "stdin": subprocess.DEVNULL,
        "stdout": log_handle,
        "stderr": log_handle,
        "close_fds": True,
    }

    if sys.platform == "win32":
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        popen_kwargs["creationflags"] = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs["start_new_session"] = True

    proc = subprocess.Popen(cmd, **popen_kwargs)
    return proc.pid


def _run_foreground_dev(port: int) -> None:
    import uvicorn

    PORT_FILE.write_text(str(port), encoding="utf-8")
    try:
        uvicorn.run(
            "common.dashboard.server:app",
            host="127.0.0.1",
            port=port,
            reload=True,
        )
    finally:
        PORT_FILE.unlink(missing_ok=True)


def _wait_for_health(port: int, timeout: float) -> bool:
    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{port}/health"
    while time.time() < deadline:
        try:
            response = httpx.get(url, timeout=0.5)
            if response.status_code == 200:
                return True
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.HTTPError):
            pass
        time.sleep(0.1)
    return False
