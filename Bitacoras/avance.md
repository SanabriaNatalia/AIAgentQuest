# Bitácora de Avance — Dashboard Arcano

> **Plan canónico:** [`2026-05-19-plan-dashboard-arcano.md`](2026-05-19-plan-dashboard-arcano.md) — define **qué hay que hacer** en total.
> **Este archivo:** refleja **qué se ha hecho efectivamente**, desviaciones del plan, hallazgos y tech debt.
> **Convención:** se actualiza al cierre de cada fase. Cualquier sesión nueva debería leer estos dos archivos antes de continuar.

---

## Estado actual

| Campo | Valor |
|---|---|
| **Branch** | `feat/dashboard-arcano` |
| **Última fase completada** | Fase 12 — Sistema de pistas (contenido) |
| **Próxima fase** | Fase 13 — Tracking tiempo/intentos + logros calculados |
| **Tiempo invertido aprox.** | ~51h (acumulado Fases 0-12) |
| **Tiempo restante estimado** | ~17h (Fases 13-17) |

### Cómo retomar en otra sesión

1. `git log --oneline -10` → ver qué commits hay; los del dashboard arrancan en `603b50f`
2. Leer **este archivo** completo → estado y decisiones acumuladas
3. Leer la sección 10 del plan canónico para la fase próxima
4. Validar que el branch esté en `feat/dashboard-arcano`: `git branch --show-current`
5. Arrancar el server para probar: `python -m uv run arkanum dashboard start` (luego `stop` al terminar)

### Workflow estable

- Dependencias se gestionan con `python -m uv` (no `uv` directo — ver hallazgo Fase 4).
- Comandos comunes:
  - `python -m uv run arkanum dashboard start|stop|status|logs`
  - `python -m uv run arkanum doctor [--skip-ping]`
- Cada fase cierra con un commit `feat(dashboard): fase N - <descripcion>` que detalla lo entregado y los hallazgos.

---

## Tabla de fases

| # | Fase | Estado | Commit | Horas plan | Notas clave |
|---|---|---|---|---|---|
| 0 | Andamiaje | ✅ | `709e383` | 2h | +build-system hatchling (no en plan original) |
| 1 | Server + lifecycle | ✅ | `a2d7a81` | 4h | UTF-8 fix para Windows agregado |
| 2 | Catálogo + perfil | ✅ | `71f5729` | 4h | Fuentes de sistema en vez de Cinzel/Inter (diferido a F17) |
| 3 | Mapa + rangos | ✅ | `09e0c41` | 4h | Sin desviaciones |
| 4 | Setup global + doctor | ✅ | `170b57a` | 5h | Vanilla JS polling en vez de HTMX (HTMX se vendoriza en F5) |
| 5 | Viewer READMEs + Códex | ✅ | `3ffc6da` | 5h | HTMX **no vendorizado** — vanilla JS basta; theme Pygments monokai servido via `/api/pygments.css` |
| 6 | Integración CLI + notif | ✅ | `dc71ecc` | 3h | `celebrate.html` placeholder creado aquí (la animación completa es F7); `kind` interno en BD usa snake_case, URL kebab-case |
| 7 | Celebración | ✅ | `a76a32d` | 3h | Toast del perfil usa endpoint `peek` (no consume) + `dismiss` explícito en vez de marcar `seen=1` al renderizar; service `celebration.py` reconstruye contexto desde el último evento `quest_completed` |
| 8 | Wizard init + CLI básico | ✅ | `f84af06` _(bitácora sin commit)_ | 4h | Legacy `init_user.py` / `show_progress.py` se conservan intactos (no se borran); módulo `next.py` renombrado a `next_quest.py` porque `next` es builtin de Python |
| 9 | Actualizar READMEs quests | ✅ | `cce7dd9` _(bitácora sin commit)_ | 2h | `arkanum start N` ahora acepta args extras (cambio mini-scope en start.py); 5 READMEs tenían typos de paths viejos (`quest_01_first_agent`, etc.) — corregidos |
| 10 | Pre-check local | ✅ | `a17d8e3` _(bitácora `109d8a6`)_ | 4h | Pre-checks AST + regex por quest (`q01..q08`); flag `--yes` agregado para auto-confirmar; regex matchea también comentarios (decisión consciente — ver hallazgos) |
| 11 | Pistas (mecánica) | ✅ | `4388260` _(bitácora sin commit)_ | 5h | Service + endpoints + UI; 24 placeholders `.md` con texto F12-pendiente; modal de confirmación vanilla JS; orden estricto validado en server |
| 12 | Pistas (contenido) | ✅ | `25c2b9b` _(bitácora sin commit)_ | 5h | 24 .md redactados con escalada Susurro/Revelación/Manifestación; títulos cortos ("El susurro" etc.) en vez del nombre del quest; snippets reales sin pegar la solución completa |
| 13 | Tracking tiempo/intentos | ⏳ | — | 4h | — |
| 14 | Tracking costo | ⏳ | — | 2h | — |
| 15 | Detección cierre acto | ⏳ | — | 2h | — |
| 16 | Visualización agent loop | ⏳ | — | 6h | — |
| 17 | Pulido | ⏳ | — | 4h | Embeber fuentes Cinzel/Inter aquí |

**Total acumulado:** Fases 0-12 = ~51h reales / 50h planificadas (cercano al estimado).

---

## Detalle por fase

### Fase 0 — Andamiaje (`709e383`)

**Entregado**
- `pyproject.toml`: nuevas deps (`jinja2`, `markdown-it-py`, `pygments`, `psutil`), entry point `arkanum`, build-system hatchling.
- Estructura vacía: `common/cli/`, `common/cli/commands/`, `common/dashboard/`, `common/dashboard/routes/`, `common/dashboard/services/` con `__init__.py`.
- Stub `common/cli/main.py` con typer app.
- Migraciones aditivas en `common/progress/db.py`: helpers `_column_exists` / `_add_column_if_missing`; nuevas tablas (`events`, `quest_attempts`, `hint_usage`, `quest_reading`, `act_milestones`); columnas nuevas en `apprentice` y `quest_completion`.
- `.gitignore`: artefactos runtime (`.quest_progress.pid`, `.quest_dashboard.log`, `.quest_dashboard.port`, `.setup_cache.json`, `.last_celebrate.timestamp`, `.quest_calls.log`).

**Desviaciones del plan**
- El plan original no especificaba `[build-system]` ni `[tool.hatch.build.targets.wheel] packages = ["common"]`. Fue necesario agregarlos para que `[project.scripts] arkanum = "common.cli.main:app"` se instale como CLI ejecutable. Sin esto, `uv sync` no crearía el comando `arkanum`.

**Hallazgos / tech debt**
- **`uv` no estaba en PATH** en el sistema del usuario. Resuelto temporalmente con `pip install --user uv` → ahora accesible vía `python -m uv`. Recomendación al usuario: instalar oficial desde `astral.sh/uv` para tenerlo en PATH.
- **UnicodeEncodeError pre-existente** detectado en `common/progress/show_progress.py` (rich + cp1252 en Windows console). NO resuelto en F0; se mitiga parcialmente en F1 (solo afecta path `arkanum`); se resuelve definitivamente en F8 cuando se reemplace `show_progress` legacy.

---

### Fase 1 — Server + lifecycle (`a2d7a81`)

**Entregado**
- `common/dashboard/server.py`: FastAPI app con `/health`.
- `common/dashboard/__main__.py`: entry point para uvicorn (usado por spawn detached y modo dev).
- `common/dashboard/lifecycle.py`: `start` / `stop` / `status` / `is_running` / `ensure_started`; spawn detached cross-platform (Windows `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`); validación PID + nombre de proceso vía psutil; fallback de puerto 8765-8768; espera con ping a `/health`; modo dev en foreground con `--reload`.
- `common/cli/commands/dashboard.py`: subcomandos `start` (con `--dev`), `stop`, `status`, `logs` (con `--follow` y `--lines`), `open`.

**Desviaciones del plan**
- **UTF-8 fix agregado a `common/cli/main.py`** (no estaba previsto en F1). Causa: el bug pre-existente de cp1252 bloqueaba el output de `rich` en Windows. Se reconfigura `sys.stdout`/`sys.stderr` a UTF-8 al inicio. Resuelve el problema para todo lo que pasa por `arkanum`. `show_progress`/`init_user` legacy siguen rotos.

**Hallazgos / tech debt**
- Confirmado: `arkanum dashboard start` arranca un proceso detached que sobrevive al cierre de la terminal del padre. Verificado via `psutil.pid_exists(pid)` + match de cmdline tras cerrar shell.
- Opt-out `ARKANUM_NO_DASHBOARD=1` para CI/tests funciona.

---

### Fase 2 — Catálogo + perfil (`71f5729`)

**Entregado**
- `common/dashboard/services/quest_catalog.py`: dataclasses `QuestMeta` y `ActMeta`; tupla `QUESTS` con 8 entradas (slug, db_id, título, acto, orden, dificultad, rango, banner, quote); dict `ACTS` con 4 actos (III y IV marcados `in_development`); helpers `quest_by_slug` / `quest_by_db_id` / `quests_in_act`.
- `common/dashboard/services/progress.py`: dataclass `Apprentice`; funciones `get_apprentice`, `get_completed_quest_ids`, `get_completed_count`, `get_xp_breakdown`, `get_quest_status_map`, `get_current_quest`.
- `common/dashboard/templating.py`: singleton `Jinja2Templates`.
- `common/dashboard/routes/health.py` (movida desde server.py) y `pages.py` (perfil + placeholders).
- `common/dashboard/server.py`: usa routers, monta `/static` y `/assets`.
- Templates: `base.html` (nav sticky con Perfil/Mapa/Rangos, footer), `profile.html` (dos estados), `coming_soon.html`.
- `common/dashboard/static/arcane.css` v1.

**Desviaciones del plan**
- **Fuentes**: el plan especificaba `Cinzel/Cormorant` para títulos e `Inter` para texto, embebidas en `/static/fonts/`. Decidí usar fuentes de sistema (`Georgia` + `system-ui`) para v1 — sin dependencias online, funciona offline. Embeber Cinzel/Inter queda para **Fase 17 (pulido)**.

**Hallazgos / tech debt**
- Ninguno crítico.

---

### Fase 3 — Mapa + galería de rangos (`09e0c41`)

**Entregado**
- `routes/pages.py`: `/map` ahora arma `acts_data` con quote por acto; `/ranks` pasa el catálogo completo; ambas reciben `status_map` y un dict de numerales romanos.
- Templates: `map.html` (4 bandas horizontales con grid de quest-cards), `ranks.html` (grid responsive de 8 rank-cards).
- `arcane.css` +330 líneas: `page-header` con flow `Prompt → Memoria → Herramientas → Conocimiento → Protocolos → Sistemas`; `act-band` con borde dashed cuando in_development; `quest-card` en 3 estados (completed/current/locked) con animación `pulse` para current; difficulty stars coloreadas (verde/ámbar/rojo/oro); XP pill púrpura; rank cards con badge circular (numeral romano) y silueta cuando locked.

**Desviaciones del plan**
- Ninguna.

**Hallazgos / tech debt**
- Las cartas del mapa NO son clickeables (planeado para F5 cuando exista `/quest/{slug}`).

---

### Fase 12 — Sistema de pistas, contenido (`25c2b9b`, bitácora sin commitear)

**Entregado**
- **Q01 — La Primera Invocación**: I empuja a notar que `genai` está importado pero no construido. II nombra `genai.Client` + `client.models.generate_content`. III pega el patrón cliente + llamada con `gemini-2.5-flash`.
- **Q02 — El Medidor Arcano**: I señala que el costo deja rastro en el `response`. II nombra `usage_metadata`, `prompt_token_count`, `candidates_token_count` + recordatorio del `RuntimeError`. III muestra el `print(f"Prompt tokens: {...}")` con el orden exacto que valida el check.
- **Q03 — La Voz del Aprendiz**: I plantea "escuchar desde la terminal + empaquetar la voz". II nombra `argparse.ArgumentParser`, `types.Content`, `types.Part`, y el cambio `contents=prompt` → `contents=messages`. III construye `messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]`.
- **Q04 — Las Leyes del Arkanum**: I apunta al canal aparte (`config=`). II nombra `GenerateContentConfig(system_instruction=..., temperature=0)` y recuerda editar primero `common/prompts/system_prompt.py`. III muestra el config completo con el `from common.prompts.system_prompt import system_prompt`.
- **Q05 — El Directorio Prohibido**: I formula la pregunta "¿cómo verificas que una ruta está contenida en otra?". II nombra `os.path.abspath`, `os.path.join`, `os.path.commonpath` + reducción `commonpath([a, b]) == a`. III pega las 4 líneas de `working_dir_abs` → `is_valid_path` dentro de `get_valid_target_path.py`.
- **Q06 — El Cofre de Instrumentos**: I dirige a observar `schema_get_files_info` como modelo. II nombra `types.FunctionDeclaration(name, description, parameters=types.Schema)`, registro en `types.Tool(function_declarations=...)`, y `tools=[available_functions]` en el starter. III pega la plantilla completa de `schema_get_file_content` recordando que `working_directory` no se declara (lo inyecta Q07).
- **Q07 — La Encarnación del Agente**: I separa "ejecutar real" de "envolver en Content". II nombra `function_map[name](**args)`, inyección de `working_directory`, formato `types.Content(role="tool", parts=[types.Part.from_function_response(...)])`, y el manejo de función desconocida con `{"error": ...}`. III pega el cuerpo completo de `call_function` (con guard de `function_name not in function_map`).
- **Q08 — El Ciclo de la Manifestación**: I apela al historial como "río" que conecta iteraciones. II nombra `for _ in range(MAX_ITERS)`, `messages.append(candidate.content)`, `messages.append(types.Content(role="tool", parts=function_results))` y el patrón de salida `return response.text`. III pega esqueleto de `main()` + `generate_content()` con `return None` significando "sigue iterando".

**Convención de formato adoptada**
- Cada `.md` arranca con un H2 corto temático: `## El susurro` / `## La revelación` / `## La manifestación`. No incluye nombre del quest (eso ya lo da la carta visualmente).
- Susurro: blockquote inicial con la pregunta, seguido de 1-2 líneas de contexto. Sin código.
- Revelación: bullets con identificadores en **bold** + tipografía monoespaciada. Mención del archivo a tocar cuando aplica. Sin pegar el código.
- Manifestación: bloque `python` de 4-10 líneas (algunos pasan de 4 por necesidad de mostrar la estructura completa, p. ej. Q07 / Q08) + 1 línea final que reencuadra _por qué_ funciona.

**Smoke test ejecutado**
- `grep -r "Contenido pendiente" quests/` → 0 matches.
- Script TestClient: `POST /api/quests/{slug}/hints/{1,2,3}` para los 8 quests = 24 invocaciones. Todas devuelven 200, ninguna contiene "Contenido pendiente", y por nivel se valida:
  - L1 contiene `El susurro` ✔
  - L2 contiene `La revelación` ✔
  - L3 contiene `La manifestación` y `<pre` (bloque de código Pygments) ✔
- Sanity con dashboard real (puerto 8765): `/quest/quest_01_first_invocation` rinde HTML sin placeholder y la card I queda como `hint-card--available`.

**Desviaciones del plan**
- **Manifestación de Q07 y Q08 superan las 4 líneas sugeridas** del contrato. Justificación: para Q07 hay que mostrar el guard de "función desconocida" + la inyección de `working_directory` + el return final, lo que no cabe en 4 líneas sin trampear. Para Q08 hay que evidenciar la separación `main()` ↔ `generate_content()` para que la pista sea útil. Sigue siendo "snippet mínimo" en el sentido que importa: no pega la solución completa, sólo la estructura crítica.
- **No se generó docstring explícito en el `.md`** advirtiendo "renuncias al logro Sin red". El modal de F11 ya lo dice; replicarlo en cada `.md` sería ruido.

**Hallazgos / tech debt**
- **Las pistas se renderizan con el mismo pipeline que el README** (`render_markdown_file` → Pygments theme monokai). El syntax highlight queda consistente con el viewer de quests sin esfuerzo extra.
- **Pistas en `<pre>` no muestran el botón "Copiar"**: el `initCopyButtons()` busca `.viewer-prose .codeblock`, no `.hint-card-body .codeblock`. Decisión consciente: las pistas son lectura, no se copian al portapapeles (forzar lectura del aprendiz). Si se cambia de criterio en F17, sólo hay que ampliar el selector.
- **El render markdown procesa enlaces relativos** dentro de los `.md` de pistas igual que en READMEs (rewrite a `/codex/...`, `/quest/...`). Ninguna pista actual los usa, pero el comportamiento queda disponible si se necesitan referencias cruzadas en futuras pistas.
- **Pistas no traducidas a otros idiomas**: todas en español. Coherente con la convención global del repo. Si en algún momento se internacionaliza, sería en `quests/quest_NN_*/hints/{locale}/...`.

**Tech debt cerrado**
- ~~Contenido pedagógico pendiente~~ — las 24 pistas tienen ahora redacción real.

---

### Fase 11 — Sistema de pistas, mecánica (`4388260`, bitácora sin commitear)

**Entregado**
- **24 placeholders `.md`** en `quests/quest_NN_*/hints/{1_susurro,2_revelacion,3_manifestacion}.md`. Cada uno renderiza ya con markdown-it y trae un H1 + blockquote "Contenido pendiente — F12" + una línea describiendo la naturaleza de la pista. Pensados para no quedar mudos durante F11; el contenido pedagógico real llega en F12.
- **`common/dashboard/services/hints.py`** (nuevo):
  - `HintMeta` dataclass con `level`, `title`, `name`, `description`, `file_exists`, `eligible`, `requested`, `requested_at`.
  - Constante `HINT_LEVELS = ((1, "Susurro", "1_susurro.md"), (2, "Revelación", ...), (3, "Manifestación", ...))` — fuente única para nombres de archivo / títulos.
  - `list_hints_for(quest)` — calcula eligibility en cascada (la I siempre arranca elegible; la N+1 requiere que la N esté `requested`).
  - `get_hint(quest, level)` — sólo renderiza si la pista YA fue solicitada (defense in depth contra escrapeo del filesystem por URL).
  - `request_hint(quest, level)` — valida nivel ∈ {1,2,3}, archivo existe, orden estricto; `INSERT OR IGNORE` para idempotencia. Lanza `HintRequestError` con mensaje descriptivo.
  - `used_hints(quest)` y `is_no_red_eligible(quest)` para el logro "Sin red".
- **Endpoints** en `common/dashboard/routes/api.py`:
  - `GET /api/quests/{slug}/hints` — JSON con metadatos de las 3 pistas (sin contenido).
  - `POST /api/quests/{slug}/hints/{level}` — marca como solicitada y devuelve `{ slug, level, requested_at, html }` con el markdown renderizado. 400 si fuera de orden o nivel inválido, 404 si el slug no existe.
- **`common/dashboard/routes/pages.py`**: `quest_page` ahora pasa `hints` (lista) y `hint_contents` (dict `{level: html}`) al template; reaprovecha `render_markdown_file` del servicio existente.
- **Template `quest_view.html`** (modificado): añade `<section class="hints-section">` al final con 3 `<article class="hint-card hint-card--{state}">` y un modal de confirmación al final del documento (estado `hidden` por defecto, controlado vía JS).
- **CSS** (`arcane.css` +200 líneas): bloque `Sistema de pistas` con:
  - `.hint-card` base + variantes `--locked` (opacidad 0.55 + grayscale 0.4), `--available` (borde púrpura + glow sutil), `--revealed` (borde dorado + paleta más cálida).
  - `.hint-card-numeral` circular con romano (I/II/III).
  - `.hint-modal` fixed + backdrop blur + `.hint-modal-card` con CTAs reusando `.viewer-cta` y la variante `--ghost` de F7.
  - Responsive: el grid usa `repeat(auto-fit, minmax(260px, 1fr))` para colapsar a 1 columna en mobile; el modal apila actions verticalmente en pantallas <540px.
- **JS** (`dashboard.js` `initHints()`): handler de click en `.hint-card-button` → abre modal con título de la pista; confirmar dispara `fetch POST`, inserta dinámicamente `<div class="hint-card-body">` con el HTML devuelto, remueve el botón, cambia clase a `--revealed` y **desbloquea automáticamente la siguiente carta** (la cambia de `--locked` a `--available` e inyecta su botón). Soporta cierre con Escape, backdrop click, botón Cancelar. Vanilla — sin HTMX (consistente con F4/F5).

**Smoke test ejecutado** (TestClient + temp DB aislada):
- GET inicial → 3 pistas, sólo I eligible.
- Quest desconocida → 404.
- POST II sin I → 400 con mensaje "orden estricto".
- POST nivel 99 → 400 nivel inválido.
- POST I → 200 con `html` que contiene `<h1` + "Susurro".
- POST I de nuevo → 200 idempotente (no duplica).
- POST III sin II → 400.
- POST II tras I → 200; POST III tras II → 200.
- GET final → las 3 pistas marcadas `requested=True`.
- `/quest/quest_01_first_invocation` HTML contiene "ofrendas del aprendiz" y "hint-card--revealed".
- `/quest/quest_03_apprentice_voice` (locked) muestra sealed view y NO incluye el bloque de pistas.
- `/quest/quest_02_arcane_gauge` (current) muestra al menos una `hint-card--available`.

**Sanity contra dashboard real** (puerto 8765):
- `GET /api/quests/quest_01_first_invocation/hints` responde 200 con JSON consistente.
- `GET /quest/quest_01_first_invocation` incluye bloque "ofrendas del aprendiz" + botón clase `hint-card-button`.
- BD real (`.quest_progress.db`) sin entries en `hint_usage` tras el smoke (no contamina).

**Desviaciones del plan**
- **Modal renderizado en el mismo template** en vez de `partials/notifications.html`. El plan F11 mencionaba un partial separado; va embebido al final de `quest_view.html` porque sólo aparece en esa página. Si en F15 el cierre de acto necesita su propio modal, ahí se refactoriza a partial. Misma decisión que F7 (toast).
- **Auto-unlock de la siguiente carta en JS** (sin recarga de página): el plan sólo pedía revelar el contenido; agregar el desbloqueo de la N+1 en cliente da una UX mucho mejor (pides la I → la II se ilumina inmediatamente sin F5). Sigue siendo defense-in-depth: el server siempre valida orden.
- **`hint_contents` se calcula en el route handler** en vez de en el template via filter Jinja. Razón: render markdown desde el template requeriría exponer una función al ambiente Jinja; pasar el dict pre-calculado es más explícito y testeable.
- **Sin endpoint partial HTML** — `POST` devuelve JSON y el cliente arma el DOM. Considerado: server-renderear el card y enviarlo via HTMX-style. Descartado por consistencia con el resto (toast, mark-read, copy también son JSON + JS).

**Hallazgos / tech debt**
- **Placeholders renderizan markdown ya en F11**: la imagen visual desde el primer commit es razonable, no se ve un texto crudo o "Lorem ipsum" si alguien revela una pista en este estado. F12 sólo cambia el contenido pedagógico, no la mecánica ni el styling.
- **Inyección de HTML dinámico**: el `hint-card-body` se construye con `innerHTML = data.html`, donde `data.html` viene del backend (Pygments + markdown-it). Es seguro porque el contenido viene del repo del usuario (no de input externo), pero queda registrado para futuras pistas que pudieran venir de fuentes no confiables.
- **`alert()` en el catch del POST**: para errores 400 (orden incorrecto) muestra un `alert` nativo. Aceptable porque el flujo del modal NUNCA debería disparar un 400 (el server-side ya está sincronizado con el estado del UI); si pasa, es bug que merece atención inmediata. Si se quiere refinar más adelante, agregar un slot `[data-hint-error]` en el modal.
- **`is_no_red_eligible(quest)` no se expone en UI todavía**: F13 (tracking tiempo/intentos + logros calculados) consumirá esta función. La dejo lista pero sin componente visual.
- **Página /quest sigue siendo el único lugar con pistas**. No hay una página `/hints` global ni mención en el perfil. Si más adelante se requiere "ver todas las pistas que pediste", el dato está en `hint_usage` y `list_hints_for` ya soporta listarlas; sólo faltaría una vista agregada.

---

### Fase 10 — Pre-check local (`a17d8e3`, bitácora `109d8a6`)

**Entregado**
- `common/cli/pre_checks/_ast_helpers.py` (nuevo): helpers ligeros mezclando AST y regex:
  - `parse_source(path)` y `read_source(path)` (tratan archivo inexistente / SyntaxError devolviendo `None` en vez de explotar).
  - `has_import(tree, module, name=None)`, `has_call(tree, "client.models.generate_content")`, `has_attribute_access(tree, "response.usage_metadata")` — todos soportan dotted paths arbitrariamente largos vía `_matches_dotted`.
  - `has_function_def`, `has_for_range(range_arg_name)`, `call_has_kwarg(tree, qualified, kwarg)`, `regex_in_source(path, pattern)`.
- `common/cli/pre_checks/runner.py` (nuevo): `PreCheckResult` dataclass + `run_pre_checks(quest)` que importa `common.cli.pre_checks.qNN` por número, captura `ModuleNotFoundError`, ausencia de `checks(quest)` y crashes del módulo devolviendo un único `PreCheckResult` informativo (nunca propaga excepciones al CLI). Helper `all_passed(results)`.
- `common/cli/pre_checks/q01.py … q08.py` (nuevos): un módulo por quest con 7-9 checks conservadores cada uno, redactados sobre los starters reales:
  - **Q01**: `load_dotenv` import + llamada, `genai.Client(...)`, `client.models.generate_content(...)`, prompt no vacío.
  - **Q02**: hereda Q01 + `response.usage_metadata` + literales `"Prompt tokens:"`/`"Response tokens:"`/`prompt_token_count`/`candidates_token_count`.
  - **Q03**: `argparse`, `types` desde `google.genai`, `ArgumentParser`, `add_argument("user_prompt", ...)`, `types.Content(role="user", ...)`, `contents=` kwarg en `generate_content`.
  - **Q04**: import + valor de `common.prompts.system_prompt`, frase clave `LAS LEYES DEL ARKANUM SON ABSOLUTAS`, `types.GenerateContentConfig` con `system_instruction=`, `temperature=0` (regex excluye `0.X` con dígito no-cero).
  - **Q05**: chequea TAMBIÉN `common/functions/get_valid_target_path.py` (existe, parsea, usa `os.path.abspath`, contención por `commonpath`/`startswith`, placeholders reemplazados). Starter: `get_valid_target_path(...)` invocado, `pass_test`/`fail_test` presentes.
  - **Q06**: 3 schemas faltantes (`schema_get_file_content`/`schema_write_file`/`schema_run_python_file`) declarados como `types.FunctionDeclaration`; `call_function.py` con ≥5 refs a `schema_`; starter importa `available_functions`, pasa `tools=`, itera `response.function_calls`, imprime `Calling function:`, system_prompt actualizado.
  - **Q07**: 4 funciones reales en `function_map` (detectadas por nombre con quotes); `call_function` devuelve `types.Content` con `role="tool"` y `Part.from_function_response`; starter importa `call_function`, agrega `--verbose`, llama `call_function(...)`, hace `function_results.append(...)`.
  - **Q08**: `from common.config import MAX_ITERS`; `def main()` y `def generate_content(messages, verbose=False)` con cuerpo (no `pass` solo); `for _ in range(MAX_ITERS)` real; literal `Maximum iterations`; `role="tool"` en append al historial.
- `common/cli/commands/check.py` (reescrito): `--dry-run` corre los pre-checks y renderiza tabla Rich con icono ✔/✘ + detalle; exit 0 si pasaron todos, 1 si no. Modo normal corre pre-checks primero; si fallan, `typer.confirm(default=False)` antes de gastar cuota. Flag nuevo `--yes`/`-y` para auto-confirmar (útil en scripts).

**Smoke test ejecutado**
- `arkanum check 1..8 --dry-run` contra los starters actuales (todos con TODOs): tablas se renderizan, exit code 1 en todos, los fallos describen lo que falta de forma legible.
- Q01 con `solution/solution.py` pegado en el starter: las 8 checks pasan ✔, exit 0, mensaje "Pre-checks OK".
- `SyntaxError` artificial en el starter: el runner reporta "El starter tiene un SyntaxError." sin propagar la excepción al CLI.

**Desviaciones del plan**
- **Flag `--yes` agregado** (no estaba en el plan F10). Razón: al integrar con scripts/CI el `typer.confirm` colgaría; con `-y` se puede correr `arkanum check N -y` aceptando el riesgo de gastar cuota.
- **No se creó `parse_source` como helper de import (q-module)**. En la práctica cada `qNN.py` llama `parse_source` directamente del `_ast_helpers`. El plan mencionaba "Helpers — parse_source(quest)" como API por-quest, pero el helper actual recibe `path: Path` y los `qNN.py` resuelven el path con `starter_path(quest)`; es más reutilizable.
- **Pre-checks de Q05 cubren DOS archivos** (validador + starter). El plan los listaba juntos; queda explícito en la tabla de salida con checks separados para `get_valid_target_path.py` y para el starter.

**Hallazgos / tech debt**
- **`regex_in_source` matchea comentarios y docstrings**. Por ejemplo, los starters de Q02/Q04/Q06 ya mencionan en sus TODOs los strings `"Prompt tokens:"`, `temperature=0` o `Calling function:` — la regex los marca como ✔ aunque el aprendiz no haya implementado nada. Es **consciente**: los pre-checks son una pista, no un validador; los checks AST más fuertes (`has_attribute_access`, `has_call`, `has_function_def`) sí discriminan correctamente. Si en el futuro queremos endurecerlo, hay que hacer strip de comentarios antes de regex.
- **`has_function_def("main")` en Q01-Q07**: los starters no requieren `def main()`, así que no se valida. Sólo Q08 lo exige y tiene su propio check.
- **`function_map` de Q07 se detecta por nombre con quotes** (heurística textual sobre `call_function.py`). No es AST — un usuario que use comillas distintas (no `"..."`/`'...'`) rompería el check. Aceptable: PEP 8 + el repo usa siempre comillas dobles/simples estándar.
- **Smoke contra solution** sólo se hizo para Q01 (los otros 7 quests tienen `solution/main.py` o `solution/solution.py` pero requieren copiar manualmente la respuesta del archivo system_prompt o tocar varios archivos). Cuando se cierre F11 con su propia validación end-to-end, se puede ampliar el smoke programático.

**Tech debt cerrado**
- ~~Pre-checks no implementados~~ — `arkanum check N --dry-run` ahora corre validaciones AST + regex reales.

---

### Fase 9 — Actualizar READMEs de quests (`cce7dd9`, bitácora sin commitear)

**Entregado**
- Los 8 READMEs (`quests/quest_NN_*/README.md`) ahora muestran como camino principal `arkanum start N` y `arkanum check N`. El comando legacy `uv run python -m quests.quest_NN_*.starter.main` se preserva dentro de un `<details>` con título "Alternativa con uv run".
- Cada README añade al inicio de la sección "Ejecutar el Quest" la pista `> 💡 Para saber en qué quest estás: arkanum current`.
- Cada README menciona el [dashboard arcano](http://127.0.0.1:8765) y la celebración automática al pasar el check.
- Q06 y Q05 no tenían sección "Ejecutar el Quest" / "Criterio de éxito" — agregadas.
- Q08 añade nota sobre el evento de cierre de acto en el dashboard.
- **Typos corregidos** en 5 READMEs (paths viejos de carpetas que ya fueron renombradas):
  - Q01: `quest_01_first_agent` → `quest_01_first_invocation`
  - Q02: `quest_02_token_metadata` → `quest_02_arcane_gauge`
  - Q03: `quest_03_user_input` → `quest_03_apprentice_voice`
  - Q04: `quest_04_laws_of_arkanum` → `quest_04_arkanum_laws`
  - Q07: `quest_07_agent_embodiment` → `quest_07_agent_incarnation`

**Cambio mini-scope en F8**: `common/cli/commands/start.py`
- `arkanum start N` ahora acepta argumentos extras y los reenvía al starter como `python -m quests.quest_NN_*.starter.main args...`. Esto se descubrió necesario al actualizar Q03/Q04/Q07/Q08 cuyos starters esperan un prompt como argumento.
- Implementado con `typer.Context` + `ctx.args` y `context_settings={"allow_extra_args": True, "ignore_unknown_options": True}` en `main.py`.
- Sin esto, `arkanum start 3 "¿Qué es un agente IA?"` habría fallado con typer "Got unexpected extra argument".

**Desviaciones del plan**
- **Argumentos extras al starter** no estaba en el plan original de F8 ni F9. Lo añado aquí porque sin esto los READMEs mostrarían un comando que no funciona. Documentado en este detalle.
- **No se modificaron los starter.py ni check.py de los quests** — el plan F9 era solo READMEs (contenido pedagógico). Confirmado.

**Hallazgos / tech debt**
- Smoke test (TestClient) confirma que los 8 READMEs renderizan en `/quest/{slug}` con: `arkanum start N`, `arkanum check N`, `arkanum current`, banner correcto, cero typos de paths viejos.
- El bloque `<details>` con título "Alternativa con uv run" funciona porque `markdown-it-py` con `html=True` (configurado en F5) preserva HTML inline.
- Renderizado en el viewer del dashboard mantiene la jerarquía visual: bloques de código resaltados, links a docs (`/codex/...`) navegables.

---

### Fase 8 — Wizard init_user + CLI básico (`f84af06`, bitácora sin commitear)

**Entregado**
- `common/cli/helpers.py` (nuevo): `resolve_quest_by_number(n)` traduce 1..8 → `QuestMeta` (lanza `typer.BadParameter` si está fuera de rango); `starter_module`, `check_module`, `starter_path`, `check_path` para resolver los `python -m` targets; `run_module(module, args)` ejecuta el subprocess en `REPO_ROOT`.
- `common/cli/commands/init.py` (nuevo): wizard `arkanum init` con Rich Panel/Prompt/Confirm. Si ya existe aprendiz, ofrece actualizar nombre (default=no). Verifica `.env`, `GEMINI_API_KEY`, pinguea Gemini (omitible con `--skip-ping`). Pregunta si abrir el dashboard (omitible con `--no-dashboard`). Cierra con panel de comandos útiles.
- `common/cli/commands/current.py` (nuevo): muestra quest actual con quote de Zhyréon, rango por obtener, XP en juego y el comando para empezar (`arkanum start N`).
- `common/cli/commands/next_quest.py` (nuevo): muestra la siguiente quest tras la actual. **Renombrado de `next.py` a `next_quest.py`** porque `next` es builtin Python y causaría sombreado del nombre al importar.
- `common/cli/commands/progress.py` (nuevo): tabla Rich con todos los quests, su estado (completed/current/locked), rango. Encabezado con XP/level/quests completados.
- `common/cli/commands/start.py` (nuevo): `arkanum start <N>` ejecuta `python -m quests.quest_NN_*.starter.main` resolviendo N→slug.
- `common/cli/commands/check.py` (nuevo): `arkanum check <N>` ejecuta `python -m quests.quest_NN_*.check`. Flag `--dry-run` imprime mensaje placeholder explicando que los pre-checks reales llegan en F10.
- `common/cli/main.py`: registra las 6 nuevas commands (`init`, `current`, `next`, `progress`, `start`, `check`).

**Desviaciones del plan**
- **Módulo Python `next_quest.py`** en lugar de `next.py`. La función expuesta sigue siendo `next_quest()`, pero registrada en typer con `app.command(name="next")` para que el CLI se invoque como `arkanum next`. El detalle es solo organizativo: `import next` colisionaría con el builtin.
- **`init_user.py` / `show_progress.py` legacy NO se borran**. El plan sugería que `arkanum init` "reemplaza" al legacy, pero seguir manteniendo `python -m common.progress.init_user` funcionando da compatibilidad con READMEs viejos hasta que F9 los actualice. Decisión: dejar legacy intacto en F8, dejar la baja para una fase de pulido posterior si el bug UTF-8 ya no afecta.

**Hallazgos / tech debt**
- **Bug UTF-8 del legacy resuelto vía la ruta nueva**. `arkanum progress` pasa por `main.py` que ya reconfigura stdout/stderr a UTF-8 (F1). El legacy `show_progress.py` sigue rompiéndose si se invoca directo, pero ya no es el camino recomendado.
- `arkanum check N` muestra el aviso "este check consume cuota de Gemini" antes de ejecutar — comportamiento conservador que pide F4 plan original.
- Smoke test: `arkanum --help` lista las 8 commands; `arkanum current` muestra Quest 1 con quote; `arkanum next` muestra Quest 1 → Quest 2; `arkanum progress` renderiza tabla con icons; `arkanum check 9` da error útil; `arkanum check 1 --dry-run` muestra placeholder; `arkanum init --skip-ping --no-dashboard` detecta apprentice existente y declina sin escribir.

**Tech debt cerrado**
- ~~`show_progress.py` / `init_user.py` legacy con bug UTF-8~~ — resuelto: la ruta nueva (`arkanum progress` / `arkanum init`) no tiene el bug. Legacy sigue ahí por compatibilidad con READMEs viejos hasta F9.

---

### Fase 7 — Página de celebración (`a76a32d`)

**Entregado**
- `common/progress/db.py`: `record_quest_completion` ahora captura `xp_before` y `level_before` antes del UPDATE y los pasa en el payload de `emit_event`. La firma interna de `_notify_dashboard` se hizo kwargs-only para evitar errores de orden.
- `common/dashboard/routes/events.py`: `QuestCompletedPayload` extendida con `xp_before` / `xp_after` / `xp_reward` / `level_before` / `level_after` (todos opcionales, retrocompatible).
- `common/dashboard/services/celebration.py` (nuevo): `build_celebration_context(quest_meta)` busca el último evento `quest_completed` cuyo `quest_id` coincida (por slug o `db_id`), extrae stats, calcula `leveled_up = level_after > level_before`. Si no hay evento, cae a `apprentice.xp/level` para mostrar al menos la versión "diferida".
- `common/dashboard/routes/pages.py`: `/celebrate` ahora usa el servicio nuevo.
- `common/dashboard/templates/celebrate.html`: reescrito por completo. Hero con eyebrow ("Asciendes" si level-up, "Quest completado" si no), banner del quest, badge de rango con glow animado, quote de Zhyréon, stats (XP ganado / XP total / Nivel con highlight si level-up), dos CTAs (Volver al perfil / Continuar travesía).
- `common/dashboard/static/celebrate.js` (nuevo): confetti DOM-based, 36 partículas, 2.6s base + jitter, drift horizontal aleatorio, respeta `prefers-reduced-motion: reduce`.
- `common/dashboard/static/arcane.css` +400 líneas: bloque `Celebrate` (header, banner, rank-badge con `celebrate-glow` pulsante, stats con `celebrate-fade-in` escalonado), keyframes `confetti-fall` con custom properties `--drift` y `--rotate`, `viewer-cta--ghost` (variante del CTA existente), bloque `notification-toast` para el perfil, y un media query `(prefers-reduced-motion: reduce)` que apaga todas las animaciones y el confetti.
- **Toast en el perfil**:
  - `common/dashboard/routes/api.py`: refactor a `_read_events(only_unseen, limit, mark_seen)` reutilizable; nuevos endpoints `GET /api/events/peek` (no marca seen) y `POST /api/events/{id}/dismiss`.
  - `common/dashboard/templates/profile.html`: contenedor `#event-toast` con `data-event-poll-url=/api/events/peek` y `data-event-dismiss-url=/api/events/{id}/dismiss`.
  - `common/dashboard/static/dashboard.js`: `initToast()` con polling cada 15s; si encuentra un `quest_completed` no visto y no es el ya mostrado, renderiza un toast con título "⚜ Asciendes" o "⚜ Quest completado", body con rango + XP, CTA a `/celebrate?quest=...` y botón ✕ que hace POST al endpoint dismiss.

**Desviaciones del plan**
- **`peek` + `dismiss` explícito en lugar de marcar `seen=1` al renderizar**. El plan original sugería un partial server-side que renderizara el toast directamente. Lo cambié a JSON + JS porque (a) si marcáramos `seen=1` al hacer GET del partial, refrescar la página perdería el toast antes de que el usuario lo viera, (b) el dismiss explícito por el usuario es semánticamente correcto: solo se "ve" cuando el usuario lo descarta o lo abre, (c) `recent_events` ya consume + marca seen para el flujo `webbrowser.open`; el del perfil necesita una semántica distinta. Documentado en docstrings de `api.py`.
- **No se creó `partials/notifications.html`**. La razón: el toast se renderiza enteramente en JS desde el payload del evento, no desde HTML server-rendered. Esto evita un round-trip extra. El partial seguirá siendo útil cuando haya múltiples tipos de eventos a tipear (F15 cierre de acto, F8 wizard, etc.); por ahora un solo tipo no justifica el partial.

**Hallazgos / tech debt**
- Smoke test TestClient cubre: `/celebrate` sin evento (versión diferida), POST evento con level-up, `/celebrate` rehidratada (detecta "Asciendes Nivel 2", muestra +50 XP y rango), peek idempotente, dismiss específico, dismiss inexistente → 404.
- Sanity con server real arrancado en puerto 8765: `/celebrate` y `/api/events/peek` responden 200.
- Compatibilidad: el endpoint POST `/events/quest-completed` acepta payloads viejos (sin los campos `xp_before` etc.) porque todos son `| None = None`. F6 no rompe.
- El throttle de `open_celebration` (5s, F6) se mantiene; abrir manualmente `/celebrate` no lo afecta.

---

### Fase 6 — Integración CLI + notificaciones (`dc71ecc`)

**Entregado**
- `common/progress/notify.py`:
  - `emit_event(kind, payload)` → `httpx.post('http://127.0.0.1:{port}/events/{kind}', json=payload, timeout=0.3)`. Si el server no responde o falla, persiste el evento directamente en la tabla `events` con `seen=0` (fallback sin HTTP).
  - `open_celebration(quest_id)` → `webbrowser.open(.../celebrate?quest=...)` con throttle de 5s vía `.last_celebrate.timestamp`.
  - Ambos respetan `ARKANUM_NO_DASHBOARD=1`. `open_celebration` además respeta `ARKANUM_NO_CELEBRATION=1`.
- `common/dashboard/routes/events.py` (router nuevo): `POST /events/quest-completed` con pydantic `QuestCompletedPayload`; persiste en `events` con `kind="quest_completed"` y devuelve `{ok, event_id, redirect: "/celebrate?quest=..."}`.
- `common/dashboard/routes/api.py`: `GET /api/events/recent?limit=N` — devuelve eventos con `seen=0` y los marca como `seen=1` en la misma transacción (evita repetir notificaciones).
- `common/dashboard/routes/pages.py`: `GET /celebrate?quest=...` (resolución por slug o por `db_id`).
- `common/dashboard/templates/celebrate.html`: placeholder con quote de Zhyréon (la animación completa llega en F7).
- `common/dashboard/server.py`: registra `events.router`.
- `common/progress/db.py`: en `record_quest_completion`, después del INSERT exitoso, llama `_notify_dashboard()` que invoca `ensure_started()` + `emit_event("quest-completed", ...)` + `open_celebration(...)`. Cada side-effect va en su propio try/except — un fallo NO revierte el commit ni rompe `check.py`.

**Desviaciones del plan**
- **`celebrate.html` creado aquí en lugar de F7**. Era necesario para que el endpoint POST devuelva una `redirect` que el usuario pueda seguir manualmente y para que el GET `/celebrate` no devuelva 404. La animación completa con confetti/level-up sigue planificada para F7 — este es un placeholder estético mínimo.
- **`kind` en BD usa snake_case (`quest_completed`)** mientras que la URL usa kebab-case (`/events/quest-completed`). Es la convención REST + Python convencional. El endpoint hace la traducción. Documentado por si confunde después.

**Hallazgos / tech debt**
- El test end-to-end con `ARKANUM_NO_DASHBOARD=1` confirma que `record_quest_completion` funciona sin side-effects: INSERT en `quest_completion` pasa, no se arranca server, no se intenta abrir browser, no se persiste evento.
- Sin opt-out + sin server: `emit_event` persiste el evento como fallback. El polling de `/api/events/recent` lo recogerá la próxima vez que el dashboard abra.
- Con server activo (TestClient): POST `/events/quest-completed` inserta evento, GET `/api/events/recent` lo trae una vez y la segunda llamada está vacía (seen=1 idempotente).
- **Import circular potencial** entre `common.progress.db` y `common.dashboard.lifecycle`: resuelto con import diferido dentro de `_notify_dashboard()` (no en el top-level del módulo).
- `.last_celebrate.timestamp` ya estaba en `.gitignore` desde F0.

---

### Fase 5 — Viewer de READMEs y Códex (`3ffc6da`)

**Entregado**
- `common/dashboard/services/markdown.py`: render con `markdown-it-py` (CommonMark + tablas + strikethrough, `html=True` para permitir banners `<p align="center"><img>`); syntax highlight con `pygments` (theme **monokai**, `cssclass="hl"`); reescritura de links/imágenes:
  - `../../docs/foo/bar.md` → `/codex/foo/bar`
  - `../../assets/images/x.png` → `/assets/images/x.png`
  - `../quest_XX_*/README.md` → `/quest/quest_XX_*`
  - Externos (`http://`, anchors, `mailto:`) intactos.
  - Aplica también a HTML inline (regex sobre `<a href>` / `<img src>` antes de pasar a markdown-it).
- `_extract_toc` extrae headings H1–H3 con anchors slugificados; el renderer inyecta `id="…"` en cada heading para hacer match con el TOC.
- `resolve_codex_path(rel)` y `resolve_quest_readme(slug)` con sanitización (evitan path traversal con `..`).
- `pygments_css()` expuesto a través de `GET /api/pygments.css` y referenciado en `base.html`.
- `routes/pages.py`: `GET /quest/{slug}` (404 si slug desconocido; vista "sellado" si `status == "locked"`; render del README en otro caso, con flag `already_read` para deshabilitar el botón mark-read). `GET /codex` y `GET /codex/{path:path}` con breadcrumbs.
- `routes/api.py`: `POST /api/quests/{slug}/mark-read` (INSERT OR REPLACE en `quest_reading`); `GET /api/pygments.css`.
- `services/progress.py`: helper `is_quest_readme_read(db_id)`.
- Templates nuevos: `quest_view.html` (TOC sticky + prose, sealed view + botón mark-read) y `codex_view.html` (breadcrumbs + TOC + prose).
- `templates/map.html`: cartas `completed` / `current` ahora son `<a href="/quest/{slug}">`; `locked` siguen como `<article>`.
- `static/dashboard.js`: ampliado con `initCopyButtons()` (botón "Copiar" sobre cada `.codeblock`, con clipboard API + fallback `execCommand`) y `initMarkRead()` (POST asincrónico, deshabilita el botón al éxito).
- `static/arcane.css` +400 líneas: variantes del map card como link, layout `viewer-layout` grid 220px+1fr, TOC sticky con bordes dorados por nivel, prose con headings serif/dorado, blockquotes, tablas, codeblocks con botón copy que aparece on-hover, sealed view y CTA, responsive (TOC colapsa abajo en <640px).

**Desviaciones del plan**
- **HTMX no vendorizado**. El plan mencionaba `htmx.min.js` como opcional para F5; no fue necesario. El botón mark-read y el polling existente se cubren con `fetch` vanilla en `dashboard.js` (~30 líneas extra). Esto cierra el tech debt de "HTMX no vendorizado" registrado en F4: lo borramos del backlog porque el viewer no lo necesita y las fases siguientes tampoco lo requieren explícitamente.
- **CSS de Pygments servido dinámicamente** vía `GET /api/pygments.css` en vez de un `pygments.css` estático. Razón: si en F17 cambiamos el theme (monokai → otro), no hay que regenerar nada manualmente.

**Hallazgos / tech debt**
- El `quest_reading.quest_id` PK guarda el `db_id` ("La Primera Invocación") porque es lo que ya usan las otras tablas (`quest_completion.quest_id`). Mantiene consistencia con el código existente; los endpoints reciben `slug` y traducen vía `quest_by_slug`.
- Los READMEs reales de Q01–Q08 usan `<p align="center"><img src="../../assets/images/...">` para banners. La reescritura por regex sobre HTML inline cubre este caso sin necesidad de un parser HTML real.
- `markdown-it-py` en versión actual requiere `env` en `renderer.renderToken(...)` (cambió respecto a versiones anteriores). Captado en smoke test, corregido antes del cierre.
- El TestClient smoke test confirma: render quest, sealed view, 404 slug, render codex root, render codex anidado, 404 path, CSS pygments, POST mark-read OK, POST mark-read 404, links en /map.

---

### Fase 4 — Setup global + doctor (`170b57a`)

**Entregado**
- `common/progress/setup_diagnostics.py`: 9 checks (python, uv, dependencias, .env, GEMINI_API_KEY presente, API key validada, BD inicializada, dashboard activo, workspace); cache en `.setup_cache.json` solo para éxitos por 24h (los fallos siempre re-pingean); SHA-256 del key invalida el cache al cambiar la clave.
- `common/cli/commands/doctor.py`: comando `arkanum doctor` con output Rich (table sin bordes, iconos coloreados, detail en dim); flag `--skip-ping`; exit code 1 si hay errores.
- `common/dashboard/services/setup_check.py`: helper `build_setup_context(skip_api_ping=True)` por default (el polling no quema cuota Gemini).
- `common/dashboard/routes/api.py`: `GET /api/setup/status` retorna fragmento HTML.
- `routes/pages.py`: `GET /setup` página completa con sección de ayuda + links externos.
- Templates: `partials/setup_panel.html`, `setup.html`.
- `templates/profile.html`: panel embebido arriba del hero.
- `templates/base.html`: link "Setup" en nav, carga `dashboard.js`.
- `static/dashboard.js`: polling vanilla JS (~15 líneas) que refresca `[data-poll-url]` cada N ms.
- `arcane.css` +160 líneas: `setup-panel` con borde dorado, `setup-pill` en 3 variantes (verde/ámbar/rojo), grid de checks responsive.

**Desviaciones del plan**
- **Polling vanilla JS en vez de HTMX vendorizado**. El plan canónico mencionaba HTMX (`htmx.min.js` en `/static/`). Decidí usar `dashboard.js` minimalista porque F4 solo necesita polling simple (fetch + replace innerHTML). HTMX se vendorizará en **Fase 5** cuando necesitemos `hx-swap`, `hx-target`, etc. para el viewer de quests.

**Hallazgos / tech debt**
- **`uv` aparece como FAIL en `arkanum doctor`** en el venv actual. Razón: instalación inicial vía `pip install --user uv` puso el binario en site-packages del Python de sistema, no en el venv. El mensaje del check sugiere correctamente la instalación oficial vía `astral.sh/uv`. Cuando el usuario lo instale así, el check pasará automáticamente sin cambios de código.

---

## Decisiones acumuladas (resumen)

| Decisión | Fase | Resumen |
|---|---|---|
| Build system hatchling | F0 | Necesario para `[project.scripts]` |
| UTF-8 reconfigure en arkanum | F1 | Resuelve cp1252 para el path nuevo |
| Fuentes de sistema | F2 | Diferido a F17 embeber Cinzel/Inter |
| Vanilla JS polling | F4 | HTMX se vendoriza en F5 |
| HTMX descartado | F5 | Vanilla `fetch` cubre polling + mark-read + copy |
| Pygments CSS servido dinámico | F5 | `/api/pygments.css` permite cambiar theme sin regenerar |
| Toast `peek`+`dismiss` | F7 | En vez de `seen=1` al renderizar; preserva el toast hasta que el usuario lo descarta |
| Legacy `init_user`/`show_progress` intacto | F8 | `arkanum init`/`progress` lo reemplazan; legacy queda hasta F9 actualice los READMEs |
| Pre-checks mix AST + regex | F10 | AST para imports/llamadas/atributos; regex para literales tipo "Prompt tokens:" — consciente de que regex matchea comentarios |
| Flag `--yes` en `arkanum check` | F10 | Para scripts/CI que no pueden responder al `typer.confirm` |
| Modal de pistas inline en quest_view | F11 | En vez de partial — sólo se usa en esa página, igual que el toast de F7 |
| Auto-unlock de pista N+1 en cliente | F11 | UX inmediata; server sigue validando orden estricto |
| Placeholders ya renderizables en F11 | F11 | Texto "Contenido pendiente — F12" se ve decente desde el primer commit |
| Pistas: títulos `## El susurro` etc. | F12 | En vez del nombre del quest (redundante con la carta) |
| L3 puede pasar de 4 líneas si la estructura lo exige | F12 | Q07/Q08 lo necesitan para mostrar la separación crítica |
| Sin botón "Copiar" en pistas | F12 | Selector limitado a `.viewer-prose .codeblock`; forzar lectura |

## Tech debt acumulado

1. **Fuentes Cinzel/Inter no embebidas** (F17).
2. ~~**HTMX no vendorizado**~~ — descartado en F5.
3. ~~**Cartas del mapa no clickeables**~~ — resuelto en F5.
4. ~~**`show_progress.py` / `init_user.py` legacy con bug UTF-8**~~ — ruta nueva (`arkanum *`) no tiene el bug; legacy se mantiene por compat hasta F9.

---

## Próxima fase

### Fase 13 — Tracking tiempo/intentos + logros calculados (~4h)

**Objetivo**
> Done cuando: cada quest registra su `first_attempt_at` la primera vez que el aprendiz corre `arkanum start` o `arkanum check`, cuenta intentos en `quest_attempts` por cada `check.py` ejecutado (pase o falle), y al completar guarda `total_time_seconds = completed_at - first_attempt_at`. Logros "One shot" (`attempts == 1`) y "Sin red" (`hint_usage` vacía) se calculan on-the-fly y aparecen en el perfil + en la celebración + en el viewer del quest.

**Plan**
1. **Captura de `first_attempt_at`**:
   - `common/cli/commands/start.py` y `commands/check.py` llaman a una función nueva `register_attempt(quest, kind)` antes de ejecutar el subprocess.
   - `common/progress/db.py` expone:
     - `register_first_attempt(quest_id)` — `INSERT OR IGNORE` en `quest_completion` con `first_attempt_at = now`, `attempts = 0`, sin tocar `completed_at`.
     - `record_quest_attempt(quest_id, passed, failure_reason)` — `INSERT` en `quest_attempts` siempre, y `UPDATE quest_completion SET attempts = attempts + 1` cuando `completed_at IS NULL`.
2. **Cierre de tiempos en `record_quest_completion`**:
   - Calcular `total_time_seconds = now - first_attempt_at` si `first_attempt_at` no es null.
   - Persistir en `quest_completion`.
3. **Logros on-the-fly** (sin tabla nueva):
   - `common/dashboard/services/achievements.py` (nuevo):
     - `achievements_for(quest_db_id) -> list[Achievement]` calcula los logros aplicables.
     - `one_shot_eligible(quest)`, `no_red_eligible(quest)` reutilizando `is_no_red_eligible` de F11.
   - Otros candidatos cuando se cierra todo el quest: "Velocista" si `total_time_seconds < 600`, etc. — opcional, depende del scope.
4. **UI**:
   - **Perfil**: badges junto al rango actual con conteo de logros.
   - **Quest view** (`quest_view.html`): si el quest está completed, sección "Trofeos de este quest" listando los logros obtenidos.
   - **Celebración** (`celebrate.html`): si en el evento `quest_completed` se incluyen logros, mostrarlos junto a la pila de XP.
5. **Tests**:
   - Smoke: `register_first_attempt` idempotente.
   - `record_quest_attempt` incrementa `attempts` y deja huella en `quest_attempts`.
   - `one_shot_eligible(quest)` → True si `attempts == 1`, False con `attempts >= 2`.
   - `no_red_eligible(quest)` → False tras un POST a `/api/quests/.../hints/1`.

**Pre-condiciones**
- Tablas `quest_attempts` y `hint_usage` existen (✅ F0).
- Columnas `attempts`, `first_attempt_at`, `total_time_seconds` en `quest_completion` (✅ F0).
- Pre-checks de F10 invocan al `check.py` real con retorno conocido (✅).

**Archivos a tocar / crear**
- ✏️ `common/progress/db.py` (helpers + actualización de `record_quest_completion`)
- ➕ `common/dashboard/services/achievements.py`
- ✏️ `common/cli/commands/start.py` y `commands/check.py` (registrar intento)
- ✏️ `common/dashboard/templates/profile.html`, `quest_view.html`, `celebrate.html`
- ✏️ `common/dashboard/static/arcane.css` (estilos de trofeos)

**Riesgos detectados**
- **Bug retroactivo**: aprendices que ya completaron quests antes de F13 no tienen `first_attempt_at`. Asumir `total_time_seconds = NULL` y mostrar "—" cuando esto pase.
- **Conteo de `attempts` debe incrementarse incluso si el check falla**, pero NO después de completed_at. La query `UPDATE ... WHERE completed_at IS NULL` lo cubre.
- **Acoplamiento CLI ↔ DB**: ahora `arkanum start/check` toca BD. Si `ARKANUM_NO_DASHBOARD=1`, debe seguir funcionando (test/CI).

**Criterio de cierre de la fase**
- `arkanum start 1` por primera vez crea row en `quest_completion` con `first_attempt_at` y `attempts=0`.
- `arkanum check 1` (que falla pre-checks o el check real) deja una row en `quest_attempts` y suma a `attempts`.
- Pasar el check real persiste `total_time_seconds`.
- `achievements_for("La Primera Invocación")` después de completar al primer intento sin pistas devuelve `["one_shot", "no_red"]`.
- Cierre con commit `feat(dashboard): fase 13 - tracking tiempo e intentos`.
- Actualizar este archivo (sección "Detalle por fase" + tabla + "Próxima fase").

---

_Plan original de F12 (cerrado en `25c2b9b`):_

### Fase 12 — Sistema de pistas, contenido (~5h)

**Objetivo**
> Done cuando: los 24 archivos `quests/quest_NN_*/hints/*.md` tienen contenido pedagógico real adaptado a los TODOs de cada starter; reemplaza los placeholders "Contenido pendiente — F12" de F11.

**Plan resumido**
1. Por cada quest, identificar el TODO bloqueo y redactar I (pregunta) / II (nombre del concepto) / III (snippet 2-4 líneas).
2. Mantener tono arcano y vocabulario alineado con los TODOs del starter.
3. Smoke con TestClient: 24 invocaciones POST verifican títulos y bloque `<pre>` en L3.

---

_Plan original de F11 (cerrado en `4388260`):_

### Fase 11 — Sistema de pistas, mecánica (~5h)

**Objetivo**
> Done cuando: cada quest expone hasta 3 pistas en orden estricto, con confirmación explícita y persistencia en `hint_usage`.

**Plan resumido**
1. 24 placeholders `.md` en `quests/quest_NN_*/hints/`.
2. `common/dashboard/services/hints.py` con `HintMeta`, `list_hints_for`, `get_hint`, `request_hint`, `used_hints`, `is_no_red_eligible`.
3. Endpoints `GET /api/quests/{slug}/hints` y `POST /api/quests/{slug}/hints/{level}`.
4. UI en `quest_view.html`: bloque "Las ofrendas del aprendiz" + modal de confirmación.
5. CSS + JS vanilla (initHints): handler de click, modal, POST, inyección del HTML revelado, auto-unlock de N+1.
6. Smoke con TestClient: orden estricto, idempotencia, render del .md.

---

_Plan original de F10 (cerrado en `a17d8e3`):_

### Fase 10 — Pre-check local (~4h)

**Objetivo**
> Done cuando: `arkanum check N --dry-run` ejecuta validaciones estáticas (regex + AST simple) sobre el `starter/main.py` del quest N y reporta si pasaron sin invocar Gemini. `arkanum check N` corre los pre-checks primero y pide confirmación antes de gastar cuota si fallan.

**Plan resumido**
1. `common/cli/pre_checks/` nuevo paquete con `qNN.py` (1..8).
2. `runner.py` con `PreCheckResult` y `run_pre_checks(quest)`.
3. `commands/check.py` reescrito: `--dry-run` corre pre-checks, modo normal pide confirmación si fallan.
4. Helpers AST + regex en `_ast_helpers.py`.
5. Smoke test: cada `qNN.py` se ejecuta contra el starter actual y reporta resultados coherentes.

---

_Plan original de F8 (cerrado en `f84af06`):_

### Fase 8 — Wizard init_user + CLI básico (~4h)

**Objetivo**
> Done cuando: `arkanum init` reemplaza al `init_user.py` legacy con un wizard arcano (nombre del aprendiz, ping a Gemini, opt-in a abrir el dashboard). Los comandos `arkanum current`, `arkanum next`, `arkanum progress`, `arkanum start <N>`, `arkanum check <N>` funcionan desde la raíz del repo y respetan UTF-8.

**Plan**
1. **`common/cli/commands/init.py`** — `arkanum init`:
   - Rich `Prompt` para nombre del aprendiz (default si ya existe).
   - Verifica `.env` y `GEMINI_API_KEY`; ofrece pegar key si falta.
   - Ping real a Gemini (con timeout) usando `setup_diagnostics`.
   - Insert/update en `apprentice` con rank inicial "Aprendiz del Arkanum".
   - Pregunta "¿Abrir el dashboard?" → si sí, `lifecycle.start()` + `webbrowser.open`.
2. **`common/cli/commands/current.py`** — muestra quest actual + comando para empezar (`arkanum start N`).
3. **`common/cli/commands/next.py`** — muestra próxima quest (la que sigue a la `current`).
4. **`common/cli/commands/progress.py`** — wrapper sobre `show_progress` legacy, sin el bug UTF-8 (todo via el reconfigure de `main.py`).
5. **`common/cli/commands/start.py`** — `arkanum start <N>` ejecuta `python -m quests.quest_NN_*.starter.main` resolviendo N → slug.
6. **`common/cli/commands/check.py`** — `arkanum check <N>` ejecuta `python -m quests.quest_NN_*.check`; flag `--dry-run` que solo corre pre-checks (la implementación de pre-checks reales llega en F10, aquí solo el flag con un mensaje placeholder).
7. **Compatibilidad**: `uv run python -m quests.quest_XX.starter.main` sigue funcionando; las nuevas commands son atajos.

**Pre-condiciones**
- `arkanum` ya está como entry point (✅ F0).
- `lifecycle.start()` arranca server detached (✅ F1).
- `setup_diagnostics` ya pinguea API key (✅ F4).
- `record_quest_completion` emite eventos al dashboard (✅ F6).

**Archivos a tocar / crear**
- ➕ `common/cli/commands/init.py`
- ➕ `common/cli/commands/current.py`
- ➕ `common/cli/commands/next.py`
- ➕ `common/cli/commands/progress.py`
- ➕ `common/cli/commands/start.py`
- ➕ `common/cli/commands/check.py`
- ✏️ `common/cli/main.py` (registrar las nuevas commands en typer app)
- ✏️ `common/cli/helpers.py` (resolución `N → slug` y descubrimiento de quests)

**Riesgos detectados**
- `init_user.py` legacy puede tener lógica que no esté en `setup_diagnostics`. Revisar antes de borrarlo o reemplazarlo. Decisión preliminar: dejar el legacy intacto y solo añadir `arkanum init` como alternativa; el legacy se removerá en una fase de pulido posterior.
- `arkanum start N` debe pasar correctamente `argv` al subprocess Python, no via shell. Usar `subprocess.run([sys.executable, "-m", ...])`.
- El bug UTF-8 del legacy `show_progress.py` se resuelve naturalmente: `arkanum progress` pasa por `main.py` que reconfigura UTF-8 antes de invocar.

**Criterio de cierre de la fase**
- `arkanum init` corre, pregunta nombre, valida API key, opcionalmente abre dashboard, inserta apprentice.
- `arkanum current` imprime quest actual con quote y comando para empezar.
- `arkanum start 1` ejecuta el starter de Q01.
- `arkanum check 1 --dry-run` imprime mensaje "pre-checks aún no implementados (F10)" sin invocar Gemini.
- `arkanum progress` muestra XP/level/quests sin error de cp1252.
- Cierre con commit `feat(dashboard): fase 8 - wizard init_user + CLI basico`.
- Actualizar este archivo (sección "Detalle por fase" + tabla + "Próxima fase").
