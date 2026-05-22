"""Runner de pre-checks locales por quest.

Despacha al módulo `qNN.py` correspondiente y devuelve una lista normalizada
de `PreCheckResult`. Si el quest no tiene pre-checks o el módulo no se puede
importar, devuelve un único resultado con `passed=False` describiendo el
problema (en lugar de levantar).
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass

from common.dashboard.services.quest_catalog import QuestMeta


@dataclass(frozen=True)
class PreCheckResult:
    name: str
    passed: bool
    detail: str | None = None


def run_pre_checks(quest: QuestMeta) -> list[PreCheckResult]:
    module_name = f"common.cli.pre_checks.q{quest.order:02d}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        return [
            PreCheckResult(
                name=f"Pre-checks para Quest {quest.order}",
                passed=False,
                detail=f"No existe el módulo {module_name}.",
            )
        ]

    checks_fn = getattr(module, "checks", None)
    if checks_fn is None:
        return [
            PreCheckResult(
                name=f"Pre-checks para Quest {quest.order}",
                passed=False,
                detail=f"{module_name} no expone `checks(quest)`.",
            )
        ]

    try:
        results = checks_fn(quest)
    except Exception as exc:  # noqa: BLE001 — reportamos cualquier crash al usuario
        return [
            PreCheckResult(
                name=f"Pre-checks para Quest {quest.order}",
                passed=False,
                detail=f"El módulo de pre-checks crashed: {exc!r}.",
            )
        ]

    return list(results)


def all_passed(results: list[PreCheckResult]) -> bool:
    return all(r.passed for r in results)
