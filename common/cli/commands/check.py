"""Comando `arkanum check <N>` — pre-checks locales + check real.

- `--dry-run`: corre sólo los pre-checks (sin gastar cuota Gemini).
- Modo normal: corre pre-checks primero. Si fallan, pide confirmación antes
  de invocar el check real. Si pasan, sigue derecho.
- Tras éxito en una quest marcada con `live_agent=True` (Q07/Q08), ofrece
  lanzar `arkanum run N "..."` y abrir el visualizador automáticamente
  (esos quests trazan solos, sin flag).
"""
from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from common.cli.helpers import (
    REPO_ROOT,
    check_module,
    check_path,
    resolve_quest_by_number,
    run_module_capturing,
)
from common.cli.pre_checks.runner import (
    PreCheckResult,
    all_passed,
    run_pre_checks,
)
from common.dashboard.services.cost import parse_tokens, record_cost
from common.dashboard.services.quest_catalog import QuestMeta
from common.progress.db import record_quest_attempt

console = Console()


def _render_table(quest_title: str, results: list[PreCheckResult]) -> None:
    table = Table(
        title=f"Pre-checks locales — {quest_title}",
        title_style="bold magenta",
        show_lines=False,
    )
    table.add_column("", width=2, no_wrap=True)
    table.add_column("Check", style="bold")
    table.add_column("Detalle", style="dim")

    for r in results:
        icon = "[green]✔[/green]" if r.passed else "[red]✘[/red]"
        detail = "" if r.passed else (r.detail or "—")
        table.add_row(icon, r.name, detail)

    console.print(table)


def check(
    ctx: typer.Context,
    number: int = typer.Argument(..., help="Número del quest (1..8)"),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Sólo correr pre-checks locales sin invocar Gemini.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Asumir sí cuando se pide confirmación tras pre-checks fallidos.",
    ),
) -> None:
    """Validar la solución del quest indicado.

    Args extra (un prompt en texto plano) se reenvían al check.py vía
    la env var `ARKANUM_CHECK_PROMPT`. Cada check decide si lo respeta
    o usa su prompt hardcoded como fallback.
    """
    extra_args = list(ctx.args) if ctx.args else []
    user_prompt = next(
        (a for a in extra_args if a and not a.startswith("-")),
        None,
    )
    quest = resolve_quest_by_number(number)
    module = check_module(quest)

    if not check_path(quest).exists():
        console.print(
            f"[red]No existe el check para Quest {quest.order}:[/] {check_path(quest)}"
        )
        raise typer.Exit(1)

    results = run_pre_checks(quest)
    _render_table(f"Quest {quest.order} — {quest.title}", results)
    passed = all_passed(results)

    if dry_run:
        if passed:
            console.print(
                f"\n[green]Pre-checks OK.[/] Cuando estés listo: "
                f"[cyan]arkanum check {quest.order}[/]"
            )
        else:
            console.print(
                "\n[yellow]Algunos pre-checks fallaron.[/] "
                "Revisa los detalles antes de invocar Gemini."
            )
            raise typer.Exit(1)
        return

    if not passed:
        if not yes:
            confirm_msg = (
                "Los pre-checks locales fallaron. ¿Continuar con el check real "
                "(consume cuota de Gemini)?"
                if quest.uses_gemini
                else "Los pre-checks locales fallaron. ¿Continuar con el check real?"
            )
            proceed = typer.confirm(confirm_msg, default=False)
            if not proceed:
                console.print("[dim]Cancelado por el aprendiz.[/]")
                raise typer.Exit(1)

    # Para quests que ejecutan el agente DURANTE el check (Q07), ofrecemos
    # verlo en vivo en lugar de re-ejecutar después. 1× Gemini en vez de 2×.
    live_during_check = quest.live_agent and quest.uses_gemini
    if live_during_check:
        run_with_tracing = _ask_live_before_check(
            quest,
            user_prompt or quest.live_agent_default_prompt,
        )
    else:
        run_with_tracing = False

    console.print(
        f"\n[dim]Ejecutando check de[/] [cyan]Quest {quest.order} — {quest.title}[/]"
    )
    if quest.uses_gemini:
        console.print("[yellow]Aviso:[/] este check consume cuota de Gemini.")
    if user_prompt:
        console.print(f"[dim]Usando prompt:[/] {user_prompt!r}")
    console.print()

    if run_with_tracing:
        # Camino "vivo": ejecutamos el starter directamente con tracing y
        # delegamos la validación al módulo del check del quest sin re-invocar.
        rc, captured = _run_starter_for_live_check(quest, user_prompt)
    else:
        # Camino normal: ejecutamos el check.py del quest como subprocess.
        env_extra = {"ARKANUM_WORKSPACE": f"quests/{quest.slug}/workspace"}
        if user_prompt:
            env_extra["ARKANUM_CHECK_PROMPT"] = user_prompt
        rc, captured = run_module_capturing(module, env_extra=env_extra)

    prompt_tokens, response_tokens = parse_tokens(captured)
    if prompt_tokens > 0 or response_tokens > 0:
        record_cost(quest.db_id, prompt_tokens, response_tokens)
        console.print(
            f"\n[dim]Coste capturado:[/] "
            f"{prompt_tokens} prompt + {response_tokens} response tokens."
        )

    record_quest_attempt(
        quest.db_id,
        passed=rc == 0,
        failure_reason=None if rc == 0 else f"check exit code {rc}",
    )
    if rc != 0:
        raise typer.Exit(rc)

    # Para Q08 (live_agent sin uses_gemini), la pregunta va al final: el
    # check no ejecutó el agente, así que invitamos a re-correrlo con
    # `arkanum run N "..."` (Q08 traza solo).
    if quest.live_agent and not live_during_check:
        _offer_live_agent(quest, user_prompt or quest.live_agent_default_prompt)


_LIVE_AGENT_URL = "http://127.0.0.1:8765/live-agent"


def _ask_live_before_check(quest: QuestMeta, prompt: str | None) -> bool:
    """Pregunta ANTES del check si quiere ver al agente trabajando en vivo.

    Si responde Y: arranca dashboard, abre navegador, devuelve True (el
    flujo principal ejecuta el starter con tracing en lugar del check.py
    del quest). El check se valida con el output capturado del starter
    sin re-invocar Gemini.

    Si responde N: devuelve False y el flujo principal usa el camino
    normal (check.py del quest como subprocess).
    """
    if not prompt:
        return False

    console.print()
    console.print(
        "[bold cyan]💡 ¿Quieres ver al agente trabajando en vivo durante el check?[/bold cyan]"
    )
    console.print(
        f"   Se ejecutará una sola vez con: [white]{prompt!r}[/white]"
    )
    console.print(
        "   [dim]Abriremos /live-agent y verás cada tool call en tiempo real.[/dim]"
    )

    try:
        proceed = typer.confirm("¿Ver en vivo?", default=True)
    except (KeyboardInterrupt, EOFError):
        console.print()
        return False

    if not proceed:
        return False

    try:
        from common.dashboard.lifecycle import ensure_started

        ensure_started()
    except Exception as exc:  # noqa: BLE001
        console.print(f"   [yellow]Aviso:[/] no pude arrancar el dashboard: {exc}")

    try:
        webbrowser.open(_LIVE_AGENT_URL)
        console.print(
            f"   [green]✓[/green] Abriendo [underline]{_LIVE_AGENT_URL}[/underline]"
        )
    except Exception:  # noqa: BLE001
        pass

    return True


def _run_starter_for_live_check(
    quest: QuestMeta, user_prompt: str | None
) -> tuple[int, str]:
    """Ejecuta el starter del quest emitiendo traces y devuelve (rc, captured).

    Reemplaza la invocación al check.py del quest cuando el aprendiz quiso
    ver el agente en vivo. Después del run, importa el módulo del check
    del quest y delega la validación a `validate_output(captured, rc)`.
    Si validate_output no lanza, llamamos a success() del check.
    """
    import importlib
    import json
    import re
    import secrets

    from common.dashboard.services.trace import record_step, start_trace
    from common.progress.notify import emit_event

    trace_id = start_trace()
    prompt = (
        user_prompt
        or os.environ.get("ARKANUM_CHECK_PROMPT")
        or quest.live_agent_default_prompt
        or ""
    )

    # session_start con el quest + prompt del usuario.
    _record_trace_step(
        trace_id,
        quest.db_id,
        "session_start",
        quest.title,
        json.dumps({
            "quest_order": quest.order,
            "slug": quest.slug,
            "user_prompt": prompt,
        }),
    )

    console.print(
        f"[dim]Trace[/] [cyan]{trace_id}[/] · "
        f"[dim]ve en[/] {_LIVE_AGENT_URL}"
    )
    console.print()

    # Patrones del parser, idénticos a los de run.py (camino con tracing).
    call_re = re.compile(r"Calling function:\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*$")
    result_re = re.compile(r"^\s*->\s*(.+?)\s*$")
    prompt_tok_re = re.compile(r"Prompt tokens:\s*(\d+)")
    response_tok_re = re.compile(r"Response tokens:\s*(\d+)")

    def on_line(line: str) -> None:
        stripped = line.rstrip("\r\n").strip()
        if not stripped:
            return
        call_m = call_re.search(stripped)
        if call_m:
            _record_trace_step(
                trace_id, quest.db_id,
                "function_call", call_m.group(1), call_m.group(2).strip(),
            )
            return
        result_m = result_re.match(stripped)
        if result_m:
            _record_trace_step(
                trace_id, quest.db_id, "function_result", None, result_m.group(1),
            )
            return
        pt = prompt_tok_re.search(stripped)
        if pt:
            _record_trace_step(
                trace_id, quest.db_id, "tokens", "prompt", pt.group(1),
            )
        rt = response_tok_re.search(stripped)
        if rt:
            _record_trace_step(
                trace_id, quest.db_id, "tokens", "response", rt.group(1),
            )

    # Ejecuta el starter directamente (no el check.py del quest).
    starter_mod = f"quests.{quest.slug}.starter.main"
    rc, captured = run_module_capturing(
        starter_mod,
        extra_args=[prompt, "--verbose"],
        on_line=on_line,
        env_extra={
            "ARKANUM_TRACE_ID": trace_id,
            "ARKANUM_TRACE": "1",
            "ARKANUM_QUEST_DB_ID": quest.db_id,
            "ARKANUM_WORKSPACE": f"quests/{quest.slug}/workspace",
            "COLUMNS": "1000",
        },
    )

    _record_trace_step(
        trace_id,
        quest.db_id,
        "session_end",
        f"exit code {rc}",
        json.dumps({"returncode": rc}),
    )

    # Delegamos la validación al módulo del check del quest, sin re-correr.
    quest_check_mod = importlib.import_module(check_module(quest))
    try:
        validator = getattr(quest_check_mod, "validate_output")
    except AttributeError:
        # Si el check del quest no expone validate_output, no podemos
        # validar sin re-ejecutar. Devolvemos rc directamente.
        return rc, captured

    try:
        validator(captured, returncode=rc, error="")
    except SystemExit as exc:
        return int(exc.code or 1), captured

    # Validación pasó: llama success() del check para sellar la quest.
    try:
        quest_check_mod.success()
    except Exception:  # noqa: BLE001
        # success() puede fallar al persistir; lo capturamos pero no
        # cambiamos rc — ya se validó el output.
        pass
    _ = emit_event  # silenciar import "no usado" si no se invoca

    return 0, captured


def _record_trace_step(
    trace_id: str,
    quest_db_id: str,
    step_type: str,
    name: str | None,
    payload: str | None,
) -> None:
    """Persiste el step en `agent_traces`.

    NO emite POST a /events/trace porque ese endpoint también llama
    record_step → duplicación. El polling del dashboard lee directo
    de la tabla, así que el efecto es el mismo sin duplicar.
    """
    from common.dashboard.services.trace import record_step

    record_step(
        trace_id=trace_id,
        step_type=step_type,
        name=name,
        payload=payload,
        quest_db_id=quest_db_id,
    )


def _offer_live_agent(quest: QuestMeta, prompt: str | None) -> None:
    """Tras un check exitoso, pregunta si lanzar `arkanum run` + abrir el panel.

    Reutiliza el prompt que ya validó el check (o el default por quest).
    Si el aprendiz acepta, spawnea el subprocess detached y abre el navegador.
    """
    if not prompt:
        return

    console.print()
    console.print("[bold cyan]💡 ¿Quieres ver al agente trabajando en vivo?[/bold cyan]")
    console.print(
        f"   Esto correrá: [white]arkanum run {quest.order} {prompt!r}[/white]"
    )
    console.print(
        "   [dim](consume cuota Gemini · abre /live-agent automáticamente)[/dim]"
    )

    try:
        proceed = typer.confirm("¿Lanzar?", default=True)
    except (KeyboardInterrupt, EOFError):
        console.print()
        proceed = False

    if not proceed:
        console.print(
            f"   [dim]Cuando quieras:[/] [cyan]arkanum run {quest.order} {prompt!r}[/cyan]"
        )
        return

    # Asegura el dashboard arrancado para que /live-agent reciba traces.
    try:
        from common.dashboard.lifecycle import ensure_started

        ensure_started()
    except Exception as exc:  # noqa: BLE001
        console.print(f"   [yellow]Aviso:[/] no pude arrancar el dashboard: {exc}")

    if not _spawn_arkanum_run(quest.order, prompt):
        console.print("   [red]No pude lanzar el subprocess.[/red]")
        return

    console.print(
        f"   [green]✓[/green] Lanzado. Abriendo "
        f"[underline]{_LIVE_AGENT_URL}[/underline] en tu navegador."
    )
    try:
        webbrowser.open(_LIVE_AGENT_URL)
    except Exception:  # noqa: BLE001
        # `webbrowser.open` puede fallar silenciosamente; el aprendiz puede
        # navegar a mano. No bloquea el flujo.
        pass


def _spawn_arkanum_run(quest_order: int, prompt: str) -> bool:
    """Spawnea `python -m common.cli.main run N "prompt"` detached. True si OK.

    Para Q07/Q08 (`live_agent=True`) `run` traza automáticamente, así que
    no hace falta pasar ningún flag para alimentar `/live-agent`.
    """
    cmd = [
        sys.executable,
        "-m",
        "common.cli.main",
        "run",
        str(quest_order),
        prompt,
    ]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    popen_kwargs: dict = {
        "cwd": str(REPO_ROOT),
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
        return True
    except OSError:
        return False
