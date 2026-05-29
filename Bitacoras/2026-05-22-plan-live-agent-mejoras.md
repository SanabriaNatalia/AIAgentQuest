# Bitácora — Plan de mejoras de la vista Live Agent

> **Fecha:** 2026-05-22
> **Branch sugerido:** `feat/live-agent-v2`
> **Estado:** Plan preliminar. Cada mejora es independiente y desplegable por separado.
> **Plan v1 (origen del Live Agent):** [`2026-05-19-plan-dashboard-arcano.md`](2026-05-19-plan-dashboard-arcano.md)
> **Plan v2 del laboratorio:** [`2026-05-20-plan-v2-arkanum.md`](2026-05-20-plan-v2-arkanum.md)

---

## 0. Resumen ejecutivo

La vista `/live-agent` cumple su objetivo mínimo —ver pasos del agent loop en vivo durante Q07–Q08— pero opera con tres limitaciones estructurales:

1. **Parser frágil:** los steps se extraen con regex sobre el `stdout` del starter (`common/cli/commands/run.py`). Cualquier cambio en los `print` del alumno rompe el tracing sin error visible.
2. **Visualización plana:** lista vertical de eventos sin agrupamiento. El alumno ve "logs bonitos", no la **unidad lógica** del loop (acción → observación → iteración).
3. **Sin historia:** solo se muestra el trace más reciente. Las ejecuciones pasadas existen en la tabla `agent_traces` pero no son navegables desde la UI.

Este plan agrupa **8 mejoras** que atacan estas limitaciones por capas, sin reescribir la arquitectura. La tabla `agent_traces` no cambia de shape; todo el trabajo es aditivo (nuevos `step_type`, nuevos endpoints opt-in, frontend).

**Estimación total:** ~22–28 horas distribuibles en 8 features.
**Cobertura:** Q06–Q08 hoy; Q03–Q04 si se aprueba la mejora #1.

---

## 1. Estado actual (lo que hay hoy)

| Pieza | Archivo | Responsabilidad |
|---|---|---|
| Wrapper CLI | `common/cli/commands/run.py` | Lanza starter como subprocess, parsea stdout con regex, emite steps. |
| Persistencia | `common/dashboard/services/trace.py` + tabla `agent_traces` (`common/progress/db.py:113`) | `record_step`, `recent_steps`, `latest_trace_summary`. |
| Endpoint HTTP | `common/dashboard/routes/events.py:82` (`POST /events/trace`) | Recibe step y delega a `record_step`. |
| Endpoint JSON | `common/dashboard/routes/api.py:155` (`GET /api/trace/current`) | Resumen + lista de pasos del trace más reciente. |
| Página | `common/dashboard/templates/live_agent.html` + `static/dashboard.js:382` (`initLiveAgent`) | Polling cada 1 s, render de lista plana. |

**Tipos de step actualmente reconocidos:**
`session_start`, `function_call`, `function_result`, `tokens`, `session_end`.

**Variables de entorno ya inyectadas al subprocess** (sin lector):
`ARKANUM_TRACE_ID`, `ARKANUM_TRACE=1`.

---

## 2. Filosofía de las mejoras

| Regla | Consecuencia |
|---|---|
| Compatible con el regex actual | Cualquier emisor estructurado nuevo convive con el parser de stdout como fallback. |
| La tabla `agent_traces` no muta su shape | Nuevos step types son strings; metadata estructurada va serializada en `payload`. |
| Cada mejora deploys sola | No hay dependencias duras; el orden recomendado es de impacto, no técnico. |
| El dashboard sigue sin ejecutar checks | La mejora #7 *lanza* el wrapper pero no valida; sigue siendo `check.py`. |
| Las quests no tienen que cambiar para que las mejoras funcionen | Si el alumno modifica un starter, el regex sigue actuando como fallback. |

---

## 3. Decisiones pendientes

| Mejora | Decisión clave |
|---|---|
| #1 Emisor estructurado | Módulo opt-in importable vs hook en `common/functions/call_function`. |
| #2 Agrupar call↔result | Tarjeta colapsable vs vista timeline. |
| #3 Bandas por iteración | Emisión explícita desde starter vs heurística por pareja consumida. |
| #4 Historial de traces | Sidebar permanente vs página dedicada `/traces`. |
| #5 Stale detection | Timeout fijo (30 s) vs configurable. |
| #6 Costo por iteración | Reutilizar `services/cost.py` o re-calcular. |
| #7 Lanzar desde dashboard | Endpoint que ejecuta subprocess vs solo copiar comando al portapapeles. |
| #8 Polling adaptativo | Detectar actividad por `last_step_at` vs por hash de respuesta. |

---

## 4. Las 8 mejoras

### Mejora #1 — Emisor de trace estructurado (`common/tracing.py`)

**Problema que resuelve:** el parser regex de `run.py:64` se rompe en silencio si el alumno reformatea `print(f"Calling function: ...")`. Hoy `ARKANUM_TRACE_ID` se inyecta al subprocess pero nadie lo lee.

**Alcance:**
- Crear `common/tracing.py` con API mínima:
  ```python
  def emit(step_type: str, name: str | None = None, payload: Any = None) -> None: ...
  def trace_enabled() -> bool: ...  # lee ARKANUM_TRACE
  ```
- `emit` hace POST best-effort a `http://127.0.0.1:8765/events/trace` con `ARKANUM_TRACE_ID`. Si falla, no levanta excepción.
- Refactor opcional en `common/functions/call_function.py` para emitir `function_call` y `function_result` automáticamente cuando `trace_enabled()` es True, sin tocar los starters.
- El regex de `run.py` sigue activo como fallback para starters viejos o que el alumno modifique.

**Archivos a tocar:**
- Crear `common/tracing.py`.
- Modificar `common/functions/call_function.py` (envolver con `emit` condicional).
- Documentar uso opcional en `docs/agents/error_handling.md` o nuevo `docs/agents/tracing.md`.

**Esfuerzo:** ~3 h.
**Riesgo:** bajo. Si el POST falla, swallow silencioso. El path de regex queda intacto.
**Criterio de éxito:** correr Q07 sin el `print` original sigue poblando `/live-agent`.

---

### Mejora #2 — Agrupar visualmente `function_call ↔ function_result`

**Problema que resuelve:** hoy la lista es plana. El alumno no ve la unidad "intento + observación" como una sola cosa; tiene que mirar dos cards seguidas y mentalmente emparejarlas.

**Alcance:**
- En `dashboard.js:initLiveAgent`, agrupar cada `function_call` con el siguiente `function_result` cuyo `name` coincida (o el inmediato si no hay name match).
- Render como tarjeta colapsable única: header con nombre de función + duración (delta entre `created_at`), body con args (call) y respuesta (result) lado a lado o tabs.
- Si un `function_call` no tiene `function_result` emparejado todavía, mostrarlo con spinner ("ejecutando…").
- CSS nuevo en `static/arcane.css` para la tarjeta agrupada.

**Archivos a tocar:**
- `common/dashboard/static/dashboard.js` (función `applyData` + nuevo `renderPair`).
- `common/dashboard/static/arcane.css`.

**Esfuerzo:** ~3 h.
**Riesgo:** medio. Empareja por orden de llegada; si el agente lanza dos calls al mismo nombre en paralelo (poco común en Gemini single-turn), podría desordenar. Mitigación: emparejar también por payload args como tie-breaker.
**Criterio de éxito:** una iteración de Q08 muestra N tarjetas (N = número de tools llamadas en esa iteración), no 2N filas.

---

### Mejora #3 — Bandas por iteración del loop (específico de Q08)

**Problema que resuelve:** Q08 es la quest donde "el loop" es el concepto pedagógico central. Hoy las iteraciones son indistinguibles entre sí; el alumno no *ve* el ciclo, solo lo intuye.

**Alcance:**
- Nuevo `step_type=iteration_start` con `payload={"iter": 1, "max": MAX_ITERS}`.
- Opción A (preferida): emitir desde el starter con `tracing.emit("iteration_start", payload={"iter": i, "max": MAX_ITERS})` al inicio de cada vuelta del `for`.
- Opción B (fallback): heurística en frontend — cada vez que aparece un `function_call` después de un `function_result` que cerró todas las parejas abiertas, abrir una banda nueva.
- UI: separadores horizontales con label "Iteración N / MAX_ITERS" y contador de tarjetas agrupadas dentro.

**Archivos a tocar:**
- `quests/quest_08_manifesting_cycle/starter/main.py` (opcional, si va opción A).
- `common/dashboard/static/dashboard.js` (lógica de banding).
- `common/dashboard/static/arcane.css` (estilo de separador).

**Esfuerzo:** ~2 h opción A; ~4 h opción B.
**Riesgo:** bajo. Banding visual; si la heurística B se equivoca, el alumno sigue viendo los pasos.
**Criterio de éxito:** Q08 con 3 iteraciones se ve como 3 bandas, no como 9 cards mezcladas.

---

### Mejora #4 — Historial de traces (sidebar o página `/traces`)

**Problema que resuelve:** hoy solo se muestra el trace más reciente. Si el alumno corre dos veces seguidas el mismo prompt para comparar comportamientos, pierde la ejecución anterior. La data sí está en `agent_traces`.

**Alcance:**
- Nuevo endpoint `GET /api/traces/recent?limit=10` que devuelve resúmenes (no steps) de los últimos N traces: `trace_id`, `quest_slug`, `started_at`, `last_step_at`, `steps`, primer prompt si está disponible en `session_start.payload`.
- Sidebar en `/live-agent` con las últimas 10 ejecuciones. Click sobre una cambia el trace activo (parámetro `?trace_id=` en `/api/trace/current`, ya soportado).
- Highlight visual del trace en vivo (último, con polling activo) vs traces históricos (snapshot, sin polling).

**Archivos a tocar:**
- `common/dashboard/services/trace.py` (nueva función `recent_trace_summaries`).
- `common/dashboard/routes/api.py` (nuevo endpoint).
- `common/dashboard/templates/live_agent.html` (sidebar).
- `common/dashboard/static/dashboard.js` (soporte de cambio de trace + polling solo si es el último).

**Esfuerzo:** ~4 h.
**Riesgo:** bajo. Solo lecturas adicionales contra una tabla ya existente.
**Criterio de éxito:** dos `arkanum run 8 "..."` consecutivos quedan ambos accesibles en la UI.

---

### Mejora #5 — Detección de traces "stale"

**Problema que resuelve:** si el starter se cuelga (timeout de Gemini, bug del alumno), nunca llega `session_end`. La UI queda en "Esperando trace…" indefinidamente.

**Alcance:**
- En `latest_trace_summary` añadir cálculo de `seconds_since_last_step`.
- En frontend (`applyData`): si `seconds_since_last_step > 30` y no hay `session_end`, marcar el trace como `stale` con badge y un hint "el agente parece haberse colgado, revisa la terminal".
- No matar el subprocess automáticamente; es informativo.

**Archivos a tocar:**
- `common/dashboard/services/trace.py` (campo nuevo en `TraceSummary`).
- `common/dashboard/routes/api.py` (incluir el cálculo en la respuesta).
- `common/dashboard/static/dashboard.js` (render del badge).

**Esfuerzo:** ~1.5 h.
**Riesgo:** mínimo. Solo UI; no afecta a `record_step`.
**Criterio de éxito:** matar un starter con Ctrl+C en mitad del loop deja la UI con un badge "stale" en lugar de "esperando".

---

### Mejora #6 — Costo por iteración

**Problema que resuelve:** los steps `tokens` (prompt/response) están en la tabla pero no se traducen a USD ni se acumulan por iteración. `common/dashboard/services/cost.py` ya existe.

**Alcance:**
- Sumar tokens por banda de iteración (depende de mejora #3 para tener bandas; sin ella, sumar al final del trace).
- Cada banda muestra "≈ X tokens · ≈ Y USD" en su header.
- En el resumen del trace: total acumulado.
- Reutilizar la tabla de pricing de `services/cost.py`.

**Archivos a tocar:**
- `common/dashboard/services/trace.py` (helper `trace_cost(trace_id)`).
- `common/dashboard/static/dashboard.js` (render).
- Posiblemente `services/cost.py` si hay que exponer una función puntual para un set de tokens.

**Esfuerzo:** ~2.5 h.
**Riesgo:** bajo. Cálculo derivado, sin escritura nueva.
**Dependencia blanda:** mejora #3 (sin bandas, el costo se ve solo en el total).
**Criterio de éxito:** Q08 completa muestra "≈ 12.4k tokens · ≈ 0.02 USD" en el resumen.

---

### Mejora #7 — Lanzar trace desde el propio dashboard

**Problema que resuelve:** hoy el alumno tiene que cambiar a la terminal para cada `arkanum run`. La UI muestra el resultado pero no es punto de entrada.

**Alcance:**
- Input de texto en `/live-agent` + botón "▶ Ejecutar prompt".
- Nuevo endpoint `POST /api/trace/run` con body `{quest_order: int, prompt: str}`.
- El endpoint lanza el subprocess de `arkanum run N "..."` en background (no bloquea la respuesta HTTP).
- Devuelve `{trace_id, status: "started"}` inmediatamente; el polling normal hace el resto.
- Pre-condiciones: el quest debe estar en estado `current` o ya `completed`. Si está bloqueado, 400.

**Archivos a tocar:**
- `common/dashboard/routes/api.py` (nuevo endpoint).
- `common/dashboard/templates/live_agent.html` (form).
- `common/dashboard/static/dashboard.js` (submit + UX).
- Posiblemente `common/cli/helpers.py` para reusar la lógica de spawn de subprocess sin pasar por typer.

**Esfuerzo:** ~4 h.
**Riesgo:** medio. Spawnear procesos desde un endpoint web requiere cuidado: timeout, no bloquear el event loop, sandbox al `cwd` del proyecto. Aceptable porque es single-user local (filosofía v1).
**Criterio de éxito:** desde `/live-agent` se puede correr un prompt y verlo aparecer sin abrir terminal.

---

### Mejora #8 — Polling adaptativo

**Problema que resuelve:** intervalo fijo de 1 s. Si el modelo tarda 8 s, son 8 fetches vacíos. Si llegan 3 steps en 200 ms, se renderizan con 1 s de delay.

**Alcance:**
- Mantener el intervalo en 1 s por defecto.
- Si el último `applyData` añadió steps nuevos, bajar el siguiente intervalo a 250 ms.
- Tras 5 polls consecutivos sin steps nuevos, subir a 3 s.
- Si el trace tiene `session_end`, parar el polling.

**Archivos a tocar:**
- `common/dashboard/static/dashboard.js` (refactor de `setInterval` a `setTimeout` recursivo con intervalo dinámico).

**Esfuerzo:** ~1.5 h.
**Riesgo:** bajo. Solo afecta cadencia de UI.
**Criterio de éxito:** durante Q08 activa, steps aparecen en <300 ms; en idle no hay fetches a `/api/trace/current` después del `session_end`.

---

## 5. Plan de implementación recomendado

Orden propuesto por **valor pedagógico × costo**:

| Fase | Mejora | Esfuerzo | Justificación del orden |
|---|---|---|---|
| 1 | #2 Agrupar call↔result | 3 h | Mayor cambio visible con menor esfuerzo. Convierte la lista plana en una unidad lógica. |
| 2 | #4 Historial de traces | 4 h | Habilita el comportamiento "comparar dos ejecuciones" que es el segundo gran valor de la vista. |
| 3 | #3 Bandas por iteración | 2 h | Cierra el círculo conceptual de Q08 (el loop). Mejor después de #2 porque las bandas agrupan tarjetas, no filas. |
| 4 | #5 Stale detection | 1.5 h | Cierra un bug real con costo mínimo. |
| 5 | #6 Costo por iteración | 2.5 h | Aprovecha #3. Conecta agentes con la dimensión económica. |
| 6 | #1 Emisor estructurado | 3 h | Mejora estructural; el regex funciona ya. Aporta robustez y prepara terreno para más step types. |
| 7 | #8 Polling adaptativo | 1.5 h | Pulido. Solo se nota en uso prolongado. |
| 8 | #7 Lanzar desde dashboard | 4 h | Mayor cambio de UX pero introduce spawn de subprocess; va al final porque cambia el contrato (dashboard ahora ejecuta). |

**Subtotal:** ~21.5 h de trabajo neto + ~3–5 h de smoke testing distribuido = ~25–27 h.

Cada fase deploya sola. Si solo se hicieran las primeras 4, el Live Agent ya quedaría notablemente mejor.

---

## 6. Criterios de éxito globales

Una vez completadas las 8 mejoras, el Live Agent debe:

1. **Aguantar refactor del alumno:** modificar los `print` de Q07/Q08 no deja la vista vacía (gracias a #1).
2. **Comunicar el loop visualmente:** en Q08 se distinguen iteraciones a primera vista (gracias a #3).
3. **Permitir comparación entre ejecuciones:** dos prompts seguidos coexisten en la UI (gracias a #4).
4. **Recuperarse de cuelgues:** un starter colgado se identifica como tal en <30 s (gracias a #5).
5. **Mostrar dimensión económica:** cada trace lleva su costo estimado (gracias a #6).
6. **Ser punto de entrada, no solo viewer:** se puede lanzar un prompt sin tocar la terminal (gracias a #7).
7. **Sentirse en vivo:** los steps aparecen en <300 ms cuando hay actividad (gracias a #8).
8. **No romper smokes existentes:** el smoke de F17 (30 checks) sigue verde.

---

## 7. No-objetivos explícitos

Lo que **no** entra en este plan, para evitar scope creep:

- **No** soporte multi-aprendiz para traces (sigue siendo single-user local).
- **No** export a herramientas externas (LangSmith, Weights & Biases). Si se quiere, va en otro plan.
- **No** SSE ni WebSockets: el polling con #8 es suficiente para uso local.
- **No** tracing de Q01–Q05 (no tienen tools que tracear). Si se quiere mostrar `prompt`/`response`/`tokens` ahí, requiere su propio diseño y va aparte.
- **No** modificar `common/progress/db.py` shape de `agent_traces`. Todo dato nuevo va en `payload` serializado.
- **No** instrumentación profunda del SDK de Gemini (interceptores, hooks de cliente). El emisor de #1 es manual y opt-in.

---

## 8. Cobertura por quest después del plan

| Quest | Cobertura hoy | Cobertura tras el plan |
|---|---|---|
| Q01–Q05 | Ninguna | Ninguna (no-objetivo). |
| Q06 Tool Chest | Solo `function_call` | Igual + agrupado y con historial. |
| Q07 Agent Incarnation | Pareja única | Pareja agrupada como tarjeta, con costo y historial. |
| Q08 Manifesting Cycle | Lista plana de N pasos | **Bandas por iteración**, parejas agrupadas, costo por iteración, historial comparable, recuperación de stale. |

---

## 9. Notas de implementación

- El branch `feat/dashboard-arcano` (actual) tiene cambios sin commitear en `common/cli/helpers.py` y `quests/quest_01_first_invocation/starter/main.py`. Conviene cerrarlos antes de abrir `feat/live-agent-v2`.
- La regla de commits es **sin coautor** (ver `MEMORY.md`).
- Cada mejora debe llevar su smoke local mínimo (cargar `/live-agent` + correr un `arkanum run 8 "..."` y verificar render).
- Si la mejora #1 se implementa, conviene crear una entrada nueva en `docs/agents/` explicando el módulo `common/tracing.py` y su API.

---

## 10. Adenda 2026-05-29 — Mejoras adicionales (post-v2)

Tras revisar el estado real del visualizador y la solución de Q08, se identifica que la mejora más estructural ausente del plan original es **hacer visible el "pensamiento" del agente** (el `Part.text` que el modelo genera entre tool calls y que hoy se descarta). De ahí salen 10 mejoras adicionales (#9–#18), agrupadas por objetivo:

- **Hacer visible lo invisible** (#9, #10, #11, #17): pensamiento del agente, prompts, contexto, diffs.
- **Cinematografía y telemetría** (#12, #13, #15): latencia, HUD, modo explicador.
- **Reproducción y compartir** (#14, #16): replay y export.
- **Experimentación** (#18): edición del system prompt.

### Mejora #9 — Pensamiento del agente (`agent_thought`)

**Problema que resuelve:** en Q08, cuando hay tool calls, el modelo a menudo genera también `Part.text` (su razonamiento intermedio: *"voy a leer notes.txt para entender qué pide el usuario"*). Hoy ese texto se descarta — `messages.append(candidate.content)` lo guarda en el historial pero nadie lo imprime ni lo trazea. El aprendiz ve la cadena `function_call → function_result → function_call → ...` pero no entiende *por qué* el modelo eligió esa cadena.

**Alcance:**
- Nuevo `step_type=agent_thought` con `payload={"text": ...}`.
- Emitido desde la solución de Q08 vía `common/tracing.emit("agent_thought", payload=text)` dentro del loop por cada `candidate.content.parts[i].text` no vacío que coexista con function calls.
- También capturable desde el wrapper para starters que no usen el emisor, agregando una regex de fallback para líneas que empiecen por `[think] ...` (si el aprendiz decide imprimir su razonamiento).
- UI: tarjeta con icono 🧠, fondo distinto al de tool calls, texto envuelto con tipografía de prosa (no monoespaciada) para enfatizar que es lenguaje natural, no código.
- Si la respuesta final también lleva texto (caso sin function calls), emitir `agent_final` para distinguirlo visualmente.

**Archivos a tocar:**
- Crear `common/tracing.py` (mínimo viable, subset de #1).
- Modificar `quests/quest_08_manifesting_cycle/solution/solution.py` (introspección de `candidate.content.parts`).
- `common/dashboard/static/dashboard.js` (`iconFor`, `renderStep` con clase `--agent_thought`).
- `common/dashboard/static/arcane.css` (nuevo estilo `.trace-step--agent_thought`).

**Esfuerzo:** ~2 h.
**Riesgo:** bajo. Si `tracing.emit` falla, el aprendiz sigue viendo todo lo demás.
**Criterio de éxito:** correr `arkanum run 8 "Lee notes.txt y dime qué contiene"` muestra al menos una burbuja "🧠 El agente piensa…" antes de la primera tool call.

---

### Mejora #10 — Prompt del usuario + system prompt visibles arriba

**Problema que resuelve:** hoy la página `/live-agent` no muestra ni el `user_prompt` que dispara la ejecución ni el `system_prompt` que condiciona al modelo. El aprendiz que abre la página después de lanzar el comando ve los pasos pero no el *origen* de los pasos. Reafirma que "el agente no es mágico": recibe reglas explícitas.

**Alcance:**
- `arkanum run` ya inyecta el quest al `session_start.payload`; ampliar el JSON para incluir `user_prompt: str` (el argumento que el aprendiz pasó).
- Nuevo endpoint `GET /api/system-prompt` que devuelve el contenido de `common/prompts/system_prompt.py:system_prompt` (string, sin secrets — es un archivo del repo).
- Panel desplegable en `/live-agent` con dos secciones: "Prompt del usuario" y "System prompt". Cerrado por defecto, con resumen del primer texto.
- Si el system_prompt es el placeholder vacío ("Escribe tu prompt del sistema aquí..."), mostrar nota: "Quest 04 te pide escribir esto; está vacío".

**Archivos a tocar:**
- `common/cli/commands/run.py` (ampliar payload de `session_start`).
- `common/dashboard/routes/api.py` (nuevo endpoint).
- `common/dashboard/templates/live_agent.html` (panel `<details>`).
- `common/dashboard/static/arcane.css` (estilos del panel).

**Esfuerzo:** ~1.5 h.
**Riesgo:** bajo. Solo lecturas.
**Criterio de éxito:** al abrir `/live-agent` después de un `arkanum run`, se ve el prompt original y, al expandir, el system prompt íntegro.

---

### Mejora #11 — Vista de "contexto creciente" (memoria del loop)

**Problema que resuelve:** en cada iteración el agente añade `candidate.content` y luego `Content(role="tool", parts=function_results)` a `messages`. El historial crece y crece, pero el aprendiz no lo ve. No siente el costo del contexto.

**Alcance:**
- Emitir `step_type=context_growth` al final de cada iteración con `payload={"messages": N, "tokens_in_context": ~estimación}`.
- Render como mini-progress-bar bajo la banda de iteración: "Contexto: 12 messages · ~3.4k tokens".
- Acumulado siempre creciente; comparable visualmente con el costo total.

**Archivos a tocar:**
- `quests/quest_08_manifesting_cycle/solution/solution.py` (introspección de `len(messages)` y tokens si `usage_metadata` disponible).
- `common/dashboard/static/dashboard.js` (render dentro de la banda — depende de #3).
- `common/dashboard/static/arcane.css`.

**Esfuerzo:** ~2 h.
**Riesgo:** bajo. Datos derivados.
**Dependencia blanda:** #3 (sin bandas, se muestra al final del trace).
**Criterio de éxito:** Q08 con 3 iteraciones muestra el contexto creciendo 1 → 3 → 5 messages (o similar) entre bandas.

---

### Mejora #12 — Latencia por llamada a Gemini

**Problema que resuelve:** un agente loop con latencias de ~3 s por iteración tarda visiblemente. El aprendiz no ve esta dimensión hoy. Es operativa (relevante para producción) y pedagógica (justifica streaming, caching, etc.).

**Alcance:**
- Medir `t1 = time.perf_counter()` antes de `client.models.generate_content(...)` y `t2 = time.perf_counter()` después.
- Emitir `step_type=latency` con `payload={"seconds": t2-t1, "iter": i}` justo después de cada llamada.
- UI: chip en el header de la banda — "Iteración 2 · 2.4 s".
- Total en el HUD (#13): "Latencia media: X s".

**Archivos a tocar:**
- `quests/quest_08_manifesting_cycle/solution/solution.py`.
- `common/dashboard/static/dashboard.js`.

**Esfuerzo:** ~1 h.
**Riesgo:** mínimo.
**Criterio de éxito:** cada banda de iteración lleva un tiempo en segundos.

---

### Mejora #13 — HUD sticky con KPIs en vivo

**Problema que resuelve:** los datos importantes (iteraciones, tools llamadas, tokens, USD, latencia) están dispersos en la lista de steps. Es difícil tener una "lectura instantánea" del estado.

**Alcance:**
- Barra sticky bajo el toolbar con 5 KPIs:
  - `Iteraciones: N / MAX_ITERS` (depende de #3)
  - `Tools llamadas: N` (cuenta de `function_call`)
  - `Tokens: ~Xk` (suma de `tokens`)
  - `Costo: ~$Y` (de #6 / `services/cost.py`)
  - `Latencia ⌀: Z s` (media de `latency` steps, de #12)
- Estilo: similar a `.profile-stats` pero compacto y sticky.
- Se calcula 100% en frontend con los steps que ya hay.

**Archivos a tocar:**
- `common/dashboard/templates/live_agent.html`.
- `common/dashboard/static/dashboard.js` (función `computeKpis(steps)`).
- `common/dashboard/static/arcane.css` (`.live-agent-hud`).

**Esfuerzo:** ~2 h.
**Riesgo:** bajo. Solo agregación de datos existentes.
**Criterio de éxito:** durante Q08 los 5 KPIs cambian en vivo a medida que llegan steps.

---

### Mejora #14 — Replay de un trace histórico

**Problema que resuelve:** un trace pasado se ve como un volcado estático. Para analizarlo (o presentarlo a otra persona) sería útil "reproducirlo" paso a paso a velocidad controlada.

**Alcance:**
- Botón ▶ Replay sobre un trace histórico (depende de #4).
- Controles: 0.5× / 1× / 2× / 4× / instantáneo.
- Renderiza steps con el mismo delta de `created_at` real (o un timing comprimido en modo rápido).
- Modo "presentación": pantalla completa, sin chrome.

**Archivos a tocar:**
- `common/dashboard/static/dashboard.js`.
- `common/dashboard/templates/live_agent.html`.

**Esfuerzo:** ~3 h.
**Riesgo:** medio (UX state machine).
**Dependencia dura:** #4 (sin historial, no hay qué reproducir).
**Criterio de éxito:** un trace de 18 steps se reanima en 18 s a 1×.

---

### Mejora #15 — Modo "explicador" para aprendices

**Problema que resuelve:** un aprendiz que ve `function_call`, `function_result`, `agent_thought` por primera vez puede no saber qué significa cada uno. Hay un costo de entrada al vocabulario.

**Alcance:**
- Toggle "📖 Modo explicador" en el toolbar.
- Al activarlo, cada step muestra un tooltip o pie de texto: "¿Qué es un function_call? Es cuando el modelo decide ejecutar una herramienta que le diste como tool…"
- Textos en `common/dashboard/services/glossary.py` (dict step_type → explicación), reutilizables si en el futuro hay un endpoint `/api/glossary`.

**Archivos a tocar:**
- Crear `common/dashboard/services/glossary.py`.
- `common/dashboard/routes/api.py`.
- `common/dashboard/static/dashboard.js`.
- `common/dashboard/static/arcane.css`.

**Esfuerzo:** ~2 h.
**Riesgo:** bajo. Documentación interactiva.
**Criterio de éxito:** un aprendiz que abre por primera vez `/live-agent` puede entender el flujo sin abrir docs externos.

---

### Mejora #16 — Export / copiar el trace

**Problema que resuelve:** un trace interesante es difícil de compartir. Hoy hay que tomar screenshots o copiar manualmente.

**Alcance:**
- Botón "📋 Copiar como markdown" — formatea el trace como markdown legible (encabezado, cada step como bullet con icono y payload en codeblock).
- Botón "💾 Descargar JSON" — devuelve el contenido crudo de `/api/trace/current?trace_id=...`.
- Opcional: ASCII art para Discord/Slack (sin colores).

**Archivos a tocar:**
- `common/dashboard/static/dashboard.js` (función `traceToMarkdown(data)`).
- `common/dashboard/templates/live_agent.html`.

**Esfuerzo:** ~1 h.
**Riesgo:** mínimo.
**Criterio de éxito:** el markdown copiado se pega en Discord y se ve como un poema técnico.

---

### Mejora #17 — Diff de contexto entre iteraciones

**Problema que resuelve:** entre dos iteraciones el `messages` cambia (se añaden cosas), pero el aprendiz no ve qué. Es como ver una película saltando los frames pares.

**Alcance:**
- Depende de #11 (que ya emite `context_growth`).
- En lugar de solo `count`, emitir `delta: [{"role": "tool", "preview": "..."}, ...]` con los nuevos items.
- Render: entre dos bandas de iteración, un mini panel: "Iter 2 → 3 · +2 messages (tool_response, model)".
- Click para expandir y ver el preview.

**Archivos a tocar:**
- `quests/quest_08_manifesting_cycle/solution/solution.py`.
- `common/dashboard/static/dashboard.js`.

**Esfuerzo:** ~3 h.
**Riesgo:** medio (privacidad de payloads — truncar previews a ~200 chars).
**Dependencia dura:** #11.
**Criterio de éxito:** al pasar a iteración 2, se ve "+1 tool_call (get_files_info), +1 tool_response".

---

### Mejora #18 — Editor del system prompt en vivo

**Problema que resuelve:** experimentar con prompts hoy requiere editar `common/prompts/system_prompt.py` en VS Code, guardar, volver a correr. Para iterar rápido conviene un editor en el dashboard.

**Alcance:**
- En el panel de #10, un botón "✏ Editar" que despliega un textarea con el contenido actual.
- Botón "💾 Guardar" que hace `POST /api/system-prompt` con el nuevo contenido.
- Backend escribe a `common/prompts/system_prompt.py` (con un diff confirmation y backup en `.system_prompt.py.bak`).
- Aviso: "el cambio se aplica desde el próximo `arkanum run`".

**Archivos a tocar:**
- `common/dashboard/routes/api.py` (POST endpoint).
- `common/dashboard/static/dashboard.js`.
- `common/dashboard/templates/live_agent.html`.

**Esfuerzo:** ~2.5 h.
**Riesgo:** medio. Escribe a un archivo del repo — riesgo de corromper sintaxis. Mitigación: validar que el string sea seguro (no inyectar Python ejecutable), reemplazar solo el contenido entre los triple-quotes.
**Criterio de éxito:** editar y guardar el system prompt desde la UI; correr `arkanum run` ve el cambio.

---

## 11. Plan de implementación recomendado (post-adenda)

Orden propuesto manteniendo el principio de "valor pedagógico × costo":

| Fase | Mejora | Esfuerzo acumulado | Justificación |
|---|---|---|---|
| 1 | #9 Pensamiento | 2 h | Cierra la opacidad central del loop. Es lo más quirúrgico. |
| 2 | #10 Prompts visibles | 3.5 h | Reafirma "no hay magia": muestra entradas. |
| 3 | #2 Agrupar call↔result | 6.5 h | Lista plana → unidades lógicas. |
| 4 | #3 Bandas por iteración | 8.5 h | Cierra el círculo conceptual de Q08. |
| 5 | #13 HUD sticky | 10.5 h | Lectura instantánea del estado. |
| 6 | #12 Latencia | 11.5 h | Pequeño, alta utilidad. |
| 7 | #11 Contexto creciente | 13.5 h | Aprovecha #3. |
| 8 | #4 Historial | 17.5 h | Necesario para #14. |
| 9 | #5 Stale detection | 19 h | Bug real, costo mínimo. |
| 10 | #14 Replay | 22 h | Aprovecha #4. |
| 11 | #15 Modo explicador | 24 h | Reduce curva de entrada. |
| 12 | #16 Export | 25 h | Compartir. |
| 13 | #6 Costo por iteración | 27.5 h | Conecta con dimensión económica. |
| 14 | #17 Diff contexto | 30.5 h | Necesario para entender pensamiento del modelo entre iteraciones. |
| 15 | #1 Emisor estructurado (full) | 33.5 h | Mejora estructural. Después del prototipo de #9. |
| 16 | #8 Polling adaptativo | 35 h | Pulido. |
| 17 | #18 Editor system prompt | 37.5 h | Última: tiene riesgo de tocar repo. |
| 18 | #7 Lanzar desde dashboard | 41.5 h | UX grande, contrato nuevo. |

**Ejecución del 2026-05-29:** se implementa el núcleo de la fase 1–5 (~10.5 h):
- ✅ #9 Pensamiento
- ✅ #10 Prompts visibles
- ✅ #2 Agrupar call↔result
- ✅ #3 Bandas por iteración
- ✅ #13 HUD sticky

Un commit por mejora. Sin coautor (regla persistente).
