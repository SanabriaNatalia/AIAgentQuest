# Bitácora — Plan Dashboard Arcano del Aprendiz

> **Fecha:** 2026-05-19
> **Branch:** `feat/dashboard-arcano`
> **Estado:** Plan aprobado, pendiente implementar Fase 0

---

## 0. Resumen ejecutivo

Sistema **single-user local** compuesto por:

1. Servidor FastAPI siempre activo via lazy auto-start.
2. CLI unificado `arkanum`.
3. Integraciones discretas con los `check.py` existentes (sin tocar su lógica de validación).

El front es **viewer y trofeero**, nunca quest runner. La terminal y el editor siguen siendo el campo de batalla.

**Estimación total:** ~62-67 horas distribuibles en fases independientes y deployables por separado.

---

## 1. Filosofía y reglas inviolables

> Los agentes no son magia. Son sistemas. — Zhyréon

| Regla | Consecuencia |
|---|---|
| El front muestra **información**, no ejecuta acciones del laboratorio | Sin editor inline, sin botón "ejecutar quest", sin botón "validar" |
| El único validador real es `check.py` | El dashboard nunca otorga XP por sí mismo |
| Lectura asistida sí, automatización del aprendizaje no | Viewer de READMEs sí; wizard paso a paso no |
| Las pistas son ofrenda, no atajo | Confirmación explícita; persistencia; afectan logro "Sin red" |
| Estética arcana es atmósfera, no decorativa | Quotes de Zhyréon, paleta, tipografías parte del diseño |

---

## 2. Decisiones tomadas

| Decisión | Valor |
|---|---|
| Stack | FastAPI + Jinja2 + HTMX + CSS arcano |
| Modelo de usuarios | Single-user local |
| Server lifecycle | Siempre activo (lazy auto-start) |
| Celebración | No-bloqueante (best-effort POST) |
| Cierre de acto | Detectado automáticamente, evento + UI (sin PDF en v1) |
| Viewer de READMEs | Sí, con visibilidad por progreso |
| Checklist de setup global | Sí (auto-detectada) |
| Checklist auto-detectada por quest | No (descartada) |
| Sistema de pistas | Siempre solicitables, sin cooldown, con confirmación |
| Actualizar READMEs de quests | Sí, fase dedicada tras CLI básico |
| Modo dev | Sí (`arkanum dashboard start --dev` usa uvicorn --reload) |
| Generación de PDFs | **Diferida a v2** (incluye decisión de banner y firma) |

---

## 3. Stack y dependencias

A agregar en `pyproject.toml`:

```toml
fastapi = "^0.115"
uvicorn = "^0.32"
jinja2 = "^3.1"
markdown-it-py = "^3.0"
pygments = "^2.18"
httpx = "^0.27"
psutil = "^6.0"

[project.scripts]
arkanum = "common.cli:main"
```

**Removido del plan original:** `reportlab`, `weasyprint` (sin PDFs en v1).

---

## 4. Esquema final de la BD

`common/progress/db.py` ejecuta migraciones aditivas idempotentes (con `PRAGMA table_info` para `ADD COLUMN` seguro).

```sql
-- Modificaciones a tablas existentes
ALTER TABLE apprentice ADD COLUMN created_at TEXT;
ALTER TABLE apprentice ADD COLUMN avatar TEXT DEFAULT 'default';

ALTER TABLE quest_completion ADD COLUMN attempts INTEGER DEFAULT 1;
ALTER TABLE quest_completion ADD COLUMN first_attempt_at TEXT;
ALTER TABLE quest_completion ADD COLUMN total_time_seconds INTEGER;

-- Tablas nuevas
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    payload TEXT NOT NULL,
    seen INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quest_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quest_id TEXT NOT NULL,
    attempted_at TEXT NOT NULL,
    passed INTEGER NOT NULL,
    failure_reason TEXT
);

CREATE TABLE IF NOT EXISTS hint_usage (
    quest_id TEXT NOT NULL,
    hint_level INTEGER NOT NULL,
    requested_at TEXT NOT NULL,
    PRIMARY KEY (quest_id, hint_level)
);

CREATE TABLE IF NOT EXISTS quest_reading (
    quest_id TEXT PRIMARY KEY,
    read_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS act_milestones (
    act_number INTEGER PRIMARY KEY,
    closed_at TEXT NOT NULL
);
```

**Removida del plan original:** tabla `certificates` (sin PDFs).
**Agregada:** tabla `act_milestones` para detección de cierre de acto.

---

## 5. Estructura completa de archivos nuevos

```
common/
├── cli/
│   ├── __init__.py
│   ├── main.py
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── run.py
│   │   ├── check.py
│   │   ├── current.py
│   │   ├── next.py
│   │   ├── progress.py
│   │   ├── doctor.py
│   │   ├── cost.py
│   │   ├── dashboard.py
│   │   └── precheck.py
│   └── helpers.py
├── dashboard/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py
│   ├── lifecycle.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── pages.py
│   │   ├── events.py
│   │   ├── hints.py
│   │   ├── api.py
│   │   └── health.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── quest_catalog.py
│   │   ├── progress.py
│   │   ├── markdown.py
│   │   ├── hints.py
│   │   ├── setup_check.py
│   │   ├── milestones.py
│   │   └── trace.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── partials/
│   │   │   ├── nav.html
│   │   │   ├── setup_panel.html
│   │   │   ├── notifications.html
│   │   │   └── hints_panel.html
│   │   ├── profile.html
│   │   ├── map.html
│   │   ├── ranks.html
│   │   ├── quest_view.html
│   │   ├── codex_view.html
│   │   ├── milestones.html
│   │   ├── celebrate.html
│   │   └── live_agent.html
│   └── static/
│       ├── arcane.css
│       ├── celebrate.js
│       ├── live_agent.js
│       ├── htmx.min.js
│       └── fonts/
├── progress/
│   ├── db.py
│   ├── notify.py
│   ├── setup_diagnostics.py
│   └── ...

quests/
├── quest_01_first_invocation/
│   └── hints/
│       ├── 1_susurro.md
│       ├── 2_revelacion.md
│       └── 3_manifestacion.md
└── ... (igual para los 8 quests)

.quest_progress.pid
.quest_dashboard.log
.quest_dashboard.port
.setup_cache.json
.last_celebrate.timestamp
.quest_calls.log
```

**Todos los archivos sin extensión arriba van al `.gitignore`.**

---

## 6. Componentes principales

### 6.1 Lifecycle del server (lazy auto-start)

`common/dashboard/lifecycle.py`:

```python
def ensure_started() -> None
def start(detached: bool = True, dev: bool = False) -> int
def stop() -> bool
def status() -> dict
def is_running() -> bool
```

**`ensure_started()`** — idempotente, ~5ms:
1. Lee `.quest_progress.pid`.
2. Valida con `psutil.pid_exists()` + nombre de proceso.
3. Si vive, return.
4. Si no, spawn detached, persiste pid + puerto.
5. Opt-out: `ARKANUM_NO_DASHBOARD=1`.

**Modo dev**: `start(dev=True)` usa `uvicorn --reload` y NO se detacha (corre en foreground). Solo para desarrollo del dashboard mismo.

**Puerto**: default 8765 con fallback automático a 8766-8768. Persistido en `.quest_dashboard.port`.

**Spawning detached**:
- Windows: `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`
- Unix: `start_new_session=True`

**Llamadores de `ensure_started()`**: `record_quest_completion`, `show_progress.main`, comandos del CLI (excepto `dashboard stop`).

### 6.2 CLI unificado `arkanum`

| Comando | Función |
|---|---|
| `arkanum start <N>` | Ejecuta `quests/quest_NN_*/starter/main.py` |
| `arkanum run <N> "prompt"` | Wrapper con tracing para Q07-Q08 |
| `arkanum check <N>` | Ejecuta `quests/quest_NN_*/check.py` |
| `arkanum check <N> --dry-run` | Solo pre-checks locales, sin llamar Gemini |
| `arkanum current` | Quest actual + comando para empezar |
| `arkanum next` | Próximo quest |
| `arkanum progress` | Equivale a `show_progress` |
| `arkanum doctor` | Diagnóstico completo |
| `arkanum cost` | Tokens consumidos |
| `arkanum dashboard [start|stop|status|open|logs]` | Control del server |
| `arkanum dashboard start --dev` | Modo desarrollo con --reload |

**Compatibilidad:** `uv run python -m quests.quest_XX.starter.main` sigue funcionando.

### 6.3 Doctor / Setup global

`common/progress/setup_diagnostics.py` expone:

```python
@dataclass
class SetupCheck:
    id: str
    label: str
    status: Literal["ok", "warn", "fail"]
    detail: str | None

def run_setup_diagnostics(skip_api_ping: bool = False) -> list[SetupCheck]
```

**Checks:**
1. Python ≥3.12
2. `uv` disponible
3. Dependencias críticas
4. `.env` existe
5. `GEMINI_API_KEY` presente
6. API key validada (ping cacheado 24h)
7. `.quest_progress.db` inicializada
8. Dashboard activo
9. `workspace/` sin cambios sospechosos

**Consumido por:** `arkanum doctor`, panel del perfil, página `/setup`, wizard de `init_user`. Auto-refresh cada 30s en el dashboard.

### 6.4 Pre-check local

Validaciones estáticas (regex + AST simple) por quest. Ejemplo Q03:

- Existe `starter/main.py`
- Importa `argparse`
- Llama `ArgumentParser()`
- Imprime "Prompt tokens:"
- Usa `types.Content`

`arkanum check N` corre pre-check primero; si falla, pregunta confirmación antes de gastar cuota Gemini. `--dry-run` solo corre pre-check.

### 6.5 Sistema de pistas

**Estructura:**

```
quests/quest_XX_*/hints/
├── 1_susurro.md       # pregunta orientadora
├── 2_revelacion.md    # nombre / concepto
└── 3_manifestacion.md # snippet 2-4 líneas
```

**Reglas:**
- Orden estricto (II requiere I, III requiere II).
- Una vez pedida, persiste.
- Sin penalización XP; solo afecta logro *"Sin red"* por quest.
- Confirmación explícita en cada solicitud.

**Servicio** `common/dashboard/services/hints.py`:

```python
def list_hints_for(quest_id: str) -> list[HintMeta]
def get_hint(quest_id: str, level: int) -> str
def request_hint(quest_id: str, level: int) -> bool
def used_hints(quest_id: str) -> set[int]
def is_no_red_eligible(quest_id: str) -> bool
```

**UI:** panel al final de `/quest/{id}` con 3 cartas y modal de confirmación.

### 6.6 Tracking de tiempo e intentos

- `first_attempt_at`: capturado en primer `arkanum start`/`check` de un quest.
- `attempts`: contado desde `quest_attempts` (cada check, exitoso o fallido).
- `total_time_seconds`: `completed_at - first_attempt_at`.

**Logros calculados on-the-fly** (sin tabla `achievements` en v1):
- *"One shot"*: `attempts == 1`.
- *"Sin red"*: sin entradas en `hint_usage` para ese quest.

### 6.7 Visualización del agent loop (Q07-Q08)

⚠️ **Wrapper opcional, no instrumentación forzada.**

```bash
arkanum run 7 "prompt"
```

`arkanum run`:
1. Setea `ARKANUM_TRACE=1` y `ARKANUM_TRACE_URL`.
2. Spawn del starter como subprocess.
3. Parsea stdout línea-por-línea (`"- Calling function: X"`, `"-> {'result': ...}"`).
4. Emite eventos POST `/events/trace` al dashboard.
5. Página `/live-agent` se refresca via HTMX polling cada 1s.

**No requiere modificar starters ni `call_function.py`.** Solo parsing externo.

### 6.8 Detección de cierre de acto (sin PDF)

Tras cada `record_quest_completion`:
1. Verificar si las quests del acto correspondiente están todas en `quest_completion`.
2. Si sí y no existe en `act_milestones`, insertar.
3. Emitir evento `act_closed`.

**UI** en página `/milestones` (reemplaza a `/certificates` del plan original):
- Lista de actos cerrados con fecha + lista de rangos obtenidos en ese acto.
- Quote de Zhyréon de cierre.
- Marcador especial en `/map` (banner luminoso sobre la columna del acto cerrado).

A futuro (v2): generar PDF descargable.

### 6.9 Notificaciones best-effort

`common/progress/notify.py`:

```python
def emit_event(kind: str, payload: dict) -> None
def open_celebration(quest_id: str) -> None
```

- `httpx.post(..., timeout=0.3)` con try/except absoluto.
- Si server no responde, evento se persiste directamente en `events` (sin HTTP).
- `webbrowser.open()` con throttle de 5s (`.last_celebrate.timestamp`).

---

## 7. Endpoints + páginas

### Páginas HTML

| Ruta | Template | Descripción |
|---|---|---|
| `/` | profile.html | Aprendiz, nivel, XP, panel setup, notificaciones |
| `/setup` | (full) | Diagnóstico completo |
| `/map` | map.html | Roadmap de 4 actos |
| `/ranks` | ranks.html | Galería de 8 rangos |
| `/quest/{id}` | quest_view.html | README + panel pistas |
| `/codex/{path:path}` | codex_view.html | Renderer de docs/ |
| `/milestones` | milestones.html | Actos cerrados |
| `/celebrate` | celebrate.html | Animación level-up |
| `/live-agent` | live_agent.html | Grafo en vivo Q07-Q08 |

### Endpoints API

| Ruta | Método | Función |
|---|---|---|
| `/health` | GET | Ping |
| `/events/quest-completed` | POST | Recibe de notify.py |
| `/events/trace` | POST | Recibe de arkanum run |
| `/events/check-failed` | POST | Sugerir pistas |
| `/api/events/recent` | GET | HTMX polling |
| `/api/setup/status` | GET | HTMX |
| `/api/quests/{id}/hints` | GET | Estado |
| `/api/quests/{id}/hints/{level}` | POST | Solicita pista |
| `/api/quests/{id}/mark-read` | POST | Marcar README leído |
| `/api/trace/current` | GET | HTMX polling agent loop |

### Estáticos

| Ruta | Sirve |
|---|---|
| `/static/*` | CSS/JS |
| `/assets/images/{name}` | Banners del repo |

---

## 8. Puntos de integración con el código existente

| Archivo | Cambio |
|---|---|
| `pyproject.toml` | +deps, +entry point `arkanum` |
| `common/progress/db.py` | Migraciones + `emit_event` + detección cierre acto |
| `common/progress/init_user.py` | Wizard (nombre, API key ping, dashboard start, browser) |
| `common/progress/show_progress.py` | `ensure_started()` al inicio |
| `.gitignore` | +archivos runtime |

**No tocamos:**
- Ningún `quests/*/check.py`
- Ningún `quests/*/starter/main.py`
- Ningún `quests/*/solution/`
- `common/functions/*.py`
- `common/prompts/system_prompt.py`
- `common/config.py`

Toda la integración pasa por `record_quest_completion`.

---

## 9. Diseño visual

Paleta:

```css
:root {
  --arkanum-bg: #0d0a1f;
  --arkanum-bg-soft: #1a1535;
  --arkanum-gold: #c9a961;
  --arkanum-purple: #8b5cf6;
  --arkanum-glow: #c084fc;
  --arkanum-text: #e8e3f0;
  --arkanum-muted: #8a82a8;
  --arkanum-locked: #3d3856;
  --arkanum-success: #65d196;
  --arkanum-warn: #e8b94d;
  --arkanum-fail: #e87a7a;
}
```

Tipografías: Cinzel/Cormorant (títulos), Inter (contenido). Embebidas en `/static/fonts/`.

---

## 10. Roadmap por fases

Cada fase es deployable y testeable independientemente.

| # | Fase | Horas |
|---|---|---|
| 0 | Andamiaje (deps, estructura, migraciones, gitignore) | 2h |
| 1 | Server + lifecycle (+modo dev) | 4h |
| 2 | Catálogo + página de perfil | 4h |
| 3 | Mapa + galería de rangos | 4h |
| 4 | Setup global + doctor | 5h |
| 5 | Viewer de READMEs y Códex | 5h |
| 6 | Integración CLI + notificaciones | 3h |
| 7 | Página de celebración | 3h |
| 8 | Wizard init_user + CLI básico (current/next/progress/start/check) | 4h |
| 9 | Actualizar READMEs de quests (mencionar comandos `arkanum`) | 2h |
| 10 | Pre-check local | 4h |
| 11 | Sistema de pistas (mecánica + endpoints + UI) | 5h |
| 12 | Contenido de pistas (24 archivos `.md`) ⚠️ pedagógico | 5h |
| 13 | Tracking tiempo/intentos + logros calculados | 4h |
| 14 | Tracking de costo (`arkanum cost`) | 2h |
| 15 | Detección de cierre de acto + página /milestones | 2h |
| 16 | Visualización del agent loop (`arkanum run`) | 6h |
| 17 | Pulido (empty states, accesibilidad, E2E manual) | 4h |

**Total: ~68 horas.**

**MVP estricto** (Fases 0-7): ~30h.
**MVP + CLI + READMEs** (Fases 0-9): ~34h.

---

## 11. Huecos detectados ⚠️

### Crítico

1. **Contenido de las 24 pistas** debe redactarse manualmente (Fase 12). Es trabajo pedagógico, no de código.
2. **Wrapper `arkanum run`** es opt-in. Los aprendices que sigan usando `uv run python -m ...` no verán el agent loop en el dashboard. Mitigación: documentar prominentemente en READMEs de Q07-Q08 (cubierto por Fase 9).

### Medio

3. **Subprocess detached en Windows** puede dejar PIDs zombi. Mitigación: validación con `psutil` + nombre de proceso.
4. **Carrera condicional** entre `notify` y server arrancando. Mitigación: persistencia directa en `events` sin depender del HTTP.
5. **`webbrowser.open()` múltiples pestañas** si pasas quests seguidos. Mitigación: throttle 5s.
6. **Auto-start agresivo** en CI/tests. Mitigación: `ARKANUM_NO_DASHBOARD=1`.

### Bajo

7. **Migración de BD existente**: las `ADD COLUMN`/`CREATE TABLE IF NOT EXISTS` son seguras.
8. **Sin eventos retroactivos** para quests ya completados antes de instalar dashboard. Sin impacto funcional.
9. **PID file stale**: validar con psutil siempre.
10. **CSRF**: server escucha en `127.0.0.1`. Suficiente para v1.

---

## 12. Diferido a v2

- Generación de certificados PDF (con decisiones de banner/firma).
- Reto/Boss del Acto.
- Grimorio personal (lista de conceptos desbloqueados).
- Glosario contextual con tooltips.
- Quiz/flashcards post-acto.
- Modo "review" diff con solución oficial post-quest.
- Multi-aprendiz.
- Audio narration TTS de Zhyréon.
- VSCode extension.
- Logros adicionales más allá de "One shot" y "Sin red".

---

## 13. Siguiente paso

Implementar **Fase 0 — Andamiaje**:

1. Editar `pyproject.toml` con nuevas deps + entry point.
2. `uv sync`.
3. Crear estructura de carpetas vacía (con `__init__.py` donde corresponda).
4. Implementar migraciones aditivas en `db.py` (sin tocar lógica existente).
5. Actualizar `.gitignore`.
6. Verificar que `uv run python -m common.progress.show_progress` sigue funcionando.
7. Commit.

**Done cuando:** la suite existente sigue pasando y la nueva estructura está lista para Fase 1.
