# Comandos del CLI `arkanum`

> *“Una llave para cada cerradura.*
> *Un conjuro para cada propósito.”*
>
> — Zhyréon

El laboratorio expone su voluntad a través de un único comando — `arkanum` — que despliega **nueve subcomandos** según lo que necesites hacer. Esta entrada del Códex es tu mapa de bolsillo: explica para qué sirve cada uno, cuándo invocarlo y cuál es su efecto en el cronómetro, en la base de datos y en el dashboard.

> **Fuente de verdad:** `arkanum --help` (lista global) y `arkanum <comando> --help` (detalle por comando) son la referencia técnica. Si esta tabla desfasa con esos comandos, ganan los `--help`.

---

## Vista de un vistazo

| Comando | Propósito | Consume cuota Gemini | Efecto en dashboard |
|---|---|---|---|
| [`arkanum init`](#arkanum-init) | Registrar al aprendiz y configurar el laboratorio | Sí (ping de validación) | Abre el dashboard |
| [`arkanum doctor`](#arkanum-doctor) | Diagnóstico completo de prerequisitos | Sí (ping real) | Refresca `/setup` |
| [`arkanum current`](#arkanum-current) | Mostrar la quest actual | No | — |
| [`arkanum next`](#arkanum-next) | Mostrar la próxima quest tras la actual | No | — |
| [`arkanum progress`](#arkanum-progress) | Tabla con el estado de las 8 quests | No | — |
| [`arkanum start N`](#arkanum-start-n) | Ejecutar el starter del quest N; en Q07/Q08 emite traces al `/live-agent` automáticamente | Sí (si el starter llama Gemini) | Steps en `/live-agent` (Q07/Q08) |
| [`arkanum check N`](#arkanum-check-n) | Validar la solución del quest N | Sí | Sella la quest + abre `/celebrate` |
| [`arkanum cost`](#arkanum-cost) | Tokens consumidos y costo estimado en USD | No | — |
| [`arkanum dashboard`](#arkanum-dashboard) | Controlar el server (`start`/`stop`/`status`/`logs`/`open`) | No | Levanta o detiene el dashboard |

---

## Setup

### `arkanum init`

Wizard inicial. **Es lo primero que ejecutas en un repo recién clonado** (después de `uv sync` + activar el venv).

```bash
arkanum init
```

Qué hace:

1. Pregunta tu nombre y lo guarda como `apprentice.username` en la BD.
2. Verifica que `.env` exista y contenga `GEMINI_API_KEY`. Si no, te ofrece pegar la clave.
3. Hace un ping real a Gemini con tu clave (puedes saltarlo con `--skip-ping`).
4. Arranca el dashboard en background y lo abre en tu navegador.

Si ya tenías un aprendiz registrado, te ofrece actualizar el nombre (default: no).

---

### `arkanum doctor`

Diagnóstico completo de los 9 prerequisitos del laboratorio (Python, uv, dependencias, `.env`, API key, BD, dashboard, workspace, ping real a Gemini).

```bash
arkanum doctor
```

Misma información que la pestaña `/setup` del dashboard, pero en la terminal y siempre con ping real (no usa caché). Útil cuando algo no funciona y quieres una respuesta autoritativa de una sola pasada.

---

## Navegación

### `arkanum current`

Muestra la quest en la que estás. Si ya completaste las 8, muestra un mensaje arcano de cierre.

```bash
arkanum current
```

### `arkanum next`

Muestra la quest siguiente a la actual.

```bash
arkanum next
```

### `arkanum progress`

Tabla con las 8 quests y su estado: completada ✓, actual ★, sellada 🔒. Incluye intentos, tiempo y XP por quest.

```bash
arkanum progress
```

---

## Ejecutar y validar

Dos comandos para correr código: `start` y `check`. La diferencia clave es **qué hace cada uno con el resultado**.

### `arkanum start N`

Ejecuta el archivo `quests/quest_NN_*/starter/main.py` directamente.

```bash
arkanum start 1
arkanum start 3 "¿Qué es un agente IA?"   # Q03+ recibe argumentos vía argparse
arkanum start 7 "Lee notes.txt"           # Q07/Q08 trazan solas en /live-agent
```

Qué hace:

1. Resuelve el quest por su número (1..8).
2. Lanza `python -m quests.quest_NN_*.starter.main` como subprocess.
3. Reenvía cualquier argumento extra al starter.
4. Devuelve el exit code.

Qué **no** hace (en quests sin agent loop):

- No arranca el cronómetro de la quest (lo hace el botón "Empezar ahora" del dashboard).
- No valida la solución contra criterios.
- No emite eventos al dashboard.

**Cuándo usarlo:** mientras iteras sobre tu solución y quieres ver el output crudo sin las verificaciones del check. Útil para experimentar con prompts en Q03+.

> ⚠️ Aunque no "valida" nada, sí consume cuota de Gemini si el starter llama a `generate_content` (que es siempre desde Q01).

#### Tracing automático del agent loop (Q07/Q08)

En los quests con agent loop (`live_agent=True`, hoy **Q07 y Q08**), `start` **emite traces estructurados automáticamente** — sin ningún flag. La pestaña `/live-agent` del dashboard los muestra paso a paso.

```bash
arkanum start 7 "¿Qué archivos hay en la raíz?"
arkanum start 8 "Lee notes.txt y dime qué contiene"
```

Qué hace de más en estos quests:

1. Genera un `trace_id` único y lo imprime con el link a `/live-agent`.
2. Inserta un `session_start` step en la tabla `agent_traces`.
3. Fuerza `--verbose` en el starter (sin él, las tool calls se imprimen sin paréntesis y el parser no las reconoce).
4. Parsea cada línea del stdout buscando patrones (`Calling function: ...`, `Prompt tokens: ...`, etc.) y emite los steps correspondientes.
5. Inserta un `session_end` step al terminar.

Esto te deja ver la secuencia `function_call → function_result → siguiente iteración` en vivo, lo que da intuición de cómo razona el agente.

> ℹ️ **Opt-out:** con `ARKANUM_NO_DASHBOARD=1` el tracing se desactiva (útil en CI), coherente con `check` e `init`. El flag oculto `--live` permite forzar el tracing en cualquier quest; rara vez hace falta.

---

### `arkanum check N`

El comando que **sella** la quest. Ejecuta los pre-checks locales (sin tocar Gemini), luego corre el check real que valida tu solución contra criterios pedagógicos específicos.

```bash
arkanum check 1
arkanum check 1 --dry-run   # solo pre-checks, sin invocar Gemini
arkanum check 1 --yes       # auto-confirma si los pre-checks fallan (útil en CI)
```

Qué hace:

1. **Pre-checks locales** — verifica vía AST que tu starter importe lo necesario, llame a las funciones correctas, etc. Sin gastar cuota.
2. Si los pre-checks fallan, pide confirmación antes de seguir (a menos que pases `--yes` o `--dry-run`).
3. **Check real** — ejecuta el starter + valida criterios específicos del quest (palabras clave, estructura del output, etc.).
4. Si pasa: registra la completación, otorga XP + rango, abre `/celebrate` en el navegador.

**Cuándo usarlo:** cuando crees que tu solución está lista. Es el comando que el panel del dashboard te sugiere al final del quest.

---

## Observabilidad y costo

### `arkanum cost`

Tabla con los tokens consumidos en checks (prompt + response) y el costo estimado en USD.

```bash
arkanum cost
arkanum cost --per-attempt   # histórico de cada invocación, no agregado por quest
```

Las tarifas usadas son las de Gemini 2.5 Flash al momento de implementar el módulo. Sirve para tener una idea del orden de magnitud, no como factura oficial.

---

## Dashboard

### `arkanum dashboard`

Cinco subcomandos para controlar el server del dashboard.

```bash
arkanum dashboard start            # arranca el server (detached por default)
arkanum dashboard start --dev      # arranca en foreground con uvicorn --reload
arkanum dashboard stop             # detiene el server
arkanum dashboard status           # muestra PID + puerto
arkanum dashboard logs             # muestra las últimas líneas del log
arkanum dashboard logs --lines 100 # con un tamaño específico
arkanum dashboard open             # arranca (si hace falta) y abre el navegador
```

> ℹ️ `start` **levanta el server pero no abre el navegador** — solo te imprime la URL. Si quieres que además se abra el browser, usa `arkanum dashboard open`.

El puerto por defecto es **8765**. Si está ocupado, el lifecycle intenta 8766, 8767, 8768 antes de rendirse.

El server sobrevive al cierre de la terminal porque se desacopla con `Popen` + redirección de stdio.

**Opt-out:** si exportas `ARKANUM_NO_DASHBOARD=1`, los comandos `check` e `init` no intentarán arrancar el server ni emitirán eventos. Útil para CI.

---

## Atajos al ejecutar comandos

Todos los comandos `arkanum *` aceptan `--help`:

```bash
arkanum --help               # lista los 9 comandos
arkanum check --help         # detalle de check (incluyendo --dry-run, --yes)
arkanum start --help         # detalle de start
arkanum dashboard --help     # lista los 5 sub-subcomandos
arkanum dashboard start --help
```

Si no activaste el venv (`. .venv\Scripts\Activate.ps1` en PowerShell o `source .venv/bin/activate` en bash), antepón `uv run`:

```bash
uv run arkanum --help
```

---

## Tabla rápida: "qué comando uso si quiero..."

| Quiero... | Comando |
|---|---|
| Empezar desde cero | `arkanum init` |
| Ver qué quest estoy haciendo | `arkanum current` |
| Probar mi código sin "sellar" la quest | `arkanum start N` |
| Probar mi agente y ver el agent loop en vivo | `arkanum start N "..."` (Q07/Q08 trazan solas) |
| Validar la solución y completar la quest | `arkanum check N` |
| Saber cuántos tokens llevo gastados | `arkanum cost` |
| Verificar que todo el setup está sano | `arkanum doctor` |
| Reiniciar el dashboard | `arkanum dashboard stop && arkanum dashboard start` |
