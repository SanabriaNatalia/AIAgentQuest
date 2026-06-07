# Tracing — emitir steps al Live Agent

El módulo [`common/tracing.py`](../../common/tracing.py) permite que tu
agente envíe eventos estructurados al visualizador `/live-agent` del
dashboard. Es la forma "rica" de trazar — más fiel que el regex que
`arkanum start` aplica sobre tu `stdout`.

## Cómo se activa

`tracing.emit` solo hace algo cuando `ARKANUM_TRACE_ID` está en el
entorno. Ese ID lo inyecta `arkanum start` al lanzar el starter de un
quest con agent loop (Q07/Q08), donde el tracing es automático. Si corres
`python -m quests…` directamente —o `start` en un quest sin agent loop—
el módulo es no-op silencioso.

| Variable de entorno      | Quien la set     | Para qué |
|---|---|---|
| `ARKANUM_TRACE_ID`       | `arkanum start`  | Identifica el trace activo. Sin esto, `emit` no hace nada. |
| `ARKANUM_QUEST_DB_ID`    | `arkanum start`  | Asocia el trace a una quest concreta. |
| `ARKANUM_TRACE_URL`      | (override)        | Por defecto `http://127.0.0.1:8765/events/trace`. Cambia el destino si el dashboard corre en otro puerto. |

## API mínima

```python
from common.tracing import emit, trace_enabled

if trace_enabled():
    emit("agent_thought", payload={"text": "voy a leer notes.txt"})
```

`emit(step_type, name=None, payload=None)` hace un POST best-effort
(timeout 500ms, swallow de errores). No interrumpe el flujo del agente:
si el dashboard está caído, tu starter sigue funcionando.

`payload` se serializa con `json.dumps(..., default=str)`. Pasa dicts,
listas, primitivos — todo se vuelve JSON.

## Helpers de alto nivel

Para los patrones más comunes de Q07/Q08, hay atajos:

```python
from common.tracing import (
    emit_function_call,
    emit_function_result,
    emit_thought,
    emit_final,
)

emit_function_call("get_files_info", args={"path": "notes.txt"})
emit_function_result("get_files_info", result={"size": 1024, "content": "..."})
emit_thought("Voy a leer notes.txt para entender qué pide el usuario.")
emit_final("El archivo contiene la lista de la compra: pan, leche, café.")
```

El frontend ya sabe renderizar estos `step_type` con icono y prosa
distintiva (ver `common/dashboard/static/dashboard.js:iconFor` y
`renderStep`).

## Step types reconocidos

Lista mantenida en [`dashboard.js`](../../common/dashboard/static/dashboard.js):

| `step_type`         | Origen                              | Render |
|---|---|---|
| `session_start`     | `arkanum start` (Q07/Q08)           | Marca el inicio del trace; payload incluye `user_prompt`. |
| `session_end`       | `arkanum start` (Q07/Q08)           | Marca el final con exit code; toolbar pasa a sealed. |
| `function_call`     | parser de `start.py` **o** `emit`   | Tarjeta agrupada con pending spinner hasta que llega su result. Los args se muestran como lista clave/valor. |
| `function_result`   | parser de `start.py` **o** `emit`   | Se ancla dentro de su `function_call` (FIFO). El valor se desenvuelve de `{'result': …}` y un error se pinta en rojo. |
| `tokens`            | parser de `start.py` **o** `emit`   | Chip de uso (prompt/response). Suma al costo de la banda. |
| `iteration_start`   | parser de `start.py` (Q08) **o** `emit` | Abre una banda visual ("Iteración N / MAX"). Lo deriva del `Prompt tokens:` de cada llamada a Gemini. |
| `agent_final`       | parser de `start.py` **o** `emit`   | Burbuja final dorada — respuesta sin más tool calls. Lo deriva del `Final response:` + texto. |
| `error`             | parser de `start.py` **o** `emit`   | Tarjeta roja: excepción del loop (`Error in generate_content:`) o tope de iteraciones. |
| `agent_thought`     | `emit` solo                         | Burbuja de prosa serif italic — el razonamiento del modelo (el stdout no lo expresa). |
| `latency`           | `emit` solo                         | Chip de tiempo; suma al meta de la banda (el stdout no lo expresa). |
| `context_growth`    | `emit` solo                         | Panel desplegable con el delta de `messages` tras la iteración (el stdout no lo expresa). |

## El regex como fallback

`common/cli/commands/start.py` (en Q07/Q08) parsea el `stdout` del
starter línea por línea y, sin pedirle al aprendiz que escriba `emit`,
deriva: `function_call`, `function_result` (con args/valor limpios),
`tokens`, `iteration_start` (de cada `Prompt tokens:`), `agent_final`
(de `Final response:` + texto) y `error`. Esto significa que:

- El starter del aprendiz, una vez completado, muestra el loop **rico**
  en `/live-agent` aunque no use `tracing.emit`.
- Si el aprendiz reformatea el `print(f"Calling function: ...")`, el
  parser falla en silencio — pero `tracing.emit` no se ve afectado.
- Para evitar duplicados, la solución de Q08 **no** emite
  `iteration_start` ni `agent_final` por `emit` (los deriva el parser);
  reserva `emit` para lo que el stdout no puede expresar: `agent_thought`,
  `latency` y `context_growth`.

## Patrón recomendado para Q07

```python
from common.tracing import (
    emit_function_call,
    emit_function_result,
    emit_thought,
    trace_enabled,
)

# Dentro de tu loop del agente:
for candidate in response.candidates or []:
    if not candidate.content:
        continue
    for part in candidate.content.parts or []:
        if part.text and response.function_calls:
            emit_thought(part.text)

for fc in response.function_calls or []:
    if trace_enabled():
        emit_function_call(fc.name, args=dict(fc.args or {}))
    result = call_function(fc, verbose=args.verbose)
    # ... extraer part.function_response.response ...
    if trace_enabled():
        emit_function_result(fc.name, result=response_dict)
```

## Cómo agregar nuevos step types

1. Inventa un nombre `kebab_or_snake_case`. No colisiones con los de
   arriba.
2. Llama `emit("mi_nuevo_tipo", payload={...})` desde el starter o
   solución.
3. En `dashboard.js`, añade el case en `iconFor`, `labelFor` y
   `explainerFor` (este último alimenta la nota pedagógica del modo verbose).
4. En `arcane.css`, añade `.trace-step--mi_nuevo_tipo` con el color
   distintivo.

La tabla `agent_traces` no necesita migración — los `step_type` son
strings opacos para SQLite.

## Smoke local

```bash
# En una terminal: arranca el dashboard.
arkanum dashboard

# En otra: corre tu agente (Q08 traza solo).
arkanum start 8 "Lee notes.txt y dime qué contiene"

# Abre http://127.0.0.1:8765/live-agent — los steps aparecen en vivo.
```
