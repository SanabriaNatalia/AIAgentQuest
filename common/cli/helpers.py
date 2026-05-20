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

import subprocess
import sys
from pathlib import Path

import typer

from common.dashboard.services.quest_catalog import QUESTS, QuestMeta

REPO_ROOT = Path(__file__).resolve().parents[2]


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


def run_module(module_path: str, extra_args: list[str] | None = None) -> int:
    cmd = [sys.executable, "-m", module_path]
    if extra_args:
        cmd.extend(extra_args)
    try:
        result = subprocess.run(cmd, cwd=str(REPO_ROOT))
        return result.returncode
    except KeyboardInterrupt:
        return 130
