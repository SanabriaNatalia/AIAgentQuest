# Bitácora de Avance — Dashboard Arcano

> **Plan canónico:** [`2026-05-19-plan-dashboard-arcano.md`](2026-05-19-plan-dashboard-arcano.md) — define **qué hay que hacer** en total.
> **Este archivo:** refleja **qué se ha hecho efectivamente**, desviaciones del plan, hallazgos y tech debt.
> **Convención:** se actualiza al cierre de cada fase. Cualquier sesión nueva debería leer estos dos archivos antes de continuar.

---

## Estado actual

| Campo | Valor |
|---|---|
| **Branch** | `feat/dashboard-arcano` |
| **Última fase completada** | Fase 7 — Página de celebración |
| **Próxima fase** | Fase 8 — Wizard init_user + CLI básico |
| **Tiempo invertido aprox.** | ~31h (acumulado Fases 0-7) |
| **Tiempo restante estimado** | ~37h (Fases 8-17) |

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
| 7 | Celebración | ✅ | _pendiente commit_ | 3h | Toast del perfil usa endpoint `peek` (no consume) + `dismiss` explícito en vez de marcar `seen=1` al renderizar; service `celebration.py` reconstruye contexto desde el último evento `quest_completed` |
| 8 | Wizard init + CLI básico | ⏳ | — | 4h | Aquí se resuelve el bug UTF-8 de `show_progress`/`init_user` legacy |
| 9 | Actualizar READMEs quests | ⏳ | — | 2h | — |
| 10 | Pre-check local | ⏳ | — | 4h | — |
| 11 | Pistas (mecánica) | ⏳ | — | 5h | — |
| 12 | Pistas (contenido) | ⏳ | — | 5h | Trabajo pedagógico, no de código |
| 13 | Tracking tiempo/intentos | ⏳ | — | 4h | — |
| 14 | Tracking costo | ⏳ | — | 2h | — |
| 15 | Detección cierre acto | ⏳ | — | 2h | — |
| 16 | Visualización agent loop | ⏳ | — | 6h | — |
| 17 | Pulido | ⏳ | — | 4h | Embeber fuentes Cinzel/Inter aquí |

**Total acumulado:** Fases 0-7 = ~31h reales / 30h planificadas (cercano al estimado).

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

### Fase 7 — Página de celebración (_pendiente commit_)

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

## Tech debt acumulado

1. **`show_progress.py` / `init_user.py` legacy** siguen con bug UTF-8 (resolución natural en F8 al reemplazar por `arkanum progress` / `arkanum init`).
2. **Fuentes Cinzel/Inter no embebidas** (F17).
3. ~~**HTMX no vendorizado**~~ — descartado en F5, no se necesita.
4. ~~**Cartas del mapa no clickeables**~~ — resuelto en F5.

---

## Próxima fase

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
