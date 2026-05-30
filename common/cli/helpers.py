"""Helpers compartidos entre los comandos `arkanum *`.

- `resolve_quest_by_number(n)`: traduce un número de quest (1..8) a su
  `QuestMeta`. Lanza `typer.BadParameter` si está fuera de rango.
- `starter_module(quest)` / `check_module(quest)`: devuelven el path
  importable (`quests.quest_NN_*.starter.main` / `.check`) para pasar
  a `python -m`.
- `run_module(module_path, extra_args)`: ejecuta el módulo como
  subprocess en el mismo intérprete; devuelve el returncode.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import typer

from common.dashboard.services.quest_catalog import QUESTS, QuestMeta

REPO_ROOT = Path(__file__).resolve().parents[2]


def _utf8_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Env para subprocess que fuerza UTF-8 en stdout/stderr del hijo.

    Sin esto, en Windows con consola en español Python usa cp1252 y
    revienta al imprimir emojis (`✅`, `🤖`, etc.). `PYTHONIOENCODING`
    cubre stdin/stdout/stderr; `PYTHONUTF8=1` activa el modo UTF-8 global.
    """
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    if extra:
        env.update(extra)
    return env


def resolve_quest_by_number(n: int) -> QuestMeta:
    matches = [q for q in QUESTS if q.order == n]
    if not matches:
        raise typer.BadParameter(
            f"No existe quest #{n}. El laboratorio contiene quests 1..{len(QUESTS)}."
        )
    return matches[0]


def starter_module(quest: QuestMeta) -> str:
    return f"quests.{quest.slug}.starter.main"


def check_module(quest: QuestMeta) -> str:
    return f"quests.{quest.slug}.check"


def starter_path(quest: QuestMeta) -> Path:
    return REPO_ROOT / "quests" / quest.slug / "starter" / "main.py"


def check_path(quest: QuestMeta) -> Path:
    return REPO_ROOT / "quests" / quest.slug / "check.py"


def run_module(
    module_path: str,
    extra_args: list[str] | None = None,
    env_extra: dict[str, str] | None = None,
) -> int:
    cmd = [sys.executable, "-m", module_path]
    if extra_args:
        cmd.extend(extra_args)
    try:
        result = subprocess.run(cmd, cwd=str(REPO_ROOT), env=_utf8_env(env_extra))
        return result.returncode
    except KeyboardInterrupt:
        return 130


def run_module_capturing(
    module_path: str,
    extra_args: list[str] | None = None,
    on_line=None,  # type: ignore[no-untyped-def]
    env_extra: dict[str, str] | None = None,
) -> tuple[int, str]:
    """Ejecuta `python -m module_path` haciendo `tee` de stdout.

    Reemite cada línea al stdout del padre (para que el aprendiz vea el
    progreso en tiempo real), la acumula en un buffer, y opcionalmente
    invoca `on_line(line)` por cada línea (útil para streaming de traces).
    Errores dentro de `on_line` se loguean a stderr pero NO matan el
    subprocess. Devuelve `(returncode, captured_stdout)`.
    """
    cmd = [sys.executable, "-u", "-m", module_path]
    if extra_args:
        cmd.extend(extra_args)

    env = _utf8_env(env_extra)

    captured: list[str] = []
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
    except OSError as exc:
        return 1, f"[arkanum] No se pudo arrancar el subprocess: {exc}"

    assert proc.stdout is not None
    try:
        for line in proc.stdout:
            captured.append(line)
            sys.stdout.write(line)
            sys.stdout.flush()
            if on_line is not None:
                try:
                    on_line(line)
                except Exception as exc:  # noqa: BLE001 — best effort
                    sys.stderr.write(f"[arkanum] on_line falló: {exc!r}\n")
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()
        return 130, "".join(captured)

    return proc.returncode or 0, "".join(captured)
