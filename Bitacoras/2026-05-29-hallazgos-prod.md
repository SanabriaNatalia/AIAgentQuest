# Bitácora — Hallazgos para llevar a master

> **Fecha de detección:** 2026-05-29
> **Rama de pruebas:** `feat/dashboard-arcano` (working tree desechable)
> **Por qué existe esta bitácora:** las soluciones de starters que pego para avanzar Q01..Q06 NO van a prod (los starters deben quedar con sus TODOs intactos para que cada aprendiz los resuelva). Pero **mientras resuelvo cada quest descubro problemas reales del producto** —tanto en pre-checks como en starters— que sí merecen merge a `master`. Aquí los anoto a medida que los encuentro.
>
> **Regla:** cuando termine de validar el flujo Q07/Q08 en esta rama, abro un branch nuevo desde `master` y aplico solo los fixes listados aquí.

---

## Estado de cada hallazgo

| ID | Quest | Resumen | Estado |
|---|---|---|---|
| H-01 | Q01 | Pre-check usa string matching del placeholder | ✅ Fix validado en rama de pruebas |
| H-02 | Q02 | Starter no importa `show_prompt` aunque la solución de Q01 lo usa | ✅ Fix validado en rama de pruebas |
| H-03 | Q03 | Mismo patrón que H-02: starter omite `show_prompt` | ✅ Fix validado en rama de pruebas |
| H-04 | Q04 | Typo `akranum check 4` + continuador bash `\` que no funciona en PowerShell | ✅ Fix validado en rama de pruebas |
| H-05 | Q07 | Docstring usa slug equivocado (`_embodiment` vs `_incarnation`) y comando inconsistente | ✅ Fix validado en rama de pruebas |
| H-06 | Q07 | Solución de referencia `solution/call_function.py:53` apunta a workspace inexistente con slug viejo | ✅ Fix validado en rama de pruebas |
| H-07 | Q05 | Solución de referencia `solution/main.py:10` importa `get_valid_target_path` desde `get_files_info` (módulo equivocado) | ✅ Fix validado en rama de pruebas |
| H-08 | todos | Wrap de `rich.Console` rompe la búsqueda `expected in output` en `check.py` cuando la terminal es estrecha | ✅ Fix completo (Q01..Q07 todos llevan `COLUMNS=1000`. Q08 no aplica porque su check no corre el starter) |
| H-09 | todos | UX confusa: la tabla pre-check toda en verde + panel rojo con solo el primer faltante. Aprendiz no sabe qué validación específica falló | ❌ pendiente (decisión: requiere refactor de 8 check.py + helper compartido) |
| H-10 | Q05 | `arkanum check` imprime "este check consume cuota de Gemini" incluso en Q05 que no llama a Gemini | ✅ Fix validado en rama de pruebas |
| H-11 | Q06 | Placeholders de los schemas en `write_file.py` y `run_python_file.py` reusan el nombre `schema_get_file_content` (copypaste). El aprendiz que solo cambia `None` por la definición termina con la variable mal nombrada | ✅ Fix validado en rama de pruebas |
| H-12 | Q06 | TODO 6.7 del starter sugiere `uv run python -m quests.quest_06_tool_chest.check` en vez de `arkanum check 6` (mismo patrón inconsistente que H-05) | ✅ Fix validado en rama de pruebas |
| H-13 | CLI | `arkanum check N "prompt"` falla con "Got unexpected extra argument", pero `arkanum start N "prompt"` y `arkanum run N "prompt"` sí aceptan prompt | ✅ Fix validado en rama (opción B: env var con fallback) |
| H-14 | Q06 | Output esquemático en consola: solo `Calling function:`, sin pensamiento ni explicación | ✅ Fix validado en rama (TODO 6.6 ahora indica mostrar `response.text` + function_calls juntos, no mutuamente excluyentes). El "resultado de la tool" requiere Q07 — fuera de scope de Q06. |
| H-15 | Q07+ | `arkanum check N` no alimenta el Live Agent | ✅ Fix completo validado (camino "vivo" para Q07: pregunta ANTES del check, ejecuta starter con tracing una sola vez, delega validación a `validate_output()` sin re-invocar Gemini · camino "post" para Q08: pregunta después + spawn detached de `arkanum run`) |
| H-19 | Q08 catálogo | `uses_gemini=True` por default era incorrecto para Q08: su `check.py` valida solo estado del filesystem | ✅ Fix validado en rama (`uses_gemini=False` en Q08) |
| H-20 | live-agent | Cada step se persistía 2× en `agent_traces` porque `_emit_step` llamaba `record_step` directo + POST a `/events/trace` que también llama `record_step` | ✅ Fix validado en rama (eliminado el POST redundante en `run.py` y `check.py`) |
| H-21 | run.py | Sin `--verbose`, el starter de Q07/Q08 imprime `" - Calling function: name"` (con guion, sin paréntesis), lo cual el regex del parser NO matchea → `/live-agent` queda con solo `session_start`/`session_end` | ✅ Fix validado en rama (`arkanum run` fuerza `--verbose` si no estaba) |
| H-22 | Q07 | Ni el docstring del starter ni el dashboard `/live-agent` aclaran que Q07 **no** devuelve el resultado al modelo. El README sí, pero quien se salta el README ve un trace que parece "incompleto" | ✅ Fix parcial (docstring del starter ahora tiene una nota ⚠ explícita; parte de "nota en el dashboard" queda pendiente por decisión de UX) |
| H-23 | Q08 workspace | Workspace de Q08 estaba triplemente roto: `test.py` (sin s) cuando todo el código espera `tests.py`; `calculator.py` como `class Calculator` mientras `test.py` importa funciones de módulo (ImportError); ningún print "All tests passed!" que el check espera. Imposible que Q08 funcionara de fábrica | ✅ Fix validado en rama (calculator.py como funciones de módulo, tests.py con asserts + print) |
| H-24 | call_function.py | `working_directory` estaba hardcoded a `quests/quest_07_agent_incarnation/workspace`. El agente de Q08 (y cualquier quest futura) operaba sobre el workspace de Q07 — `arkanum check 8` jamás aprobaría porque calculator.py de Q08 nunca cambiaba | ✅ Fix validado en rama (lee env var `ARKANUM_WORKSPACE` inyectada por `start`/`run`/`check`) |
| H-16 | docs | Inconsistencias menores en READMEs vs código real (mensajes de error, idioma, formato) | ✅ Fix validado en rama (Q05 mensaje de error, Q06 prompt en español + formato una línea, Q07 formato con paréntesis y --verbose) |
| H-17 | Q07/Q08 README | READMEs no mencionan `arkanum run` ni `/live-agent` | ✅ Fix validado en rama (sección "🪞 Ver al agente en vivo" + tabla de comandos) |
| H-18 | Q07/Q08 check | La celebración no apunta al Live Agent | ✅ Fix validado en rama (línea adicional con `arkanum run` + URL) |

---

## H-01 — Pre-check de Q01 falsa "Prompt vacío" cuando aprendiz sigue las instrucciones

**Archivo afectado:** `common/cli/pre_checks/q01.py`
**Detectado al resolver:** Q01

### Síntoma reproducible

1. El aprendiz lee `starter/main.py` y sigue al pie de la letra el docstring que dice *"No borres el código existente, solo añádele lo que se pide en cada paso"*.
2. En el TODO 1.5 cambia `prompt = ""` a `prompt = "Explícame qué es un agente IA..."`.
3. **No borra** el bloque siguiente:
   ```python
   if not prompt:
       raise SystemExit(
           "\n❌ Falta resolver el TODO 1.5 (definir el prompt).\n"
           '  prompt = ""\n'   # ← string literal con el placeholder
           ...
       )
   ```
4. Corre `python -m quests.quest_01_first_invocation.starter.main` → **funciona perfecto**.
5. Corre `arkanum check 1` → pre-check **rojo**: "El placeholder `prompt = ""` debe reemplazarse por tu prompt."

### Causa raíz

El pre-check hace string matching crudo sobre el source del archivo:

```python
'prompt = ""' not in source and "prompt = ''" not in source
```

La cadena `prompt = ""` aparece también dentro del mensaje del `raise SystemExit`, así que el check confunde docs/mensajes con código real.

### Fix propuesto

Reemplazar el string matching por análisis con `ast` que mire solo asignaciones top-level. Validado en esta rama; ver el código en `common/cli/pre_checks/q01.py` función `_prompt_assignment_is_nonempty`. Núcleo:

```python
def _prompt_assignment_is_nonempty(tree: ast.Module) -> bool:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "prompt" for t in node.targets):
            continue
        value = node.value
        if isinstance(value, ast.Constant):
            if isinstance(value.value, str) and value.value.strip():
                return True
        else:
            return True  # fstring, variable, expresión: válido
    return False
```

Ventajas: inmune a placeholders mencionados en mensajes, comentarios o docstrings; acepta `prompt = f"..."`, `prompt = some_var`, etc.

### Revisar por simetría

Mismo patrón en otros pre-checks (`q02..q06`): los `regex_in_source(...)` también pueden devolver falsos positivos si el aprendiz menciona el formato esperado en un comentario. No es crítico hoy porque `check.py` corre el starter y valida el stdout real, pero conviene auditarlos.

---

## H-02 — Starter de Q02 omite `show_prompt` en imports

**Archivo afectado:** `quests/quest_02_arcane_gauge/starter/main.py`
**Detectado al resolver:** Q02

### Síntoma reproducible

1. El aprendiz lee el TODO 2.0 del starter de Q02:
   > *"Copia tu solución del Quest 01 en este archivo. No copies los imports ni la función show_quest_header, solo el código que va después."*
2. Abre `quests/quest_01_first_invocation/solution/solution.py` y copia desde la línea 28 (`load_dotenv()`) hasta el final.
3. Esa solución usa `show_prompt(prompt)`.
4. Corre el starter → **NameError: name 'show_prompt' is not defined**.

### Causa raíz

El starter de Q02 importa:

```python
from common.utils.ui import (
    show_quest_header,
    narrator,
    agent,
    success,
)
```

Falta `show_prompt`. La solución de Q01 (referenciada por la instrucción) sí lo importa y lo usa. Como el TODO 2.0 prohíbe copiar imports, el aprendiz queda atascado.

### Fix propuesto

Añadir `show_prompt` al import del starter de Q02:

```python
from common.utils.ui import (
    show_quest_header,
    narrator,
    agent,
    success,
    show_prompt,
)
```

Validado en esta rama. Cambio mínimo, una sola línea.

### Mejora secundaria opcional

El TODO 2.0 podría aclarar: *"El starter ya importa todo lo necesario para la solución de Q01. Si copias código que necesita un símbolo nuevo, añádelo al bloque de import de arriba."* — desbloquea al aprendiz que cae en el mismo patrón en Q03..Q08.

### Revisar por simetría

Hay que auditar todos los starters de Q03..Q08 — cada vez que el TODO X.0 dice "copia tu solución de la quest anterior", el starter debería importar el superset de símbolos que esa solución usa. Si falta uno, repetimos el mismo bug.

---

---

## H-03 — Starter de Q03 omite `show_prompt` (confirmación del patrón H-02)

**Archivo afectado:** `quests/quest_03_apprentice_voice/starter/main.py`
**Detectado al resolver:** Q03

### Síntoma reproducible

Idéntico a H-02. El TODO 3.0 pide *"Copia tu solución del Quest 02 en este archivo. No copies los imports..."*. La solución de Q02 (y de Q01 antes) usa `show_prompt(prompt)`. El starter de Q03 importa:

```python
from common.utils.ui import (
    show_quest_header,
    narrator,
    agent,
    success,
)
```

Falta `show_prompt`. Mismo `NameError` al primer intento del aprendiz.

### Conclusión: patrón parcial, no uniforme

Después de Q02 y Q03 confirmando el bug, pensé que sería sistemático. **Q04 lo refuta**: su starter sí incluye `show_prompt` en los imports desde el origen. Por tanto la auditoría de Q05..Q08 sigue siendo necesaria pero **caso por caso** — no se puede asumir que todas las quests tienen el mismo desfase.

Estado parcial del audit:

| Quest | `show_prompt` en starter | Notas |
|---|---|---|
| Q02 | ❌ falta | H-02 |
| Q03 | ❌ falta | H-03 |
| Q04 | ✅ presente | — |
| Q05 | ❓ por auditar | |
| Q06 | ❓ por auditar | |
| Q07 | ❓ por auditar | |
| Q08 | ❓ por auditar | |

### Fix propuesto

Mismo que H-02: añadir `show_prompt` al import del starter de Q03 (validado en rama).

### Mitigación estructural recomendada (opcional pero deseable)

En lugar de parchear quest por quest, el fix limpio es **estandarizar el bloque de imports en todos los starters Q02..Q08** para que importen siempre el superset:

```python
from common.utils.ui import (
    show_quest_header,
    narrator,
    agent,
    success,
    show_prompt,
)
```

Costo: 6 archivos, una línea cada uno. Beneficio: elimina el bug para todas las quests futuras sin tener que pensar quest a quest.

---

## H-04 — Docstring de Q04 tiene typo y continuador de línea estilo bash

**Archivo afectado:** `quests/quest_04_arkanum_laws/starter/main.py` (líneas 9-15)
**Detectado al resolver:** Q04

### Síntoma reproducible

El docstring del starter, que el aprendiz lee al abrir el archivo, dice:

```
Ejecutar desde la raíz del proyecto:

    arkanum start 4 \
    "¿Cuál es la capital de Francia?"

Una vez hayas terminado, valida tu solución ejecutando:

    akranum check 4
```

Dos problemas:

1. **`akranum check 4`** — typo. El comando real es `arkanum check 4`. El aprendiz que copie literal verá `'akranum' is not recognized as an internal or external command`.
2. **`arkanum start 4 \`** — el `\` como continuador de línea solo funciona en bash/zsh. En PowerShell (entorno por defecto en Windows) y en CMD ni siquiera es válido. El aprendiz que copie literal recibe error de sintaxis del shell.

### Fix propuesto

Ambos comandos en una sola línea, sin typos:

```
Ejecutar desde la raíz del proyecto:

    arkanum start 4 "¿Cuál es la capital de Francia?"

Una vez hayas terminado, valida tu solución ejecutando:

    arkanum check 4
```

Aplicado en la rama de pruebas (commit pendiente).

### Revisar por simetría

Auditoría completa de los 8 starters tras este hallazgo:

| Quest | Comando start | Comando check | Estado |
|---|---|---|---|
| Q01 | `arkanum start 1` | `arkanum check 1` | OK |
| Q02 | `arkanum start 2` | `arkanum check 2` | OK |
| Q03 | `arkanum start 3 "¿Qué es un agente IA?"` | `arkanum check 3` | OK |
| Q04 | (corregido) | (corregido) | era buggy |
| Q05 | `arkanum start 5` | `arkanum check 5` | OK (no usa prompt) |
| Q06 | `arkanum start 6 "¿Qué archivos hay en la raíz?"` | `arkanum check 6` | OK |
| Q07 | `arkanum start 7 "..."` y `--verbose` | (ver H-05) | parcial |
| Q08 | `arkanum start 8 "..."` y `--verbose` | `arkanum check 8` | OK |

Solo Q04 tenía el continuador bash y el typo. Q01..Q08 ya muestran el comando con prompt como parámetro cuando aplica.

---

## H-05 — Docstring de Q07 usa slug equivocado y comando inconsistente

**Archivo afectado:** `quests/quest_07_agent_incarnation/starter/main.py` (línea 18)
**Detectado al resolver:** Q04 (auditoría de simetría)

### Síntoma reproducible

El docstring del starter de Q07 dice para validar:

```
Una vez hayas terminado, valida tu solución ejecutando:

    uv run python -m quests.quest_07_agent_embodiment.check
```

Dos problemas:

1. **El slug es `quest_07_agent_incarnation`, no `quest_07_agent_embodiment`.** El módulo no existe con ese nombre. Aprendiz literal → `No module named 'quests.quest_07_agent_embodiment'`.
2. **Inconsistente con el resto de quests** que usan `arkanum check N`. Hace al aprendiz salirse de la convención que aprendió en Q01..Q06.

### Fix propuesto

Reemplazar por la forma corta canónica:

```
Una vez hayas terminado, valida tu solución ejecutando:

    arkanum check 7
```

Aplicado en la rama de pruebas (commit pendiente).

### Revisar por simetría

Buscar en el resto de starters/docs cualquier referencia restante a `_embodiment` (parece ser un slug viejo que se renombró pero quedó referencia obsoleta en este docstring). Si aparece en READMEs, hints o docs de `docs/`, también arreglar.

Ver H-06 inmediatamente: el mismo slug obsoleto reaparece en la solución de referencia de Q07.

---

## H-06 — Solución de referencia de Q07 apunta a un workspace inexistente

**Archivo afectado:** `quests/quest_07_agent_incarnation/solution/call_function.py` (línea 52-54)
**Detectado al resolver:** Q04 (auditoría del slug `_embodiment` desencadenada por H-05)

### Síntoma reproducible

1. El aprendiz, al resolver el TODO 7.1 (paso 7) en `common/functions/call_function.py`, se atasca y abre la solución de referencia.
2. Ve este fragmento:
   ```python
   args["working_directory"] = (
       "quests/quest_07_agent_embodiment/workspace"
   )
   ```
3. Lo copia tal cual. Su agente queda apuntando a un directorio que no existe.
4. Al correr `arkanum start 7 "..."`, las tools intentan listar/leer ese workspace y devuelven errores del tipo `FileNotFoundError` o `path not allowed`.

### Causa raíz

El slug del módulo es `quest_07_agent_incarnation` (visible en el path `quests/quest_07_agent_incarnation/`). Pero la solución reusa un slug viejo `quest_07_agent_embodiment` que ya no existe. **Inconsistente con el comentario del TODO original**, que en `common/functions/call_function.py:87` sí escribe el slug correcto:

```python
# args["working_directory"] = "quests/quest_07_agent_incarnation/workspace"
```

Es decir: la guía del aprendiz dice una cosa, la solución de referencia dice otra. Quien siga la solución cae en el bug.

### Fix propuesto

Cambiar la línea 53 de `solution/call_function.py` por:

```python
args["working_directory"] = (
    "quests/quest_07_agent_incarnation/workspace"
)
```

Aplicado en la rama de pruebas.

### Revisar por simetría

- Buscar `_embodiment` global: además del docstring de H-05 y este archivo, queda una mención en `Bitacoras/avance.md` (histórica, no se ejecuta — segura de ignorar).
- Verificar que no haya quests Q08+ que importen módulos con el slug viejo. (Q08 hereda y trabaja sobre el mismo workspace; conviene revisar `quests/quest_08_manifesting_cycle/` también).

---

## H-07 — Solución de Q05 importa desde el módulo equivocado

**Archivo afectado:** `quests/quest_05_forbidden_directory/solution/main.py` (línea 10)
**Detectado al resolver:** Q05

### Síntoma reproducible

1. El aprendiz lee el starter de Q05 que dice trabajar en dos archivos: `get_valid_target_path.py` y `starter/main.py`.
2. Se atasca en los TODOs 5.7 / 5.8 y abre la solución de referencia `solution/main.py`.
3. La línea 10 dice:
   ```python
   from common.functions.get_files_info import get_valid_target_path
   ```
4. Si el aprendiz copia este import literal, recibe `ImportError: cannot import name 'get_valid_target_path' from 'common.functions.get_files_info'`.

### Causa raíz

El validador vive en `common/functions/get_valid_target_path.py`, no en `get_files_info.py`. El starter de Q05 lo importa correctamente (línea 27):

```python
from common.functions.get_valid_target_path import get_valid_target_path
```

Pero la solución de referencia se equivocó de módulo. Mismo patrón conceptual que H-06: **la solución contradice al starter/guía oficial** y rompe a quien la copie.

### Fix propuesto

Reemplazar la línea 10 de `solution/main.py`:

```python
from common.functions.get_valid_target_path import get_valid_target_path
```

Aplicado en la rama de pruebas.

### Revisar por simetría

Auditar todos los archivos de `solution/` en Q01..Q08 buscando imports raros o referencias a módulos viejos. Este tipo de bug (solución desactualizada respecto al starter) es el más venenoso para el aprendiz, porque la solución es justamente lo que consulta cuando está perdido.

---

## H-08 — Wrap de Rich rompe la validación post-runtime de todos los `check.py`

**Archivos afectados:** los 8 `quests/quest_0X_*/check.py`
**Detectado al validar Q05** (pero estructural, aplica a todos).

### Síntoma reproducible

1. El aprendiz tiene su terminal a ancho razonable (~75-100 cols).
2. Corre `arkanum check 5`.
3. Los pre-checks salen todos en verde.
4. La sección "Ejecutando check" reproduce el output del starter — visualmente todo PASS verde, los 5 tests aprobados.
5. Inmediatamente después, panel rojo "QUEST INCOMPLETO" diciendo "No encontré una salida esperada. Faltó: Ruta bloqueada correctamente -> '../' is outside the permitted working directory".
6. El aprendiz mira la salida y **ve** ese mensaje. Le confunde por completo.

### Causa raíz

`common/utils/ui.py:58` define:

```python
def pass_test(message: str) -> None:
    console.print(f"[bold green]✅ PASS > [/bold green]{message}")
```

Con `console = Console()` sin argumentos, Rich detecta el ancho real de la terminal del aprendiz y **envuelve líneas largas automáticamente**, insertando `\n`. El mensaje de Q05 mide ~90 chars y se parte:

```
✅ PASS > Ruta bloqueada correctamente -> '../' is outside the permitted    ← \n aquí
working directory
```

`check.py` hace `if expected not in output` con `expected` como string contigua. La subcadena exacta no existe porque está partida por el wrap → falso negativo.

### Por qué es estructural

Los 8 `check.py` usan el mismo patrón:

| Quest | Línea relevante | Strings esperados con riesgo de wrap |
|---|---|---|
| Q01 | `if "Agente:" not in output` | bajo (string corto) |
| Q02 | `if "Prompt tokens:" not in output` | bajo |
| Q03 | `if prompt not in output` | **alto** si el aprendiz pasa prompts largos |
| Q04 | `if EXPECTED_RESPONSE not in output` | medio (la respuesta del modelo puede ser larga) |
| Q05 | `for expected in REQUIRED_OUTPUTS` | **confirmado roto** |
| Q06 | `for expected in REQUIRED_OUTPUTS` | **alto** (rutas largas) |
| Q07 | `for expected in REQUIRED_OUTPUTS` | **alto** |
| Q08 | `if "All tests passed!" not in output` | bajo |

### Fix propuesto

Forzar `COLUMNS=1000` en el `env` del `subprocess.run` que ejecuta el starter. Rich lee `COLUMNS` antes de detectar el TTY y, con un valor enorme, jamás envuelve.

```python
import os
env = os.environ.copy()
env["COLUMNS"] = "1000"
result = subprocess.run([...], env=env, ...)
```

Aplicado en `quests/quest_05_forbidden_directory/check.py` (validar tras commit). Replicar en los 7 restantes con un loop o crear un helper compartido `common/cli/_check_subprocess.py`.

### Fix preferido (estructural)

Crear `common/cli/check_runner.py` con:

```python
def run_starter_capturing(quest_module: str, *, timeout: int = 20) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.setdefault("COLUMNS", "1000")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    return subprocess.run(
        [sys.executable, "-m", quest_module],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=env,
    )
```

Y refactorizar los 8 `check.py` para llamarlo. Pierde duplicación, blinda contra futuros wrap-bugs.

### Revisar por simetría

Considerar el mismo fix en `common/cli/commands/run.py:run_module_capturing` que lanza los starters de Q07/Q08 — el visualizador Live Agent también captura stdout línea por línea. Si Rich envuelve un `Calling function: ...` muy largo, el regex se rompe igual. Verificar.

---

## H-09 — UX del check.py es confusa cuando falla el subprocess post-runtime

**Archivos afectados:** los 8 `quests/quest_0X_*/check.py`
**Detectado al validar Q05.**

### Síntoma

El usuario lo describió mejor que yo: *"sería bueno ser más claros con el error, como poner una x roja en el item que falló, porque sale todo en verde"*.

Hoy el flujo visual es:

1. Tabla de pre-checks con ✔/✘ por cada validación AST (claro y didáctico).
2. Output crudo del subprocess (puede ser largo, con sus propios PASS verdes).
3. Si falla algo: **panel rojo gigante con texto plano** mencionando solo el primer expected faltante.

El aprendiz no puede:
- Ver una tabla equivalente a la de pre-checks que diga "esta salida sí / esta salida no".
- Saber si fallaron 1 o 5 outputs.
- Distinguir entre "el starter crasheó" y "el starter corrió pero faltó un texto".

### Fix propuesto

Después del subprocess, en lugar de un `fail(...)` de texto, mostrar una segunda tabla `rich.Table` con:

| Esperado | Encontrado |
|---|---|
| `Validando ruta permitida: .`         | ✔ |
| `Ruta válida ->`                       | ✔ |
| `Validando ruta prohibida: ../`        | ✔ |
| `Ruta bloqueada correctamente -> ...`  | ✘ |

Más una columna opcional con el snippet del stdout donde se esperaba, o la línea más cercana que se encontró.

Recomendación: crear `common/cli/check_runner.py:report_required_outputs(output, expected_list)` que devuelve la tabla `rich.Table` lista para imprimir. Reusable en los 8 checks.

### Prioridad

Media. No es un bug funcional — el check sí falla cuando debe fallar (modulo H-08). Pero la UX para entender el fallo es mala, y combinado con H-08 confunde mucho al aprendiz (que ve verde por todos lados y luego un rojo opaco).

---

## H-10 — Aviso "consume cuota de Gemini" se imprime incluso cuando no es cierto

**Archivos afectados:** `common/cli/commands/check.py` (líneas 92-104)
**Detectado al ejecutar `arkanum check 5`**.

### Síntoma

```
Ejecutando check de Quest 5 — El Directorio Prohibido
Aviso: este check consume cuota de Gemini.
```

Pero Q05 (`El Directorio Prohibido`) es 100% local: solo prueba `os.path.abspath`/`commonpath` contra rutas válidas/inválidas. **No invoca el modelo en ningún momento**. El aviso es factualmente falso y mete ruido pedagógico — sugiere al aprendiz que su quota está siendo gastada cuando no.

### Causa raíz

El aviso es un `console.print(...)` hardcoded en `check.py:104` que se ejecuta para todas las quests sin condicionar:

```python
console.print("[yellow]Aviso:[/] este check consume cuota de Gemini.")
```

Lo mismo en `check.py:93-94` (el mensaje de `typer.confirm` tras pre-checks fallidos también menciona Gemini).

### Fix propuesto

Añadir un campo `uses_gemini: bool = True` al dataclass `QuestMeta` (default True para no romper nada) y poner `False` solo en Q05.

```python
@dataclass(frozen=True)
class QuestMeta:
    ...
    uses_gemini: bool = True
```

```python
QuestMeta(
    slug="quest_05_forbidden_directory",
    ...
    uses_gemini=False,
),
```

Y condicionar los dos mensajes:

```python
if quest.uses_gemini:
    console.print("[yellow]Aviso:[/] este check consume cuota de Gemini.")

confirm_msg = (
    "Los pre-checks locales fallaron. ¿Continuar con el check real "
    "(consume cuota de Gemini)?"
    if quest.uses_gemini
    else "Los pre-checks locales fallaron. ¿Continuar con el check real?"
)
```

Aplicado en la rama de pruebas. Cambio aislado y a prueba de futuro: si se añade otra quest sin Gemini (ej. una quest de seguridad pura como Q05), solo hay que marcar `uses_gemini=False`.

### Revisar por simetría

- Otros sitios donde se mencione "cuota de Gemini" o se asuma que toda quest invoca al modelo:
  - `docs/cli/commands.md:120` menciona "consume cuota de Gemini" en contexto de `arkanum start` — ese mensaje también necesitaría matiz si `arkanum start 5` se documenta.
  - `Bitacoras/2026-05-20-plan-pruebas.md:333` lo lista como output esperado del TC de Q01 — vigente, no es bug ahí.
- Considerar también si la pre-check tabla podría mostrar un badge "100% local" para Q05 al inicio, para que el aprendiz sepa de antemano que no gastará tokens.

---

## H-11 — Placeholders de schemas copypaste mal nombrados en Q06

**Archivos afectados:**
- `common/functions/write_file.py` (línea 11)
- `common/functions/run_python_file.py` (línea 12)
**Detectado al resolver Q06.**

### Síntoma reproducible

El aprendiz abre `write_file.py` para resolver TODO 6.2 (definir el schema). Ve:

```python
# TODO 6.2 (write_file.py): Define el schema para la función write_file,
# similar a schema_get_files_info
# ...
schema_get_file_content = None
```

El comentario dice "schema para write_file", pero la variable se llama `schema_get_file_content`. Tres caminos posibles para el aprendiz:

1. **No nota la inconsistencia** y solo reemplaza `None` por la definición del schema:
   ```python
   schema_get_file_content = types.FunctionDeclaration(name="write_file", ...)
   ```
   La variable queda mal nombrada. El pre-check `q06.py:51` busca `regex_in_source(path, rf"schema_write_file\s*=\s*types\.FunctionDeclaration")` → **falla**. El aprendiz ve "schema_write_file definido como FunctionDeclaration ✘" y se confunde porque su archivo "tiene un schema".

2. **Lo nota y renombra** la variable a `schema_write_file`. Pasa el pre-check.

3. **Decide importar la variable con el nombre que ve** desde call_function.py: `from common.functions.write_file import schema_get_file_content as schema_write_file`. Solución hacky.

Lo más probable es el camino 1, que es justo el más confuso.

### Causa raíz

Copypaste sucio de `get_file_content.py` (donde sí es correcto) hacia los otros dos archivos, sin renombrar la variable. El comentario sí se renombró, lo que hace el bug aún más sigiloso.

### Fix propuesto

Renombrar el placeholder en cada archivo para que coincida con el schema esperado por el pre-check:

```python
# common/functions/write_file.py
schema_write_file = None  # placeholder coherente con el TODO

# common/functions/run_python_file.py
schema_run_python_file = None
```

Aplicado en la rama de pruebas (con la implementación completa, no como `None`).

### Revisar por simetría

Buscar más casos de copypaste en `common/functions/`:

- `grep -rn "schema_\w\+\s*=\s*None"` en `common/functions/` post-fix: 0 matches. Bien.
- Verificar `common/functions/__init__.py` por si exporta nombres mal: no aplica (no hay re-exports problemáticos).

### Prioridad

**Alta.** Es el tipo de bug que parece "el código del aprendiz está mal" pero en realidad es el placeholder. Aprendiz pierde 20-40 min debugueando algo que no es su error.

---

## H-12 — TODO 6.7 sugiere comando `uv run python -m` en vez de `arkanum check 6`

**Archivo afectado:** `quests/quest_06_tool_chest/starter/main.py` (TODO 6.7 original)
**Detectado al resolver Q06.**

### Síntoma reproducible

El TODO 6.7 del starter terminaba con:

```
Cuando hayas validado que las tools se están llamando correctamente,
ejecuta el check para completar la quest:

uv run python -m quests.quest_06_tool_chest.check
```

Dos problemas:
1. **Inconsistente** con el resto de quests que usan `arkanum check N`. Mismo patrón de H-05 (Q07 docstring) confirmando el bug.
2. **Inconsistente con el propio docstring del archivo** que arriba (línea 14) ya dice `arkanum check 6`.

### Causa raíz

Inercia del estado pre-`arkanum` CLI: cuando los checks se invocaban directo con `python -m`. La línea quedó copy-pasteada al añadir el wrapper Typer.

### Fix propuesto

Cambiar `uv run python -m quests.quest_06_tool_chest.check` → `arkanum check 6` en el TODO 6.7.

Aplicado en la rama de pruebas (al simplificar el starter, el TODO 6.7 quedó eliminado entero, pero al llevarlo a master conviene preservar el TODO original y solo arreglar el comando).

### Revisar por simetría

Auditoría global ejecutada con `grep -rn "uv run python -m quests"`:

| Archivo | ¿Es bug? |
|---|---|
| `quests/quest_02_arcane_gauge/solution/solution.py:10` | No — documenta cómo correr la solución como módulo. Aceptable porque no hay atajo `arkanum` para correr soluciones. |
| `quests/quest_03_apprentice_voice/solution/solution.py:11` | No — mismo caso. |
| `quests/quest_03_apprentice_voice/README.md:57` | No — marcado como "equivalente legacy". |
| `quests/quest_04_arkanum_laws/solution/solution.py:11` | No — mismo caso. |
| `quests/quest_06_tool_chest/solution/solution.py:11` | No — mismo caso. |
| `quests/quest_07_agent_incarnation/README.md:147` | No — marcado como "equivalente legacy". |
| `quests/quest_07_agent_incarnation/solution/solution.py:13` | No — mismo caso. |

Patrón consolidado: usar `uv run python -m ...` en `solution/solution.py` es válido (explica cómo ejecutar la solución como módulo); usarlo en starter o como sugerencia de check es **bug**. Después de los fixes, no quedan ocurrencias problemáticas.

---

## H-13 — `arkanum check N "prompt"` falla mientras `arkanum start N "prompt"` funciona

**Archivo afectado:** `common/cli/commands/check.py` (firma del comando)
**Detectado al validar Q06.**

### Síntoma reproducible

```
PS> arkanum check 6 "¿Qué archivos hay en la raíz?"
Usage: arkanum check [OPTIONS] NUMBER
Try 'arkanum check --help' for help.
╭─ Error ─────────────────────────────────────────╮
│ Got unexpected extra argument (¿Qué archivos…)  │
╰─────────────────────────────────────────────────╯
```

El aprendiz que llegó hasta Q06 ya aprendió este patrón en Q03..Q05:

```
arkanum start 3 "¿Qué es un agente IA?"     ← acepta prompt
arkanum start 6 "¿Qué archivos hay en…"     ← acepta prompt
arkanum run 8 "Lee notes.txt y…"            ← acepta prompt
arkanum check 6 "¿Qué archivos…"            ← rechaza, error críptico
```

El error de Typer no explica **por qué** un prompt no aplica, ni qué hacer en su lugar.

### Causa raíz

`check.py:48-60` define el comando sin `allow_extra_args`:

```python
def check(
    number: int = typer.Argument(...),
    dry_run: bool = typer.Option(False, "--dry-run", ...),
    yes: bool = typer.Option(False, "--yes", "-y", ...),
) -> None:
```

Mientras `start` y `run` sí tienen `context_settings={"allow_extra_args": True, ...}` (visible en `common/cli/main.py:90-100`). Por diseño cada `check.py` quest-específico tiene su prompt hardcoded para reproducibilidad — no debe cambiar entre runs del mismo aprendiz.

### Tres fixes posibles

| Opción | Descripción | Pro | Contra |
|---|---|---|---|
| A | Aceptar args extras silenciosamente y mostrar nota: `"El check usa un prompt fijo. Tu argumento se ignoró."` | Mantiene compat con la intuición del aprendiz | Pierde el error explícito |
| B | Si pasa prompt, usarlo; si no, fallback al hardcoded del `check.py` | Más útil | Rompe reproducibilidad de los checks |
| **C** | Mantener rechazo pero con mensaje contextual: `"arkanum check no acepta prompt — el validador usa uno fijo. Usa: arkanum check N"` | Mantiene seguridad + claridad pedagógica | Requiere capturar el error de Typer |

**Recomendado: C.** Solo añade un mensaje útil sin cambiar comportamiento.

### Revisar por simetría

Otros comandos sin `allow_extra_args` que potencialmente confunden:
- `arkanum progress` — no toma args, OK.
- `arkanum cost` — no toma args, OK.
- `arkanum dashboard` — no toma args, OK.

Solo `check` rompe la expectativa porque se usa con N (como `start` y `run`).

---

## H-14 — El check de Q06 muestra poco "del agente" en consola

**Archivo afectado:** `quests/quest_06_tool_chest/check.py` + el patrón mental detrás
**Detectado al validar Q06.**

### Síntoma

Al correr `arkanum check 6`, el output del subprocess es:

```
✅ API key encontrada.
✅ Cliente de Gemini inicializado.
🧙 Zhyréon: Recibiendo la solicitud del aprendiz...
🧑 Prompt: ¿Qué archivos hay en la raíz?
✅ Respuesta recibida.
Prompt tokens: 351
Response tokens: 15
Calling function: get_files_info({'directory': ''})
```

El aprendiz tiene varias preguntas legítimas que la consola no responde:

1. **¿El agente "pensó" algo antes de elegir la tool?** Posiblemente sí — Gemini a veces incluye texto explicativo en `candidate.content.parts[i].text` junto con `function_calls`. El starter actual lo descarta.
2. **¿Cuál es la "respuesta final" del agente?** El código hace `if function_calls: imprime; else: agent(response.text)`. Cuando hay tools, no hay respuesta. Para el aprendiz que esperaba un párrafo de Gemini, parece que el agente "se quedó callado".
3. **¿La tool con `directory: ''` se ejecutó?** No — Q06 solo *registra* el plan. La ejecución llega en Q07. Esto **no está explicado** en consola.

### Por qué esto no es exactamente un bug

Q06 está intencionalmente acotada: enseña el registro y dispatch del plan, no la ejecución. El siguiente quest (Q07) cubre la ejecución y muestra el resultado de cada tool. El siguiente (Q08) cubre el loop completo con thought intermedio.

Pero pedagógicamente la consola de Q06 **deja al aprendiz preguntándose si el agente funcionó**. La transición Q06 → Q07 → Q08 es brusca: hay que esperar dos quests para "ver al agente vivo".

### Fixes propuestos (ordenados por valor)

1. **Imprimir `response.text` cuando coexiste con function_calls** (alta utilidad, mínimo cambio). Modificar el TODO 6.6 para que muestre tanto el texto del modelo (su razonamiento) como las tool calls:

   ```python
   if response.text:
       agent(response.text)
   for fc in response.function_calls or []:
       print(f"Calling function: {fc.name}({fc.args})")
   ```

   Esto enseña al aprendiz que **el modelo puede pensar Y planear tools en la misma respuesta**.

2. **Añadir un mensaje pedagógico al final del starter de Q06**:

   ```
   ℹ️  Q06 solo registra el plan del agente. La ejecución llega en Q07.
   ```

   Una línea que evita la sensación de "el agente no hizo nada".

3. **Mejorar el formato de `Calling function:`**: hoy es texto plano. Podría usar `console.print(...)` con estilo (icono ⚡, color glow). Hace consistente con el resto del laboratorio.

4. **Apuntar al Live Agent para experiencia rica**: cuando termine Q06, el banner final podría sugerir:

   ```
   💡 ¿Quieres ver al agente en vivo? Lanza el dashboard y prueba `arkanum run 7 "..."`
   en http://127.0.0.1:8765/live-agent.
   ```

   Esto conecta el flujo de quests con la nueva infraestructura del visualizador.

### Prioridad

Media. No bloquea pero deja una mala primera impresión. Especialmente si el aprendiz viene de Q05 (todo se ve en consola, claro y completo) y de pronto en Q06 "no se ve nada".

---

## H-15 — `arkanum check` no alimenta el Live Agent; aprendiz no entiende por qué

**Archivo afectado:** `common/cli/commands/check.py` (decisión arquitectónica)
**Detectado al cerrar Q07.**

### Síntoma reproducible

1. El aprendiz termina Q07, ejecuta `arkanum check 7`.
2. Ve la celebración "QUEST COMPLETADO ✨ Conjurador de Encarnaciones".
3. Abre `/live-agent` en el navegador esperando ver lo que su agente acaba de hacer.
4. El panel está vacío. El aprendiz pregunta: *"¿el visualizador no funciona?"*.

### Causa raíz

Por diseño solo `arkanum run` emite traces (`session_start`, `function_call`, ..., `session_end`) al endpoint `/events/trace`. `arkanum check` solo ejecuta el starter como subprocess y compara stdout. Comparativa:

| Comando | Inyecta `ARKANUM_TRACE_ID` | Parsea stdout línea por línea | Emite a `/events/trace` |
|---|---|---|---|
| `arkanum run`   | sí | sí | sí |
| `arkanum check` | no | no | no |
| `arkanum start` | no | no | no |

Esta separación es intencional (validar ≠ demostrar), pero **invisible** para el aprendiz que ya pagó tokens y espera ver "su corrida" en el dashboard.

### Tres opciones de fix

| Opción | Descripción | Pros | Contras |
|---|---|---|---|
| A | Mensaje al cerrar `check 7+`: "Para ver el agente en vivo, corre `arkanum run 7 \"...\"`" | Mínimo, no rompe nada | El aprendiz tiene que correr de nuevo + pagar tokens |
| B | Hacer que `check` también emita traces (reusar lógica de `run.py`) | El aprendiz ve resultado sin doble corrida | Aumenta complejidad de `check`, duplica trabajo en CI |
| **C** | A + cachear el trace de `check` para que `run` posterior pueda mostrarlo sin gemini extra | Best of both | Más infraestructura |

**Recomendado: A para empezar.** Una línea en `success()` de los `check.py` desde Q07 en adelante.

### Revisar por simetría

Ver también H-17 (los READMEs de Q07/Q08 no presentan `arkanum run`) y H-18 (la celebración no apunta al Live Agent). Los tres juntos forman un problema de discoverability del visualizador.

---

## H-16 — Inconsistencias menores entre READMEs y código real

**Archivos afectados:**
- `quests/quest_05_forbidden_directory/README.md`
- `quests/quest_06_tool_chest/README.md`
- `quests/quest_07_agent_incarnation/README.md`

**Detectado al revisar documentación.**

### Inconsistencias encontradas

| Quest | Línea README | Lo que dice el README | Lo que hace el código | Severidad |
|---|---|---|---|---|
| Q05 | 213-216 | `Error: Cannot list '../' as it is outside the permitted working directory` | `RuntimeError("'../' is outside the permitted working directory")` (sin "Cannot list") | Baja — formato esperado del aprendiz queda incorrecto |
| Q06 | 273 | Prompt en inglés: `what files are in the root?` | El resto del proyecto usa español: `"¿Qué archivos hay en la raíz?"` | Baja — distrae |
| Q06 | 232-235 | `Calling function:\nget_files_info({'directory': '.'})` (en dos líneas) | `print(f"Calling function: {function_call.name}({function_call.args})")` (una línea) | Baja — estética |
| Q06 | 148-160 | system_prompt con `'''` (comillas triples simples) | El archivo real usa `"""` (comillas triples dobles) | Muy baja — Python acepta ambas, pero inconsistente |
| Q07 | 244-247 | Salida con prefijo guion (`- Calling function:`) que corresponde a verbose=False | El check.py corre con `--verbose`, formato real es `Calling function: name(args)` sin guion | Media — confunde al verificar resultados |

### Fix propuesto

Pasada de coherencia README ↔ código. Lo ideal sería un test que extraiga snippets de los READMEs y los compare con lo que el starter realmente imprime al correrlo con el prompt del README. Bastante esfuerzo, pero protege contra desfase futuro.

### Prioridad

Baja-media. Ninguna inconsistencia bloquea al aprendiz, pero generan microdudas que erosionan la confianza en la documentación.

---

## H-17 — READMEs de Q07/Q08 no presentan `arkanum run` ni el Live Agent

**Archivos afectados:**
- `quests/quest_07_agent_incarnation/README.md`
- `quests/quest_08_manifesting_cycle/README.md` (por verificar)

**Detectado al revisar README de Q07.**

### Síntoma

El README de Q07 menciona como única forma de probar:

```
arkanum start 7 "lee notes.txt" --verbose
```

Y para validar:

```
arkanum check 7
```

**Ni una palabra sobre `arkanum run` ni sobre `/live-agent`.** Sin embargo, `docs/cli/commands.md:161` explícitamente recomienda:

> Cuándo usarlo: principalmente en **Q07 y Q08** (agent loop con tool calling), donde ver la secuencia function_call → function_result → siguiente iteración en vivo te da intuición de cómo razona el agente.

Esa recomendación clave está enterrada en el codex genérico, no en el README del quest donde tiene sentido.

### Causa raíz

Los READMEs se escribieron antes que existiera el visualizador. Cuando se agregó `arkanum run` + `/live-agent`, se documentó en `docs/cli/commands.md` pero no se actualizaron los READMEs de quest.

### Fix propuesto

Añadir una sección **"🪞 Ver al agente en vivo"** al README de Q07 (y Q08) entre "Tu misión" y "Resultado esperado":

```markdown
## 🪞 Ver al agente en vivo

Para ver paso a paso cómo el modelo decide tools, ejecuta:

    arkanum run 7 "lee notes.txt"

y abre [http://127.0.0.1:8765/live-agent](http://127.0.0.1:8765/live-agent).
El panel muestra cada `function_call`, su resultado, y los tokens consumidos
sin que tengas que leerlos en la terminal.
```

### Revisar por simetría

- Verificar README de Q08 (asumido similar a Q07).
- Q06 no necesita mención del Live Agent porque el agent loop aún no existe; ver decisión en H-14.
- Para Q01..Q05, mencionar el visualizador no aporta porque no hay tools que ver.

---

## H-18 — Celebración de Q07/Q08 no apunta al Live Agent

**Archivos afectados:**
- `quests/quest_07_agent_incarnation/check.py` (función `success()`)
- `quests/quest_08_manifesting_cycle/check.py` (asumido similar)

**Detectado al cerrar Q07.**

### Síntoma

Al pasar `arkanum check 7`, la última pantalla que ve el aprendiz es:

```
┌─────────────────────────────────────────────────┐
│ QUEST COMPLETADO ✨                              │
│                                                 │
│ 🧙 Zhyréon:                                     │
│ El agente ha actuado sobre el mundo por primera vez.
│                                                 │
│ 🏆 Rango desbloqueado: Conjurador de Encarnaciones
│                                                 │
│ 🎉 ✨ 🎉 ✨ 🎉                                  │
└─────────────────────────────────────────────────┘
```

Bonita, pero termina ahí. **No hay invitación a ver el agente en vivo**, justo cuando el aprendiz está más receptivo (acaba de "ganar" la quest).

### Fix propuesto

Agregar una línea al panel `success()` de `check.py`:

```
🎉 ✨ 🎉 ✨ 🎉

💡 Ahora puedes verlo en acción en vivo:
   arkanum run 7 "..."
   → http://127.0.0.1:8765/live-agent
```

Cuesta una línea, conecta el flujo de quests con el visualizador, y aprovecha el momento de mayor engagement del aprendiz.

### Revisar por simetría

- Aplicar también a `check.py` de Q08 (con el comando `arkanum run 8 "..."`).
- Considerar también extender al `arkanum next` cuando el siguiente quest tenga visualización Live Agent.

---

## H-20 — Cada step se duplica en `agent_traces`

**Archivos afectados:**
- `common/cli/commands/run.py` (función `_emit_step`)
- `common/cli/commands/check.py` (función `_record_trace_step` que añadí en este branch)

**Detectado al probar `arkanum check 7` con `live_agent=True`.**

### Síntoma reproducible

Al ejecutar `arkanum check 7` y aceptar "ver en vivo", el panel `/live-agent` muestra cada step **dos veces** con timestamps casi idénticos (≤1 segundo de diferencia):

```
🜂 session_start ... 17:45:25
🜂 session_start ... 17:45:26   ← duplicado
🜄 session_end   ... 17:45:29
🜄 session_end   ... 17:45:29   ← duplicado
```

Y `SELECT trace_id, COUNT(*) FROM agent_traces GROUP BY trace_id, step_type` confirma el conteo doble por step.

### Causa raíz

`_emit_step` (y mi `_record_trace_step` que copia el patrón) hace dos cosas para "mejor cobertura":

```python
record_step(trace_id, step_type, name, payload, quest_db_id)   # inserta fila
emit_event("trace", {...})                                      # POST a /events/trace
```

El endpoint `common/dashboard/routes/events.py:trace_event` **también** llama `record_step` con el mismo payload:

```python
@router.post("/events/trace")
def trace_event(payload):
    record_step(trace_id=payload.trace_id, ...)
```

Resultado: cada step se inserta dos veces (una directa, otra vía HTTP). El comentario original en `run.py` decía *"No es crítico"* — sí lo es.

### Fix aplicado

Eliminado el `emit_event("trace", ...)` redundante en ambos sitios. La persistencia local es la fuente de verdad y el polling del dashboard la lee directo.

### Por qué nadie lo había notado

`emit_event` falla silenciosamente en muchos escenarios (dashboard apagado, timeout HTTP, etc.). Cuando falla, no se duplica. Solo cuando el dashboard responde rápido se ve el doble registro. El usuario que probó con `arkanum run` antes de que existieran las mejoras del Live Agent probablemente no se fijó porque los steps son tantos que perderse uno o ver un doble pasa desapercibido.

### Riesgo en otras superficies

El endpoint `/events/trace` sigue siendo útil para emisores **externos al proceso** (por ejemplo, el módulo `common/tracing.py` que carga el SDK de Q08 dentro del proceso del aprendiz). Esos no tienen acceso directo a la DB y necesitan el POST. La regla queda:

- **Dentro del proceso CLI**: usa `record_step` directo.
- **Desde un subprocess o el SDK del aprendiz**: usa `tracing.emit(...)` → POST.

Nunca ambos para el mismo step.

---

## H-21 — `arkanum run` no forzaba `--verbose` y el parser quedaba ciego

**Archivo afectado:** `common/cli/commands/run.py`
**Detectado al diagnosticar por qué `/live-agent` solo mostraba session_start/session_end.**

### Síntoma reproducible

```bash
arkanum run 7 "cuantos archivos hay en la raíz"
```

→ `/live-agent` muestra solo:

```
🜂 session_start ...
🜄 session_end ... exit code 0
```

Sin function_call, sin function_result, sin tokens. El aprendiz piensa que el agente no hizo nada — pero en realidad sí corrió tools, solo que el parser no las vio.

### Causa raíz

`common/functions/call_function.py` tiene dos formatos de print según el flag verbose:

```python
if verbose:
    print(f"Calling function: {function_call.name}({function_call.args})")  # con args entre paréntesis
else:
    print(f" - Calling function: {function_call.name}")  # con guion al inicio, SIN paréntesis
```

El regex del parser de `run.py` exige paréntesis al final:

```python
_CALL_RE = re.compile(r"Calling function:\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*$")
```

Sin `--verbose`, el formato `" - Calling function: get_files_info"` **no matchea** porque no hay paréntesis. Además sin verbose el starter no imprime `Prompt tokens: N` ni `Response tokens: N` ni `-> {result}`. Resultado: el parser de stdout no encuentra nada que emitir.

El `arkanum check` con flujo "vivo" no caía en este bug porque mi código (`_run_starter_for_live_check`) sí forzaba `--verbose` en los `extra_args`. Pero `arkanum run` no lo hacía.

### Fix aplicado

```python
extra_args = list(ctx.args)
...
if "--verbose" not in extra_args and "-v" not in extra_args:
    extra_args.append("--verbose")
```

`run.py` siempre fuerza el flag. El aprendiz puede pasarlo explícitamente también, pero ya no es necesario.

### Mejora estructural opcional

El regex podría tolerar también el formato sin verbose:

```python
_CALL_RE = re.compile(r"Calling function:\s*([A-Za-z_][A-Za-z0-9_]*)(?:\s*\((.*)\))?\s*$")
```

Args quedarían vacíos en modo no-verbose, pero al menos el step se emitiría. Bajo esfuerzo, alta tolerancia. Aún así, forzar `--verbose` es más limpio para Q07/Q08 porque los tokens también necesitan ese flag.

### Revisar por simetría

Si en el futuro existe `arkanum run` para Q06 o Q05 (no es el caso hoy), confirmar que el starter del quest soporta `--verbose` antes de forzarlo — si no lo soporta, argparse va a quejarse.

---

## H-23 — Workspace de Q08 estaba triplemente roto

**Archivos afectados:**
- `quests/quest_08_manifesting_cycle/workspace/test.py` (nombre equivocado, importa funciones inexistentes)
- `quests/quest_08_manifesting_cycle/workspace/calculator.py` (clase con métodos sin self)

**Detectado al avanzar Q08.**

### Síntoma reproducible

1. El aprendiz lee el README de Q08: *"Dentro del `workspace/` encontrarás un pequeño programa: `calculator.py`, `tests.py`. Uno de los tests está fallando."*
2. Inspecciona el workspace: ve **`test.py`** (sin s) y **`calculator.py`**.
3. Intenta correr `python tests.py` desde el workspace → `tests.py no existe`. Si corre `python test.py` (asumiendo typo del README) → `ImportError: cannot import name 'add' from 'calculator'`.
4. Aún si el aprendiz arregla esos dos detalles, el check de Q08 valida que el output contenga `"All tests passed!"`, lo cual `test.py` nunca imprime.

### Tres bugs encadenados

| # | Archivo | Problema |
|---|---|---|
| 1 | `test.py` (sin s) | El README, `check.py`, el banner de la quest y la solución de referencia usan `tests.py` con s. Discrepancia. |
| 2 | `calculator.py` | Definido como `class Calculator` con métodos `def add(a, b)` (sin self). Pero `test.py` importa con `from calculator import add, subtract, ...` que solo funciona si `add` es función a nivel de módulo. |
| 3 | `test.py` | Solo tiene `assert`s. Si pasan, sale sin imprimir nada. Pero el check.py de Q08 hace `if "All tests passed!" not in output: fail()`. |

Esto significa que **Q08 era literalmente imposible de completar** de fábrica:
- El agente lee `test.py`, no `tests.py` → se confunde.
- Si arregla `calculator.py` (cambia `return a - b` por `return a + b` en `add`), los tests siguen fallando con `ImportError`.
- Aún si el agente arregla todo, el check falla porque falta `"All tests passed!"`.

### Fix aplicado

1. Reescribir `calculator.py` como funciones de módulo (preservando el bug en `add`):
   ```python
   def add(a, b):
       return a - b   # bug intencional que el agente arregla
   def subtract(a, b):
       return a - b
   def multiply(a, b):
       return a * b
   def divide(a, b):
       if b == 0:
           return "Error: División por cero"
       return a / b
   ```
2. Crear `tests.py` (con s) que importe las funciones, las pruebe e imprima `"All tests passed!"` al final.
3. Eliminar `test.py` (huérfano).

Tras los fixes, el flujo del aprendiz de Q08 funciona:
- `python tests.py` desde workspace → falla en `assert add(2, 3) == 5` (devuelve -1).
- Agente lee `tests.py`, ve el assert que falla, abre `calculator.py`, ve `return a - b` en `add`, lo cambia por `return a + b`.
- Re-ejecuta `tests.py` → imprime `"All tests passed!"`.
- `arkanum check 8` valida estado del filesystem (calculator.py con `return a + b` + tests.py pasa) → sella la quest.

### Prioridad

**Alta crítica.** Q08 era inviable. Cualquier aprendiz que llegara a Q08 se atascaría en debugging cosas que no son del quest (qué archivos existen, qué importa cada uno).

---

## H-24 — `call_function.py` hardcodea el workspace al de Q07

**Archivos afectados:**
- `common/functions/call_function.py` (línea ~87 del aprendiz, TODO 7.1 paso 7)
- `common/cli/commands/run.py`, `start.py`, `check.py` (puntos de entrada que ahora inyectan la env var)

**Detectado al ejecutar `arkanum run 8` y observar que el agente trabajaba sobre el workspace de Q07.**

### Síntoma reproducible

1. Aprendiz corre `arkanum run 8 "Los tests de calculator están fallando."`.
2. El agente lista archivos y encuentra `notes.txt`, `project.md`, `src/app.py` — esos son del **workspace de Q07**, no de Q08.
3. No encuentra `calculator.py` ni `tests.py`, así que "improvisa": los crea desde cero dentro del workspace de Q07.
4. Eventualmente "arregla" el bug y reporta éxito en el log.
5. Pero `arkanum check 8` falla porque `quests/quest_08_manifesting_cycle/workspace/calculator.py` nunca se tocó.

### Causa raíz

La instrucción TODO 7.1 paso 7 del aprendiz (en `common/functions/call_function.py`) decía:

```python
args["working_directory"] = "quests/quest_07_agent_incarnation/workspace"
```

Hardcoded al workspace de Q07 porque fue la primera quest que tuvo agente con tools. Cuando llega Q08, el agente "actúa" sobre el directorio equivocado.

El comentario del TODO incluso lo dice así: *"args["working_directory"] = 'quests/quest_07_agent_incarnation/workspace'"*. Es decir, el problema viene desde la guía oficial — no es solo que la solución estuviera mal (H-06 era distinto, ese era el slug `_embodiment` vs `_incarnation`). Aquí el slug está bien, pero ATADO a una quest concreta.

### Fix aplicado

1. `common/functions/call_function.py` ahora lee la env var con fallback:
   ```python
   args["working_directory"] = os.environ.get(
       "ARKANUM_WORKSPACE",
       "quests/quest_07_agent_incarnation/workspace",  # fallback histórico
   )
   ```
2. `common/cli/commands/run.py` inyecta `ARKANUM_WORKSPACE=f"quests/{quest.slug}/workspace"` al subprocess del starter.
3. `common/cli/commands/start.py` inyecta lo mismo. Para eso `helpers.run_module` ahora acepta `env_extra`.
4. `common/cli/commands/check.py` inyecta lo mismo en ambos caminos: el "vivo" (`_run_starter_for_live_check`) y el normal (`run_module_capturing` del check.py del quest).

Resultado: cada quest opera sobre **su** workspace sin que el aprendiz tenga que editar `call_function.py` cada vez.

### Mejora pedagógica para llevar a master

El TODO 7.1 paso 7 del aprendiz podría reescribirse para enseñar el patrón correcto desde el principio:

```python
# TODO 7.1 (call_function.py, paso 7):
# Inyecta el working_directory desde una env var que el CLI te pasa.
# Esto permite que cada quest opere sobre su propio workspace.
#
#   args["working_directory"] = os.environ.get(
#       "ARKANUM_WORKSPACE",
#       "quests/quest_07_agent_incarnation/workspace",  # fallback si corres a mano
#   )
```

Así el aprendiz aprende desde Q07 a separar configuración de código.

### Side-effect del bug

Durante esta sesión de pruebas, el agente creó archivos contaminantes en `quests/quest_07_agent_incarnation/workspace/src/` (`calculator.py`, `test_calculator.py`, `__pycache__`). Limpiados manualmente. En máquinas de aprendices futuros este efecto secundario también ocurriría — vale la pena un script `arkanum doctor --clean-workspaces` o similar para limpiarlos.

### Prioridad

**Alta crítica.** Sin este fix, Q08 (y cualquier futura quest que use tools) es imposible de completar.

---

## Plantilla para hallazgos futuros

Cuando aparezca uno nuevo durante el avance del plan de pruebas, añadirlo aquí con este esquema:

```
## H-XX — Título corto

**Archivo afectado:** ...
**Detectado al resolver:** Q0X

### Síntoma reproducible
(pasos numerados desde la perspectiva del aprendiz)

### Causa raíz
(qué línea / qué patrón rompe)

### Fix propuesto
(qué cambia, ejemplo de código si aplica)

### Revisar por simetría
(otros sitios con el mismo patrón)
```

---

## Workflow propuesto para llevar a master

Una vez la suite de pruebas Q07/Q08 esté validada:

1. Desde `master`, crear `fix/qchecks-and-starters-2026-05-29` (o nombre similar).
2. Aplicar cada hallazgo como un commit independiente:
   - `fix(precheck-q01): usa AST en vez de string matching para el placeholder de prompt`
   - `fix(starter-q02..q08): estandariza imports incluyendo show_prompt`
   - …
3. (Recomendado) Aplicar la mitigación estructural de H-03: estandarizar el bloque de imports `from common.utils.ui import (...)` en TODOS los starters Q02..Q08 para incluir el superset, en lugar de parchear quest por quest.
4. Auditoría rápida de pre-checks Q02..Q06 buscando `regex_in_source` que puedan dar falsos positivos (mismo riesgo que H-01 en otra forma).
5. PR sobre `master` con esta bitácora como descripción.
