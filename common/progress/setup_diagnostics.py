"""Diagnósticos de setup del laboratorio.

Compartido entre el CLI (`arkanum doctor`) y el dashboard
(`/api/setup/status`). Las validaciones son puras y devuelven dataclasses
serializables; cualquier I/O lento (ping a Gemini) está cacheado en
`.setup_cache.json` para no penalizar el polling del front.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

CheckStatus = Literal["ok", "warn", "fail"]

CACHE_FILE = Path(".setup_cache.json")
CACHE_TTL_OK_SECONDS = 24 * 3600
CRITICAL_PACKAGES: tuple[str, ...] = (
    "google.genai",
    "fastapi",
    "rich",
    "typer",
    "jinja2",
    "httpx",
    "psutil",
)


@dataclass(frozen=True)
class SetupCheck:
    id: str
    label: str
    status: CheckStatus
    detail: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def run_setup_diagnostics(skip_api_ping: bool = False) -> list[SetupCheck]:
    """Ejecuta todos los checks. El orden refleja prerrequisitos lógicos."""
    api_present, api_valid = _check_api_key(skip_ping=skip_api_ping)
    return [
        _check_python(),
        _check_uv(),
        _check_dependencies(),
        _check_env_file(),
        api_present,
        api_valid,
        _check_database(),
        _check_dashboard(),
        _check_workspace(),
    ]


def count_statuses(checks: list[SetupCheck]) -> dict[str, int]:
    counts = {"ok": 0, "warn": 0, "fail": 0}
    for check in checks:
        counts[check.status] += 1
    return counts


# === Checks individuales ===

def _check_python() -> SetupCheck:
    info = sys.version_info
    version = f"{info.major}.{info.minor}.{info.micro}"
    if (info.major, info.minor) >= (3, 12):
        return SetupCheck("python_version", "Python ≥ 3.12", "ok", f"detectado {version}")
    return SetupCheck(
        "python_version",
        "Python ≥ 3.12",
        "fail",
        f"detectado {version}, se requiere 3.12+",
    )


def _check_uv() -> SetupCheck:
    if shutil.which("uv"):
        out = _safe_subprocess(["uv", "--version"])
        if out:
            return SetupCheck("uv_available", "uv en PATH", "ok", out)

    out = _safe_subprocess([sys.executable, "-m", "uv", "--version"])
    if out:
        return SetupCheck(
            "uv_available",
            "uv disponible",
            "warn",
            f"{out} · accesible solo vía `python -m uv`",
        )

    return SetupCheck(
        "uv_available",
        "uv disponible",
        "fail",
        "no encontrado · instala desde astral.sh/uv",
    )


def _safe_subprocess(cmd: list[str]) -> str | None:
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.STDOUT, timeout=5
        ).strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, FileNotFoundError):
        return None


def _check_dependencies() -> SetupCheck:
    missing = [pkg for pkg in CRITICAL_PACKAGES if importlib.util.find_spec(pkg) is None]
    if missing:
        return SetupCheck(
            "dependencies",
            "Dependencias críticas",
            "fail",
            f"faltan {len(missing)}: {', '.join(missing)} · ejecuta `uv sync`",
        )
    return SetupCheck(
        "dependencies",
        "Dependencias críticas",
        "ok",
        f"{len(CRITICAL_PACKAGES)} paquetes presentes",
    )


def _check_env_file() -> SetupCheck:
    if Path(".env").exists():
        return SetupCheck("env_file", "Archivo .env presente", "ok")
    return SetupCheck(
        "env_file",
        "Archivo .env presente",
        "fail",
        "no existe · copia .env.example",
    )


def _check_api_key(skip_ping: bool) -> tuple[SetupCheck, SetupCheck]:
    api_key = _read_gemini_key()
    if not api_key:
        return (
            SetupCheck(
                "api_key_present",
                "GEMINI_API_KEY configurada",
                "fail",
                "ausente o vacía",
            ),
            SetupCheck(
                "api_key_valid",
                "API key validada",
                "fail",
                "no se puede validar sin clave",
            ),
        )

    present = SetupCheck(
        "api_key_present",
        "GEMINI_API_KEY configurada",
        "ok",
        f"longitud {len(api_key)}",
    )

    if skip_ping:
        cached = _read_cache_for_key(api_key)
        if cached == "ok":
            return present, SetupCheck(
                "api_key_valid", "API key validada", "ok", "cacheada (ping reciente)"
            )
        return present, SetupCheck(
            "api_key_valid", "API key validada", "warn", "ping omitido"
        )

    return present, _validate_api_key(api_key)


def _read_gemini_key() -> str | None:
    env_path = Path(".env")
    if env_path.exists():
        try:
            from dotenv import dotenv_values

            values = dotenv_values(env_path)
            key = (values.get("GEMINI_API_KEY") or "").strip().strip("'\"")
            if key:
                return key
        except ImportError:
            pass
        except OSError:
            pass

    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    return env_key or None


def _validate_api_key(api_key: str) -> SetupCheck:
    cached = _read_cache_for_key(api_key)
    if cached == "ok":
        return SetupCheck(
            "api_key_valid", "API key validada", "ok", "cacheada (ping reciente)"
        )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        client.models.generate_content(
            model="gemini-2.5-flash",
            contents="hi",
            config=types.GenerateContentConfig(max_output_tokens=5, temperature=0),
        )
        _write_cache_for_key(api_key, "ok")
        return SetupCheck("api_key_valid", "API key validada", "ok", "ping exitoso")
    except Exception as exc:
        from common.gemini_errors import classify_gemini_error

        err = classify_gemini_error(exc)
        # Un 429 (cuota/rate) NO significa que la clave esté mal: el ping no
        # debe marcarla inválida ni bloquear el onboarding por ello. Idem un
        # problema temporal de servidor o de red. Solo auth/desconocido → fail.
        if err.kind == "quota":
            return SetupCheck(
                "api_key_valid", "API key validada", "warn",
                "cuota/rate de Gemini topada (la clave es válida; espera y reintenta)",
            )
        if err.kind in ("server", "network"):
            return SetupCheck(
                "api_key_valid", "API key validada", "warn", err.title.lower(),
            )
        return SetupCheck(
            "api_key_valid",
            "API key validada",
            "fail",
            f"{type(exc).__name__}: {str(exc)[:80]}",
        )


def _read_cache_for_key(api_key: str) -> str | None:
    if not CACHE_FILE.exists():
        return None
    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    if data.get("api_key_hash") != _hash_key(api_key):
        return None
    if data.get("result") != "ok":
        return None
    if (time.time() - data.get("validated_at", 0)) > CACHE_TTL_OK_SECONDS:
        return None
    return "ok"


def _write_cache_for_key(api_key: str, result: str) -> None:
    payload = {
        "api_key_hash": _hash_key(api_key),
        "validated_at": time.time(),
        "result": result,
    }
    try:
        CACHE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError:
        pass


def _hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def _check_database() -> SetupCheck:
    db_path = Path(".quest_progress.db")
    if not db_path.exists():
        return SetupCheck(
            "database",
            "Base de datos inicializada",
            "warn",
            "se creará al registrar un aprendiz",
        )

    try:
        from common.progress.db import get_connection, init_db

        init_db()
        with get_connection() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
        return SetupCheck(
            "database",
            "Base de datos inicializada",
            "ok",
            f"{len(tables)} tablas",
        )
    except Exception as exc:
        return SetupCheck(
            "database",
            "Base de datos inicializada",
            "fail",
            f"{type(exc).__name__}: {str(exc)[:80]}",
        )


def _check_dashboard() -> SetupCheck:
    try:
        from common.dashboard.lifecycle import status

        info = status()
    except Exception as exc:
        return SetupCheck(
            "dashboard",
            "Dashboard activo",
            "fail",
            f"{type(exc).__name__}: {str(exc)[:80]}",
        )

    if info.get("running"):
        return SetupCheck(
            "dashboard",
            "Dashboard activo",
            "ok",
            f"PID {info['pid']} · puerto {info['port']}",
        )
    return SetupCheck("dashboard", "Dashboard activo", "warn", "inactivo")


def _check_workspace() -> SetupCheck:
    workspace = Path("workspace")
    if not workspace.exists():
        return SetupCheck(
            "workspace",
            "workspace/ presente",
            "warn",
            "no existe; se usará en Acto II",
        )
    try:
        files = sum(
            1
            for p in workspace.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        )
        return SetupCheck("workspace", "workspace/ presente", "ok", f"{files} archivos")
    except OSError as exc:
        return SetupCheck("workspace", "workspace/ presente", "fail", str(exc))
