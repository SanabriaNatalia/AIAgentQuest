"""Comando `arkanum run <N> "prompt"` — wrapper con tracing para Q07-Q08.

Ejecuta el starter como subprocess, parsea su stdout línea-por-línea y
emite eventos `trace` al dashboard. La página `/live-agent` los muestra
en vivo (polling cada 1s).

Patrones reconocidos:
- `Calling function: NAME(ARGS)` → function_call
- `-> {...}` o `-> ...`         → function_result
- `Prompt tokens: N`            → tokens (prompt)
- `Response tokens: N`          → tokens (response)
"""
from __future__ import annotations

import json
import re

import typer
from rich.console import Console

from common.cli.helpers import resolve_quest_by_number, run_module_capturing, starter_module, starter_path
from common.dashboard.services.trace import record_step, start_trace
from common.progress.notify import emit_event

console = Console()

_CALL_RE = re.compile(r"Calling function:\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*$")
_RESULT_RE = re.compile(r"^\s*->\s*(.+?)\s*$")
_PROMPT_TOK_RE = re.compile(r"Prompt tokens:\s*(\d+)")
_RESPONSE_TOK_RE = re.compile(r"Response tokens:\s*(\d+)")


def _emit_step(trace_id: str, quest_db_id: str, step_type: str, name: str | None, payload: str | None) -> None:
    """Persiste localmente y, si el dashboard responde, también via HTTP.

    La persistencia local es la fuente de verdad — el POST sólo acelera
    el polling de /live-agent (que también recoge la tabla directamente).
    """
    record_step(
        trace_id=trace_id,
        step_type=step_type,
        name=name,
        payload=payload,
        quest_db_id=quest_db_id,
    )
    # Mejor esfuerzo: si el dashboard está activo, el polling encontrará
    # los rows sin que hagamos un POST extra. Lo emitimos por simetría con
    # otros eventos, no es crítico.
    try:
        emit_event(
            "trace",
            {
                "trace_id": trace_id,
                "step_type": step_type,
                "name": name,
                "payload": payload,
                "quest_db_id": quest_db_id,
            },
        )
    except Exception:  # noqa: BLE001
        pass


def _parse_line(
    line: str,
    *,
    trace_id: str,
    quest_db_id: str,
) -> None:
    """Inspecciona una línea y emite los steps que correspondan."""
    stripped = line.rstrip("\r\n").strip()
    if not stripped:
        return

    call_match = _CALL_RE.search(stripped)
    if call_match:
        name, args = call_match.group(1), call_match.group(2).strip()
        _emit_step(trace_id, quest_db_id, "function_call", name, args)
        return

    result_match = _RESULT_RE.match(stripped)
    if result_match:
        _emit_step(trace_id, quest_db_id, "function_result", None, result_match.group(1))
        return

    pt = _PROMPT_TOK_RE.search(stripped)
    rt = _RESPONSE_TOK_RE.search(stripped)
    if pt is not None:
        _emit_step(trace_id, quest_db_id, "tokens", "prompt", pt.group(1))
    if rt is not None:
        _emit_step(trace_id, quest_db_id, "tokens", "response", rt.group(1))


def run(
    ctx: typer.Context,
    number: int = typer.Argument(..., help="Número del quest (1..8). Pensado para Q07-Q08."),
) -> None:
    """Ejecutar el starter del quest con tracing en vivo del agent loop.

    Argumentos extras se reenvían al starter como si lo invocaras con
    `python -m`. Ejemplo: `arkanum run 7 "¿Qué archivos hay?"`.
    """
    quest = resolve_quest_by_number(number)
    if not starter_path(quest).exists():
        console.print(
            f"[red]No existe el starter para Quest {quest.order}:[/] {starter_path(quest)}"
        )
        raise typer.Exit(1)

    if quest.order < 6:
        console.print(
            "[yellow]Aviso:[/] `arkanum run` está pensado para Q07-Q08 (agent loop). "
            "En este quest los patrones de tracing pueden no aparecer."
        )

    trace_id = start_trace()

    # Marca el inicio del trace con un step "session_start" para que
    # /live-agent muestre algo aunque el starter no imprima nada en seguida.
    _emit_step(
        trace_id,
        quest.db_id,
        "session_start",
        quest.title,
        json.dumps({"quest_order": quest.order, "slug": quest.slug}),
    )

    console.print(
        f"[dim]Trace[/] [cyan]{trace_id}[/] · "
        f"[dim]Visualízalo en[/] http://127.0.0.1:8765/live-agent"
    )
    console.print()

    def on_line(line: str) -> None:
        _parse_line(line, trace_id=trace_id, quest_db_id=quest.db_id)

    extra = list(ctx.args)
    rc, _captured = run_module_capturing(
        starter_module(quest),
        extra_args=extra,
        on_line=on_line,
        env_extra={
            "ARKANUM_TRACE_ID": trace_id,
            "ARKANUM_TRACE": "1",
            "ARKANUM_QUEST_DB_ID": quest.db_id,
        },
    )

    _emit_step(
        trace_id,
        quest.db_id,
        "session_end",
        f"exit code {rc}",
        json.dumps({"returncode": rc}),
    )

    if rc != 0:
        raise typer.Exit(rc)
