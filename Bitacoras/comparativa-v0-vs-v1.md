# AI Agent Quest — v0 vs v1

> Comparativa lado a lado entre la versión original del laboratorio y la versión con dashboard arcano y CLI unificado.
> Asume todas las fases (0-17) implementadas.

---

## Resumen en una frase

| Versión | Definición |
|---|---|
| **v0 (antigua)** | Curso autoguiado por terminal: editar `starter/main.py` → ejecutar starter → ejecutar `check.py` → repetir. Progreso persistido en SQLite local, visible solo vía `show_progress`. |
| **v1 (nueva)** | El **mismo curso por terminal**, ahora acompañado de un dashboard arcano siempre activo en `localhost:8765`, un CLI unificado `arkanum`, sistema de pistas, tracking de tiempo y costo, diagnóstico de setup, viewer de READMEs y celebraciones en vivo. **La filosofía no cambia: el aprendiz sigue editando y ejecutando desde su editor/terminal.** El dashboard es trofeero, no quest-runner. |

---

## Filosofía: qué se preserva intacto

La regla de oro del laboratorio sigue vigente al 100%:

| Principio | Cómo se respeta en v1 |
|---|---|
| El aprendiz **edita código** en su editor | El dashboard no tiene editor inline |
| El aprendiz **ejecuta comandos** en su terminal | El dashboard no tiene botón "ejecutar quest" |
| La **única validación real** es `check.py` | El dashboard nunca otorga XP por sí mismo |
| La **comprensión** importa más que pasar el quest | Las pistas requieren confirmación explícita; nunca se muestran solas |
| **Cero magia oculta** | Toda la BD, logs y archivos siguen siendo locales e inspeccionables |
| **Sin nube, sin cuenta** | Single-user local, sin servidor remoto, sin login |

---

## Cambio de experiencia, paso a paso

### v0 — Workflow del aprendiz hoy

```text
1. uv sync                                              (instalar)
2. crear .env con GEMINI_API_KEY                       (a ciegas — sin verificación)
3. uv run python -m common.progress.init_user          (registro, sin validar API key)
4. abrir quests/quest_01_first_invocation/README.md    (lectura en VSCode)
5. editar starter/main.py                              (TODOs guiados)
6. uv run python -m quests.quest_01_first_invocation.starter.main   (probar)
7. uv run python -m quests.quest_01_first_invocation.check          (validar, gasta Gemini)
8. uv run python -m common.progress.show_progress      (ver progreso en terminal)
9. → siguiente quest (repetir, sin saber tiempo ni intentos)
```

**Fricción**: comandos largos, sin verificación previa, sin feedback visual, errores silenciosos hasta el `check.py`.

### v1 — Workflow del aprendiz con dashboard

```text
1. uv sync                                              (instalar)
2. arkanum doctor                                       (diagnóstico: te dice exactamente qué falta)
3. crear .env con GEMINI_API_KEY                       (doctor valida con un ping real)
4. arkanum init                                         (wizard: nombre + validación API + arranca dashboard)
                                                        → http://127.0.0.1:8765 se abre solo
5. abrir el README en el dashboard (estética arcana) o en VSCode
6. editar starter/main.py                              (mismo flujo de antes)
7. arkanum check 1 --dry-run                            (pre-check local, sin gastar Gemini)
8. arkanum check 1                                      (validación real)
                                                        → al pasar: celebración auto-abre,
                                                        XP suma en vivo, rango desbloqueado
9. → siguiente quest, con tu tiempo y nº de intentos visibles en el mapa
```

**Fricción**: comandos cortos, diagnóstico proactivo, feedback visual constante, pistas disponibles si te atascas.

---

## Comandos: tabla de equivalencias

| Tarea | v0 | v1 |
|---|---|---|
| Registrar aprendiz | `uv run python -m common.progress.init_user` | `arkanum init` (wizard con validación) |
| Ver progreso | `uv run python -m common.progress.show_progress` | `arkanum progress` o abrir el dashboard |
| Saber cuál es mi quest actual | _leer mentalmente el output_ | `arkanum current` |
| Ejecutar starter del quest 3 | `uv run python -m quests.quest_03_apprentice_voice.starter.main "prompt"` | `arkanum start 3 "prompt"` |
| Validar quest 3 | `uv run python -m quests.quest_03_apprentice_voice.check` | `arkanum check 3` |
| Validación sin gastar Gemini | _no existe_ | `arkanum check 3 --dry-run` |
| Diagnóstico de setup | _no existe_ | `arkanum doctor` |
| Tokens consumidos | _no existe_ | `arkanum cost` |
| Ver agente trabajar en vivo (Q07-Q08) | _solo verbose en stdout_ | `arkanum run 7 "prompt"` + dashboard |
| Pedir una pista | _no existe_ | botón en `/quest/{slug}` del dashboard |
| Compartir cierre de acto | _no existe_ | `/milestones` muestra los actos cerrados |

---

## Capacidades nuevas (tabla maestra)

| Categoría | v0 | v1 |
|---|---|---|
| **Setup** | A ciegas hasta que algo falle | `arkanum doctor` con 9 checks; panel siempre visible; cache de 24h del ping a Gemini |
| **Onboarding** | Pregunta solo el nombre | Wizard: nombre + valida API + arranca dashboard + abre browser |
| **Visualización del progreso** | `print()` en terminal | Dashboard always-on: perfil + mapa + rangos + milestones |
| **Mapa del curso** | Texto plano del README | Mapa interactivo con 4 actos, 8 cartas con estados (completed/current/locked), banners, animación pulse para la quest activa |
| **Rangos** | String en `current_rank` | Galería de 8 cartas con badge en numeral romano, quote de Zhyréon, locked en silueta |
| **Lectura de READMEs** | Markdown en VSCode | Viewer con estética arcana, syntax highlight, TOC lateral, links al Códex, botón "copiar" en code blocks |
| **Lectura del Códex** | Markdown en VSCode | Viewer dedicado en `/codex/...` con navegación cruzada desde los READMEs |
| **Pistas pedagógicas** | Inexistente | 3 niveles por quest (susurro / revelación / manifestación); orden estricto; confirmación previa; afectan logro "Sin red" |
| **Tracking de tiempo** | Inexistente | `first_attempt_at` por quest, `total_time_seconds` al completar |
| **Tracking de intentos** | Inexistente | `attempts` count + logro "One shot" si pasaste al primer intento |
| **Tracking de costo** | Inexistente | Log de invocaciones a Gemini en `.quest_calls.log`; `arkanum cost` resume |
| **Pre-validación** | El `check.py` siempre gasta Gemini | Pre-check estático (regex + AST) detecta TODOs faltantes sin tocar la API |
| **Celebración** | Panel Rich en terminal | Animación con partículas en `/celebrate` + auto-open del browser |
| **Notificaciones cross-terminal** | Inexistente | El check en una terminal hace aparecer notificación viva en el dashboard de otra |
| **Cierre de acto** | Sin marcar | Evento `act_closed` detectado automáticamente + página `/milestones` con quote de Zhyréon y rangos del acto |
| **Visualización del agent loop** | Solo `--verbose` en stdout | Página `/live-agent` con grafo en vivo de tool_call → observation → tool_call durante Q07-Q08 |
| **READMEs de quests** | Comandos largos | Documentación actualizada con `arkanum start/check N` (los originales siguen funcionando) |
| **Encoding Windows** | Bug pre-existente: UnicodeEncodeError en cp1252 | Reconfigure UTF-8 stdout/stderr al inicio del CLI |

---

## Arquitectura nueva (qué se agregó)

### v0 — Componentes existentes (sin cambios)

```
common/
├── progress/         (init_user, show_progress, db, levels)
├── functions/        (tools del agente: get_files_info, etc.)
├── prompts/          (system_prompt)
└── utils/            (ui rich)

quests/
└── quest_NN_*/       (README, starter, solution, check)

docs/                 (Arcane Codex — markdown)
assets/images/        (banners + logos)
```

### v1 — Lo agregado

```
common/
├── cli/                                  ← NUEVO: CLI unificado arkanum
│   ├── main.py                           (typer app, UTF-8 fix)
│   └── commands/
│       ├── dashboard.py                  (start/stop/status/logs/open)
│       ├── doctor.py                     (diagnóstico)
│       ├── start.py / check.py / run.py  (wrappers de quest)
│       ├── current.py / next.py
│       ├── progress.py / cost.py
│       └── precheck.py
│
├── dashboard/                            ← NUEVO: server FastAPI
│   ├── server.py                         (app factory + routers)
│   ├── lifecycle.py                      (start/stop detached, ensure_started)
│   ├── __main__.py                       (uvicorn entry para spawn)
│   ├── templating.py                     (Jinja2 singleton)
│   ├── routes/
│   │   ├── health.py                     (ping)
│   │   ├── api.py                        (fragmentos HTML + JSON)
│   │   ├── events.py                     (recibe POST de notify.py)
│   │   ├── hints.py                      (sistema de pistas)
│   │   └── pages.py                      (/, /map, /ranks, /quest/{slug}, /codex/...)
│   ├── services/
│   │   ├── quest_catalog.py              (metadata estática de 8 quests + 4 actos)
│   │   ├── progress.py                   (lectura BD)
│   │   ├── markdown.py                   (render + rewriting de links)
│   │   ├── hints.py                      (gestión de pistas)
│   │   ├── setup_check.py                (builder de contexto)
│   │   ├── milestones.py                 (detección cierre de acto)
│   │   └── trace.py                      (buffer del agent loop en vivo)
│   ├── templates/
│   │   ├── base.html                     (layout arcano, nav, footer)
│   │   ├── profile.html                  (hero + barra XP + stats)
│   │   ├── map.html                      (roadmap de 4 actos)
│   │   ├── ranks.html                    (galería de 8 rangos)
│   │   ├── quest_view.html               (viewer de README)
│   │   ├── codex_view.html               (viewer del Códex)
│   │   ├── setup.html                    (diagnóstico full)
│   │   ├── milestones.html               (actos cerrados)
│   │   ├── celebrate.html                (animación level-up)
│   │   ├── live_agent.html               (grafo del agent loop)
│   │   └── partials/
│   │       ├── setup_panel.html
│   │       ├── hints_panel.html
│   │       └── notifications.html
│   └── static/
│       ├── arcane.css                    (tema completo)
│       ├── dashboard.js                  (polling + copy + mark-read)
│       ├── celebrate.js                  (partículas + animación)
│       ├── live_agent.js                 (grafo del loop)
│       └── fonts/                        (Cinzel + Inter embebidas)
│
└── progress/
    ├── db.py                             (+5 tablas nuevas, +5 columnas, +emit_event)
    ├── notify.py                         ← NUEVO (POST best-effort + open_celebration)
    └── setup_diagnostics.py              ← NUEVO (9 checks compartidos)

quests/quest_NN_*/
└── hints/                                ← NUEVO en cada quest
    ├── 1_susurro.md
    ├── 2_revelacion.md
    └── 3_manifestacion.md

Bitacoras/                                ← NUEVO
├── 2026-05-19-plan-dashboard-arcano.md   (plan canónico)
├── avance.md                             (log vivo de fases)
└── comparativa-v0-vs-v1.md               (este archivo)
```

### Esquema de BD

| Tabla | v0 | v1 |
|---|---|---|
| `apprentice` | id, username, current_rank, xp, level | + `created_at`, + `avatar` |
| `quest_completion` | quest_id, difficulty, completed_at | + `attempts`, + `first_attempt_at`, + `total_time_seconds` |
| `events` | _no existe_ | id, kind, payload, seen, created_at |
| `quest_attempts` | _no existe_ | id, quest_id, attempted_at, passed, failure_reason |
| `hint_usage` | _no existe_ | quest_id, hint_level, requested_at |
| `quest_reading` | _no existe_ | quest_id, read_at |
| `act_milestones` | _no existe_ | act_number, closed_at |

Todas las migraciones son **aditivas e idempotentes** — los aprendices con `.quest_progress.db` poblada de v0 simplemente ganan las nuevas columnas/tablas sin perder datos.

### Stack nuevo

| Dependencia | Propósito |
|---|---|
| `fastapi` | Servidor del dashboard |
| `uvicorn` | ASGI runner |
| `jinja2` | Templates HTML |
| `markdown-it-py` | Render de READMEs y Códex |
| `pygments` | Syntax highlight en code blocks |
| `psutil` | Validar PIDs del proceso detached |
| `httpx` | Cliente del notify.py best-effort |
| `typer` | CLI unificado |
| `rich` | Output coloreado de doctor / progress |

---

## Ganancias concretas para el aprendiz

### Pedagógicas
1. **Setup proactivo**: el aprendiz nunca se atasca 30 minutos por una API key mal puesta — `doctor` lo dice antes.
2. **Pistas opt-in**: cuando se atasca, puede pedir guía sin sentir que está "haciendo trampa" (sistema de 3 niveles con consentimiento).
3. **Pre-check ahorra cuota**: validaciones estáticas le dicen si su código tiene los hitos antes de gastar Gemini.
4. **Tiempo y intentos visibles**: el aprendiz ve su propia evolución (logros "One shot", "Sin red").
5. **Agente loop visible**: en Q07-Q08, el grafo en vivo muestra el ciclo de razonamiento → tool → observación. El concepto central del Acto II se *ve*, no solo se lee.

### Experiencia
6. **Mapa visual del viaje**: en lugar de "estoy en quest 4 de 8", el aprendiz *ve* dónde está, qué le falta y qué rangos quedan por desbloquear.
7. **Celebración al pasar quest**: animación + auto-apertura del browser. Refuerza positivamente la conducta deseada.
8. **Notificaciones cruzadas**: el check en una terminal hace aparecer el evento en el dashboard de otro monitor, sin recargar.
9. **Comandos cortos**: `arkanum check 3` vs `uv run python -m quests.quest_03_apprentice_voice.check`. Reducción de fricción del orden de 5-10x.
10. **Tipografía y estética arcana**: la metáfora narrativa (Zhyréon, Arkanum, rangos, actos) se materializa visualmente, refuerza la inmersión.

### Operativas
11. **`arkanum doctor` antes de pedir ayuda**: cualquier troubleshooting empieza por ahí. Reduce soporte 1-a-1.
12. **Cierre de acto detectado automáticamente**: el sistema sabe cuándo terminaste un acto y deja constancia visible.
13. **Tracking de costo**: el aprendiz ve cuántos tokens ha consumido. Útil para hacer consciencia y para presupuestos.
14. **UTF-8 fix transparente**: bug pre-existente de Windows resuelto.

---

## Lo que **no** se rompió

**Compatibilidad 100%** con la forma vieja de trabajar:

- Los comandos viejos siguen funcionando idénticos:
  - `uv run python -m common.progress.init_user`
  - `uv run python -m common.progress.show_progress`
  - `uv run python -m quests.quest_NN.starter.main`
  - `uv run python -m quests.quest_NN.check`
- Los `check.py` no se tocaron — siguen siendo la **única fuente de verdad** sobre si un quest está completado.
- Los `starter/main.py` no se tocaron — el aprendiz sigue escribiendo el mismo código.
- Los `solution/` no se tocaron — siguen siendo referencia accesible.
- La BD de un aprendiz que ya tenía progreso en v0 migra automáticamente (todas las migraciones son aditivas).
- Si el aprendiz prefiere no ver el dashboard, `ARKANUM_NO_DASHBOARD=1` lo desactiva — sigue usando solo terminal y todo funciona.

**Conclusión:** v1 es un **superset estricto** de v0. Nadie pierde funcionalidad, todos ganan opciones.

---

## Métricas del cambio

| Métrica | Valor |
|---|---|
| Archivos nuevos | ~45 |
| Líneas de código agregadas | ~5,500 (Python) + ~1,200 (CSS) + ~400 (JS) + ~600 (HTML) |
| Tablas nuevas en BD | 5 |
| Columnas nuevas en tablas existentes | 5 |
| Endpoints nuevos | ~15 (HTML + JSON) |
| Páginas del dashboard | 9 |
| Comandos del CLI `arkanum` | 13 |
| Pistas pedagógicas redactadas | 24 (3 × 8 quests) |
| Tiempo de implementación | ~68h en 18 fases |
| Tests/verificaciones manuales | cada fase cierra con criterio "Done cuando…" verificado |
| Branch | `feat/dashboard-arcano` (mergeable a master) |

