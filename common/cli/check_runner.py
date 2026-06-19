"""Helpers compartidos para reportar validaciones de output en `check.py`.

Cada quest tiene su `check.py` que ejecuta el starter en subprocess y
busca strings esperados en el stdout capturado. Antes esa validación
se hacía con un loop `if expected not in output: fail(...)` que solo
reportaba el primer fallo en un panel rojo de texto plano. Eso era
opaco: el aprendiz no veía cuáles validaciones pasaron y cuáles no.

Este módulo centraliza el reporte como tablas `rich.Table` con ✔/✘
por validación, alineado visualmente con la tabla de pre-checks que
ya conoce el aprendiz desde `arkanum check`.

API mínima:
- `render_required_outputs_table(title, output, expected)`: devuelve
  `(Table, missing_list)`. El caller imprime la tabla y, si
  `missing_list` no está vacío, llama a su `fail(...)` local.
- `render_any_of_table(title, output, candidates, label)`: para checks
  que aceptan que al menos uno de varios candidatos aparezca (p.ej.
  tools válidas en Q06/Q07).
"""
from __future__ import annotations

from rich.table import Table


def render_required_outputs_table(
    title: str,
    output: str,
    expected: list[str | tuple[str, str]],
) -> tuple[Table, list[str]]:
    """Tabla con cada salida esperada marcada ✔/✘ según esté en `output`.

    Cada item de `expected` puede ser:
    - un string: el texto que debe aparecer en la salida (se muestra tal cual).
    - una tupla `(needle, label)`: `needle` es el texto que se busca en la
      salida y `label` es una descripción legible que se muestra en la tabla.
      Útil para marcadores crípticos (p.ej. `("Agente:", "La respuesta del
      agente")`) que por sí solos no le dicen nada al aprendiz.

    Devuelve `(table, missing)`. `missing` es la lista de `needle` que no se
    encontraron — vacía si todo pasó.
    """
    table = Table(
        title=title,
        title_style="bold cyan",
        caption="Cada fila es un texto que tu solución debe imprimir en la consola.",
        caption_style="dim",
        show_lines=False,
    )
    table.add_column("", width=2, no_wrap=True)
    table.add_column("Tu salida debe incluir", style="white")

    missing: list[str] = []
    for item in expected:
        needle, label = item if isinstance(item, tuple) else (item, item)
        if needle in output:
            table.add_row("[green]✔[/green]", _truncate(label, 100))
        else:
            table.add_row("[red]✘[/red]", _truncate(label, 100))
            missing.append(needle)
    return table, missing


def render_any_of_table(
    title: str,
    output: str,
    candidates: list[str],
    item_label: str = "Candidato",
) -> tuple[Table, bool]:
    """Tabla para validaciones tipo "al menos uno de la lista debe estar".

    Marca con ✔ los que se encontraron, con · los que no (sin rojo,
    porque no es obligatorio que estén todos). Devuelve `(table, found)`
    donde `found` es True si al menos uno apareció.
    """
    table = Table(
        title=title,
        title_style="bold cyan",
        show_lines=False,
    )
    table.add_column("", width=2, no_wrap=True)
    table.add_column(item_label, style="white")

    any_found = False
    for cand in candidates:
        if cand in output:
            table.add_row("[green]✔[/green]", cand)
            any_found = True
        else:
            table.add_row("[dim]·[/dim]", f"[dim]{cand}[/dim]")
    return table, any_found


def _truncate(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"
